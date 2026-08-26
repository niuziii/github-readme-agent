# GitHub 项目解读 Agent

一个运行在 Windows 桌面的轻量级 AI Agent。粘贴 GitHub 仓库链接后，自动获取 README，并调用用户自己的大模型 API，生成结构化中文解读、约 1000 字内容总结和完整中文翻译。

## 功能特性

- GitHub 仓库链接自动识别，支持 HTTPS 与 SSH 形式
- 通过 GitHub API 获取 README，不依赖网页抓取
- 支持任意 OpenAI 兼容的 LLM API（DeepSeek、OpenAI、通义、智谱等）
- 输出项目名称、项目定位、解决的问题、技术栈、核心功能、工作流程、通俗理解
- 先输出约 1000 字 README 内容总结，再输出完整 README 中文翻译
- 长 README 自动分段理解，避免超出模型上下文限制
- 流式输出，可随时停止，停止后保留已生成内容
- 流式输出时不会自动滚动，阅读位置完全由用户控制

## 技术栈

- Python
- PySide6
- GitHub API
- OpenAI 兼容 LLM API
- Pydantic
- python-dotenv
- PyInstaller

## 快速开始

### 直接运行 exe（推荐）

仓库已附带 Windows 可执行文件：

```text
dist\GitHubReadmeAgent.exe
```

下载或 clone 仓库后直接双击即可运行，不需要安装 Python 和任何依赖。

### 环境要求

- Windows 10 / 11
- Python 3.10+

### 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 配置

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，填写自己的大模型 API 配置：

```dotenv
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.3
GITHUB_TOKEN=
MAX_README_CHARS=24000
```

也可以直接双击 `run.bat`，首次运行会自动创建虚拟环境并安装依赖。

### 运行

```powershell
python main.py
```

打开后在设置中填写 API 配置，粘贴 GitHub 仓库链接，点击“开始分析”。

## 打包为 Windows exe

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name GitHubReadmeAgent main.py
```

或直接双击 `build.bat`，生成文件位于 `dist\GitHubReadmeAgent.exe`。

## 项目结构

```text
.
├── main.py              # 程序入口
├── ui.py                # PySide6 桌面界面
├── agent.py             # GitHub README 获取与 LLM 解读 Agent
├── config.py            # .env 配置管理
├── requirements.txt     # Python 依赖
├── run.bat              # 一键运行脚本
├── build.bat            # 一键打包脚本
└── .env.example         # 环境变量模板
```

## 许可证

[MIT](LICENSE)
