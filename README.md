# Entropy_Anchor - Vibe-driven Agent Builder - The Vibe Architect 

> "意图架构师: 不要仅仅写代码，要赋予它秩序。开始编译现实。"

> "熵之锚：负熵之锚, 工作于混沌边缘。

> 混乱 > 坍缩 > 秩序, Idea > Action Node。"

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 核心哲学

通过最精简的自然语言意图（Vibe），自动编译并生成具备特定 Skill 的子智能体。

Entropy_Anchor 是一个基于 LangChain 的智能体构建框架，它能够理解模糊的自然语言意图，将其"塌缩"为具体的任务规划、工具选择和执行路径，并自动生成工作量证明。

## 架构层次

1. **The Philosopher Layer**: 处理输入的自然语言 Vibe
2. **The Probability Layer**: 评估任务可行性并生成多个执行路径
3. **The Action Node**: 最终生成的 Agent 实例，自带工作量证明（PoW）机制

## 项目结构

```
entropy_anchor/
├── core/                  # 核心架构
│   ├── __init__.py
│   ├── agent.py          # Agent 基础类和能量系统
│   ├── philosopher.py    # Philosopher Layer - Vibe 解析
│   ├── probability.py    # Probability Layer - 路径生成
│   ├── action.py         # Action Node - 任务执行
│   └── llm_factory.py    # LLM 工厂类（支持 OpenAI/Gemini）
├── api/                  # FastAPI 后端
│   ├── __init__.py
│   └── routes.py         # RESTful API 接口
├── ui/                   # Streamlit UI
│   └── app.py            # 可视化界面
├── examples/             # 示例和测试
│   └── mva_example.py    # 最小可行性示例
├── workspace/            # 工作目录（生成的文件）
├── requirements.txt      # Python 依赖
├── pyproject.toml        # 项目配置（uv）
├── env.example           # 环境变量示例
├── run_api.sh           # API 启动脚本
├── run_ui.sh            # UI 启动脚本
├── README.md            # 项目说明
├── QUICKSTART.md        # 快速开始指南
└── ARCHITECTURE.md      # 架构文档
```

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/jangels/Entropy_Anchor.git
cd Entropy_Anchor

# 安装依赖（推荐使用 uv）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 配置

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，填入你的 API Key
# 至少需要设置 OPENAI_API_KEY 或 GEMINI_API_KEY 中的一个
```

### 运行

```bash
# 方式 1: 运行示例
uv run python examples/mva_example.py

# 方式 2: 命令行接口
uv run python main.py "写一个计算斐波那契数列的函数"

# 方式 3: 启动 Web UI
./run_ui.sh  # 或 uv run streamlit run ui/app.py
```

详细说明请查看 [QUICKSTART.md](QUICKSTART.md)

## 技术栈

- Backend: FastAPI + Pydantic
- Agent Framework: LangChain + LangGraph
- LLM: 支持 OpenAI (GPT-4) 和 Google Gemini (2.0 Flash)
- UI: Streamlit

## 支持的模型

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Gemini**: Gemini 2.5 Flash, Gemini 2.0 Flash, Gemini 1.5 Flash, Gemini 1.5 Pro

### 模型配置

默认模型可通过环境变量配置（当你不显式传 `--model` / `model_name` 时生效）：

**优先级**：
1. `GEMINI_MODEL_NAME` / `OPENAI_MODEL_NAME`（按提供商）
2. `LLM_MODEL_NAME`（全局默认）
3. 内置默认（OpenAI: `gpt-4`，Gemini: `gemini-1.5-flash`）

## 特性

- 🎯 **三层架构**: Philosopher → Probability → Action
- ⚡ **能量系统**: 防止无限执行，自动管理资源
- 📜 **工作量证明**: 自动生成可验证的执行报告
- 🔌 **多模型支持**: OpenAI 和 Google Gemini
- 🚀 **即插即用**: 简单的 API 和 CLI 接口
- 🎨 **可视化界面**: Streamlit UI 实时观测

## 文档

- [快速开始指南](QUICKSTART.md) - 详细的安装和使用说明
- [架构文档](ARCHITECTURE.md) - 深入了解系统设计

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
