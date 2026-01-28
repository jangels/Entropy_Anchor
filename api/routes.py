"""
FastAPI Routes - 提供 Agent 构建和管理的 API 接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn

from core import (
    EntropyAgent,
    PhilosopherLayer,
    ProbabilityLayer,
    ActionNode,
    ModelProvider,
)


app = FastAPI(
    title="Entropy_Anchor API",
    description="The Vibe Coder - Agent Builder API",
    version="0.1.0",
)


class VibeRequest(BaseModel):
    """Vibe 请求模型"""
    vibe: str = Field(..., description="自然语言意图")
    energy_budget: float = Field(default=100.0, ge=0.0, le=100.0, description="能量预算")
    llm_provider: Optional[str] = Field(default=None, description="LLM 提供商 (openai/gemini)，默认自动检测")
    model_name: Optional[str] = Field(default=None, description="模型名称，默认使用提供商默认模型")


class AgentResponse(BaseModel):
    """Agent 响应模型"""
    agent_id: str
    state: str
    energy: float
    task_plan: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    entropy_report: Optional[Dict[str, Any]] = None


# 全局实例（实际应用中应使用依赖注入）
philosopher = None
probability_layer = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化（使用默认配置）"""
    global philosopher, probability_layer
    try:
        # 使用默认配置初始化（会自动检测可用的 API Key）
        philosopher = PhilosopherLayer()
        probability_layer = ProbabilityLayer()
    except Exception as e:
        print(f"Warning: Failed to initialize layers: {e}")
        print("Note: Layers will be created per-request with specified provider/model")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Entropy_Anchor API",
        "status": "running",
        "version": "0.1.0",
    }


@app.post("/api/v1/agent/create", response_model=AgentResponse)
async def create_agent(request: VibeRequest):
    """
    创建并执行 Agent
    
    流程：
    1. Philosopher Layer 解析 Vibe
    2. Probability Layer 生成执行路径
    3. Action Node 执行任务
    """
    try:
        # 解析模型提供商
        provider = None
        if request.llm_provider:
            if request.llm_provider.lower() not in ["openai", "gemini"]:
                raise HTTPException(
                    status_code=400,
                    detail="llm_provider must be 'openai' or 'gemini'"
                )
            provider = request.llm_provider.lower()  # type: ignore
        
        # 创建 Agent
        agent = EntropyAgent(vibe=request.vibe, energy=request.energy_budget)
        
        # Philosopher Layer: 解析 Vibe（使用请求中的模型参数）
        philosopher_instance = PhilosopherLayer(
            provider=provider,
            model_name=request.model_name,
        )
        parsed_vibe = philosopher_instance.parse_vibe(request.vibe)
        task_plan = philosopher_instance.extract_task_plan(parsed_vibe)
        agent.task_plan = task_plan
        agent.add_proof_of_work(
            action="vibe_parsing",
            result="Vibe parsed successfully",
            energy_cost=5.0,
        )
        
        # Probability Layer: 生成执行路径（使用请求中的模型参数）
        probability_instance = ProbabilityLayer(
            provider=provider,
            model_name=request.model_name,
        )
        paths = probability_instance.generate_paths(task_plan)
        optimal_path = probability_instance.select_optimal_path(
            paths,
            energy_budget=agent.energy,
        )
        
        if not optimal_path:
            raise HTTPException(
                status_code=400,
                detail="No feasible execution path found within energy budget"
            )
        
        agent.selected_tools = optimal_path.tools_required
        agent.add_proof_of_work(
            action="path_selection",
            result=f"Selected path: {optimal_path.path_id}",
            energy_cost=3.0,
        )
        
        # Action Node: 执行任务（使用请求中的模型参数）
        action_node = ActionNode(
            agent,
            optimal_path,
            provider=provider,
            model_name=request.model_name,
        )
        execution_result = action_node.execute()
        
        # 生成熵报告
        entropy_report = agent.get_entropy_report()
        
        return AgentResponse(
            agent_id=agent.id,
            state=agent.state.value,
            energy=agent.energy,
            task_plan=task_plan,
            execution_result=execution_result,
            entropy_report=entropy_report,
        )
        
    except ValueError as e:
        # 处理配置错误（如缺少 API Key）
        error_msg = str(e)
        if "API_KEY" in error_msg or "not found in environment" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"配置错误: {error_msg}. 请检查 .env 文件中的 API Key 配置。"
            )
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        error_str = str(e)
        
        # 检测 API Key 相关错误
        if "401" in error_str or "invalid_api_key" in error_str.lower() or "incorrect api key" in error_str.lower():
            raise HTTPException(
                status_code=401,
                detail="API Key 无效或已过期。请检查：\n"
                       "1. .env 文件中的 OPENAI_API_KEY 或 GEMINI_API_KEY 是否正确\n"
                       "2. API Key 是否已过期或被撤销\n"
                       "3. 是否在正确的平台（OpenAI 或 Google AI Studio）获取了 API Key\n"
                       f"错误详情: {error_str[:200]}..."  # 只显示前200字符，避免暴露完整信息
            )
        
        # 检测网络或连接错误
        if "connection" in error_str.lower() or "timeout" in error_str.lower():
            raise HTTPException(
                status_code=503,
                detail=f"服务连接错误: {error_str[:200]}..."
            )
        
        # 其他错误
        raise HTTPException(
            status_code=500,
            detail=f"内部错误: {error_str[:500]}..."  # 限制错误信息长度
        )


@app.get("/api/v1/agent/{agent_id}/report")
async def get_agent_report(agent_id: str):
    """
    获取 Agent 的熵报告
    
    注意：这是一个简化版本，实际应用中应该从数据库或存储中获取
    """
    return {
        "message": "Agent report retrieval",
        "agent_id": agent_id,
        "note": "In a full implementation, this would fetch from persistent storage",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
