# Entropy_Anchor 架构文档

## 核心哲学

> "不要仅仅写代码，要赋予它秩序。开始编译现实。"

Entropy_Anchor 通过最精简的自然语言意图（Vibe），自动编译并生成具备特定 Skill 的子智能体。

## 三层架构

### 1. The Philosopher Layer (哲学家层)

**位置**: `core/philosopher.py`

**职责**:
- 处理输入的自然语言 Vibe
- 将模糊意图"塌缩"为清晰的结构化意图
- 提取核心意图、领域、复杂度、所需技能和约束条件

**核心类**:
- `PhilosopherLayer`: 主要处理类
- `ParsedVibe`: 解析后的结构化意图模型

**工作流程**:
```
自然语言 Vibe 
  → LLM 解析 
  → ParsedVibe 对象 
  → Task Plan (任务规划)
```

### 2. The Probability Layer (概率层)

**位置**: `core/probability.py`

**职责**:
- 评估任务可行性
- 生成多个执行路径
- 选择最优执行路径（基于可行性分数和能量效率）

**核心类**:
- `ProbabilityLayer`: 路径生成和选择
- `ExecutionPath`: 执行路径模型

**工作流程**:
```
Task Plan 
  → 生成多个 ExecutionPath 
  → 评估可行性 
  → 选择最优路径
```

### 3. The Action Node (行动节点)

**位置**: `core/action.py`

**职责**:
- 执行具体的任务
- 生成代码、运行测试、管理文件
- 实现工作量证明（PoW）机制

**核心类**:
- `ActionNode`: 任务执行器
- `ProofOfWork`: 工作量证明记录器

**工作流程**:
```
ExecutionPath 
  → 选择工具 
  → 执行任务 
  → 生成工作量证明
```

## 核心组件

### EntropyAgent

**位置**: `core/agent.py`

**特性**:
- **能量衰减机制**: 每次行动消耗能量，能量过低时进入衰减态
- **状态机**: QUANTUM → COLLAPSING → ANCHORED → DECAYED
- **工作量证明**: 自动记录所有行动轨迹

**状态转换**:
```
QUANTUM (量子态)
  ↓
COLLAPSING (塌缩中)
  ↓
ANCHORED (已锚定) / DECAYED (已衰减)
```

### 能量系统

- **初始能量**: 100.0（可配置）
- **能量消耗**: 每个行动都有对应的能量成本
- **衰减阈值**: 能量 < 10.0 时自动进入衰减态
- **能量预算**: 执行路径必须在能量预算内

### 工作量证明 (PoW)

每个 Agent 都会生成：
- `proof_of_work.log`: 详细的行动日志
- `entropy_report.json`: 完整的熵报告
- 生成的文件: 所有代码和输出文件

## 数据流

```
用户输入 Vibe
  ↓
[Philosopher Layer] 解析意图
  ↓
生成 Task Plan
  ↓
[Probability Layer] 生成执行路径
  ↓
选择最优路径
  ↓
[Action Node] 执行任务
  ↓
生成代码 + 运行测试
  ↓
生成工作量证明报告
```

## 工具系统

当前支持的工具：
- `code_generator`: 代码生成器
- `test_runner`: 测试运行器
- `file_manager`: 文件管理器
- `git_manager`: Git 管理器（预留）
- `log_analyzer`: 日志分析器（预留）

## API 接口

**位置**: `api/routes.py`

**端点**:
- `GET /`: 健康检查
- `POST /api/v1/agent/create`: 创建并执行 Agent
- `GET /api/v1/agent/{agent_id}/report`: 获取 Agent 报告

## UI 界面

**位置**: `ui/app.py`

**功能**:
- 输入 Vibe
- 实时观测 Agent 塌缩过程
- 查看任务规划、执行结果和熵报告
- 下载工作量证明报告

## 扩展点

### 添加新工具

在 `core/action.py` 的 `ActionNode` 类中添加新方法：

```python
def _your_new_tool(self) -> Dict[str, Any]:
    """你的新工具"""
    # 实现逻辑
    self.agent.add_proof_of_work(
        action="your_tool",
        result="...",
        energy_cost=5.0,
    )
    return {...}
```

然后在 `_execute_path` 方法中添加调用。

### 自定义路径生成

修改 `core/probability.py` 的 `_parse_paths_from_response` 方法，实现更智能的路径解析。

### 自定义意图解析

修改 `core/philosopher.py` 的 prompt 模板，调整解析逻辑。

## 技术栈

- **Backend**: FastAPI + Pydantic
- **Agent Framework**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4 / Google Gemini (可配置)
- **UI**: Streamlit
- **日志**: JSON 格式的工作量证明
- **包管理**: uv (推荐) 或 pip

## 设计原则

1. **能量守恒**: 每个行动都有能量成本，防止无限执行
2. **状态透明**: 所有状态转换都有记录
3. **可验证性**: 通过工作量证明确保可追溯
4. **可扩展性**: 模块化设计，易于添加新功能
