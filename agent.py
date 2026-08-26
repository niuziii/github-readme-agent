"""GitHub README 获取与 LLM 结构化解读 Agent。"""

from __future__ import annotations

import json
import re
import threading
from typing import Iterator, List

import requests
from pydantic import BaseModel
from PySide6.QtCore import QThread, Signal

from config import AppConfig


class AgentError(Exception):
    """Agent 业务错误基类。"""


class GitHubReadmeError(AgentError):
    """GitHub 相关错误。"""


class LlmError(AgentError):
    """LLM API 相关错误。"""


class CancelledError(AgentError):
    """用户主动取消。"""


class RepositoryRef(BaseModel):
    owner: str
    repo: str
    url: str


_GITHUB_RE = re.compile(r"github\.com[:/]([^/?#\s]+)/([^/?#\s]+)", re.IGNORECASE)


def _strip_git_suffix(value: str) -> str:
    return value[:-4] if value.endswith(".git") else value


def parse_github_url(raw: str) -> RepositoryRef:
    text = raw.strip()
    match = _GITHUB_RE.search(text)
    if not match:
        raise GitHubReadmeError("链接格式不正确，请输入类似 https://github.com/owner/repo 的仓库地址")
    owner = _strip_git_suffix(match.group(1))
    repo = _strip_git_suffix(match.group(2))
    if not owner or not repo:
        raise GitHubReadmeError("链接格式不正确，请输入类似 https://github.com/owner/repo 的仓库地址")
    return RepositoryRef(owner=owner, repo=repo, url=f"https://github.com/{owner}/{repo}")


def fetch_readme(ref: RepositoryRef, token: str = "") -> str:
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "GitHub-README-Intelligence-Agent",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}/readme"
    try:
        response = requests.get(url, headers=headers, timeout=(5, 25))
    except requests.RequestException as exc:
        raise GitHubReadmeError(f"无法连接 GitHub API：{exc}") from exc

    if response.status_code == 404:
        raise GitHubReadmeError(
            f"未找到 {ref.owner}/{ref.repo} 的 README，仓库可能不存在或为私有仓库"
        )
    if response.status_code == 403:
        raise GitHubReadmeError(
            "GitHub API 访问被限制（可能触发限流），可稍后重试，或在设置中填写 GitHub Token"
        )
    if response.status_code != 200:
        raise GitHubReadmeError(f"获取 README 失败（HTTP {response.status_code}）")
    return response.text


def split_readme(readme: str, max_chars: int) -> List[str]:
    if len(readme) <= max_chars:
        return [readme]
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    for line in readme.splitlines(keepends=True):
        if current and size + len(line) > max_chars:
            chunks.append("".join(current))
            current = []
            size = 0
        current.append(line)
        size += len(line)
    if current:
        chunks.append("".join(current))
    return chunks or [readme]


def _extract_error(response: requests.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            message = data.get("message")
            if message:
                return str(message)
            error = data.get("error")
            if isinstance(error, dict) and error.get("message"):
                return str(error["message"])
            if isinstance(error, str):
                return error
    except (ValueError, TypeError):
        pass
    text = response.text.strip()[:300]
    return text or response.reason or "未知错误"


SYSTEM_PROMPT = (
    "你是一名资深开源项目技术分析师，擅长用中文向开发者解释 GitHub 项目。"
    "你的任务不是逐句机器翻译，而是先理解 README 的整体语义，"
    "再生成准确、通俗、结构完整的中文项目解读。"
    "请保留 Markdown 格式、代码块、命令、技术名称、URL 和配置示例，避免破坏原文结构。"
)

SECTION_HEADINGS = "\n".join(
    [
        "## 📦 项目名称",
        "## 🎯 项目是做什么的？",
        "## 🧩 解决了什么问题？",
        "## 🛠️ 技术栈",
        "## ⚙️ 核心功能",
        "## 🔄 工作流程",
        "## 🧠 通俗理解",
        "## 📝 README 内容总结",
        "## 📖 README 中文翻译",
    ]
)


def _build_analysis_prompt(readme: str, source_label: str = "README") -> str:
    return f"""请分析下面的 GitHub 项目{source_label}，生成一份完整的结构化中文解读。

输出要求：
1. 必须按以下章节标题依次输出，标题使用 Markdown 二级标题：
{SECTION_HEADINGS}
2. 项目名称、项目是做什么的、解决了什么问题、技术栈、核心功能、工作流程要精炼准确。
3. 通俗理解要像对朋友解释一样，用一句话说清这个项目是什么。
4. README 内容总结需要用约 1000 个中文字符，全面概括{source_label}的核心内容、关键功能和技术要点。
5. README 中文翻译需要完整覆盖{source_label}内容，保留 Markdown、代码块、命令、技术名称、URL 和配置示例。
6. 不要输出本章节要求以外的内容。

{source_label}内容如下：

{readme}"""


def _build_chunk_prompt(chunk: str, index: int, total: int) -> str:
    return f"""下面是某个 GitHub 项目 README 的第 {index}/{total} 部分。
请提炼这部分的核心信息，生成精炼的中文摘要，保留关键技术名词、命令、URL 和重要功能点，不要遗漏关键内容。
直接输出摘要：

{chunk}"""


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def _endpoint(self) -> str:
        base = self.config.base_url
        if not base:
            raise LlmError("请先在设置中填写 LLM API 地址")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    def _payload(self, messages: list[dict[str, str]]) -> dict:
        return {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "stream": True,
        }

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        api_key = self.config.api_key
        if not api_key:
            raise LlmError("请先在设置中填写 LLM API Key")
        if not self.config.model:
            raise LlmError("请先在设置中填写模型名称")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        try:
            response = requests.post(
                self._endpoint(),
                headers=headers,
                json=self._payload(messages),
                stream=True,
                timeout=(10, 300),
            )
        except requests.RequestException as exc:
            raise LlmError(f"无法连接 LLM API：{exc}") from exc

        if response.status_code != 200:
            detail = _extract_error(response)
            raise LlmError(f"LLM API 返回错误（HTTP {response.status_code}）：{detail}")

        content_type = response.headers.get("Content-Type", "")
        try:
            if "application/json" in content_type and "text/event-stream" not in content_type:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    yield content
                return

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                stripped = line.strip()
                if not stripped.startswith("data:"):
                    continue
                payload = stripped[len("data:"):].strip()
                if not payload or payload == "[DONE]":
                    continue
                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content
        except requests.RequestException as exc:
            raise LlmError(f"读取模型响应中断：{exc}") from exc


class AnalysisWorker(QThread):
    status_changed = Signal(str)
    stream_delta = Signal(str)
    repo_ready = Signal(str)
    analysis_finished = Signal(str)
    failed = Signal(str)

    def __init__(self, config: AppConfig, url: str) -> None:
        super().__init__()
        self._config = config
        self._url = url
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        self._cancel_event.set()

    def _check_cancelled(self) -> None:
        if self._cancel_event.is_set():
            raise CancelledError()

    def _complete(self, client: LLMClient, messages: list[dict[str, str]]) -> str:
        parts: list[str] = []
        for delta in client.stream(messages):
            self._check_cancelled()
            parts.append(delta)
        return "".join(parts)

    def _stream_analysis(self, client: LLMClient, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        parts: list[str] = []
        for delta in client.stream(messages):
            self._check_cancelled()
            parts.append(delta)
            self.stream_delta.emit(delta)
        return "".join(parts)

    def run(self) -> None:
        try:
            ref = parse_github_url(self._url)
            self.repo_ready.emit(f"{ref.owner}/{ref.repo}")
            self.status_changed.emit("正在从 GitHub 获取 README...")

            readme = fetch_readme(ref, self._config.github_token)
            self._check_cancelled()
            self.status_changed.emit(
                f"README 获取成功（{len(readme):,} 字符），正在调用大模型..."
            )

            chunks = split_readme(readme, self._config.max_readme_chars)
            client = LLMClient(self._config)
            if len(chunks) == 1:
                result = self._stream_analysis(client, _build_analysis_prompt(readme))
            else:
                self.status_changed.emit(
                    f"README 较长，已拆分为 {len(chunks)} 段进行理解..."
                )
                summaries: list[str] = []
                for index, chunk in enumerate(chunks, start=1):
                    self._check_cancelled()
                    self.status_changed.emit(f"正在分段理解 {index}/{len(chunks)}...")
                    summaries.append(
                        self._complete(
                            client,
                            [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": _build_chunk_prompt(chunk, index, len(chunks))},
                            ],
                        )
                    )
                combined = "\n\n".join(summaries)
                self.status_changed.emit("分段理解完成，正在生成最终解读...")
                result = self._stream_analysis(
                    client, _build_analysis_prompt(combined, "分段摘要")
                )

            self._check_cancelled()
            self.analysis_finished.emit(result)
        except CancelledError:
            return
        except AgentError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"发生未知错误：{exc}")
