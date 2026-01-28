# Entropy_Anchor 快速开始指南

## 环境准备

1. **安装依赖**

```bash
# 推荐使用 uv（更快）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
# 方式 1: 直接创建 .env 文件（推荐）
# 使用 OpenAI
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# 或使用 Gemini
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# 方式 2: 复制示例文件
cp env.example .env

# 然后编辑 .env 文件，填入你的实际 API Key
# 至少需要设置 OPENAI_API_KEY 或 GEMINI_API_KEY 中的一个
```

**支持的模型提供商**:

- **OpenAI**: 需要设置 `OPENAI_API_KEY`，默认使用 `gpt-4`
- **Gemini**: 需要设置 `GEMINI_API_KEY`，默认使用 `gemini-1.5-flash`

**默认模型读取规则（当你不传 `--model` / `model_name` 时）**：

1. 优先读取 `GEMINI_MODEL_NAME` / `OPENAI_MODEL_NAME`（按提供商）
2. 其次读取 `LLM_MODEL_NAME`（全局默认）
3. 最后回退到内置默认（OpenAI: `gpt-4`，Gemini: `gemini-1.5-flash`）

## 使用方式

### 方式 1: 命令行接口 (CLI)

```bash
# 使用默认模型（自动检测）
uv run python main.py "写一个计算斐波那契数列的函数，并测试前10个数"

# 指定使用 Gemini
uv run python main.py "写一个计算斐波那契数列的函数" --provider gemini

# 指定使用 OpenAI
uv run python main.py "写一个计算斐波那契数列的函数" --provider openai

# 指定模型和能量预算
uv run python main.py "创建一个简单的 HTTP 服务器" --provider gemini --model gemini-2.5-flash --energy 80
```

### 方式 2: MVA 示例

运行最小可行性示例：

```bash
uv run python examples/mva_example.py
```

### 方式 3: FastAPI 后端 + Streamlit UI

**启动 API 服务**（终端 1）：

```bash
# 使用启动脚本（推荐）
./run_api.sh

# 或手动启动
uv run uvicorn api.routes:app --reload --host 0.0.0.0 --port 8003
```

**启动 Streamlit UI**（终端 2）：

```bash
# 使用启动脚本（推荐）
./run_ui.sh

# 或手动启动
uv run streamlit run ui/app.py
```

然后在浏览器中打开显示的 URL（通常是 `http://localhost:8501`）

## 工作流程

1. **输入 Vibe**: 用自然语言描述你的意图
2. **Philosopher Layer**: 系统解析你的意图，提取核心任务
3. **Probability Layer**: 生成多个执行路径，选择最优路径
4. **Action Node**: 执行任务，生成代码和测试
5. **工作量证明**: 自动生成熵报告，记录所有执行轨迹

## 输出文件

所有生成的文件和报告都保存在 `./workspace/{agent_id}/` 目录下：

- `generated_{agent_id}.py`: 生成的代码文件
- `proof_of_work.log`: 工作量证明日志
- `entropy_report.json`: 完整的熵报告

## 故障排查

### 问题: API Key 错误 (401)

**错误信息**: `API Key 无效或已过期` 或 `invalid_api_key`

**解决步骤**:
1. 检查 `.env` 文件是否存在且包含有效的 API Key
2. 验证 API Key 格式是否正确（OpenAI: `sk-` 开头）
3. 确认 API Key 未过期或被撤销
4. 可以尝试切换到 Gemini：设置 `GEMINI_API_KEY` 并在请求中指定 `"llm_provider": "gemini"`

**详细排查**: 查看项目 Issues 或提交新的 Issue

### 问题: "OPENAI_API_KEY not found"

**解决**: 确保已创建 `.env` 文件并设置了 `OPENAI_API_KEY` 或 `GEMINI_API_KEY`

### 问题: API 连接失败

**解决**: 确保 API 服务正在运行（检查端口 8003，默认配置）

### 问题: 导入错误

**解决**: 确保已安装所有依赖 `uv sync` 或 `pip install -r requirements.txt`

## 下一步

- 查看 `examples/mva_example.py` 了解如何自定义 Agent
- 阅读 `core/` 目录下的源代码了解架构细节
- 修改 `core/action.py` 添加自定义工具
