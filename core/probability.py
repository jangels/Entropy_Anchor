"""
ProbabilityLayer - 概率层
评估任务可行性并生成多个执行路径
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from .llm_factory import LLMFactory, ModelProvider
import os
from dotenv import load_dotenv

load_dotenv()


class ExecutionPath(BaseModel):
    """执行路径"""
    path_id: str
    description: str
    feasibility_score: float  # 0-1
    estimated_energy_cost: float
    tools_required: List[str]
    risk_factors: List[str]


class ProbabilityLayer:
    """
    概率层 - 评估任务可行性并生成多个执行路径
    """
    
    def __init__(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        初始化概率层
        
        Args:
            provider: LLM 提供商 ("openai" 或 "gemini")，如果为 None 则自动检测
            model_name: 使用的 LLM 模型名称，如果为 None 则使用默认值
            temperature: 温度参数（较高值保证更多样化的路径）
        """
        self.llm = LLMFactory.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
        )
        
        self.path_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个概率评估专家。你的任务是为给定的任务生成多个可能的执行路径，并评估每个路径的可行性。

对于每个路径，你需要：
1. 给出清晰的描述
2. 评估可行性分数（0-1，1最可行）
3. 估算能量消耗（1-100）
4. 列出所需工具
5. 识别风险因素

请生成3-5个不同的执行路径。"""),
            ("human", "任务信息：\n{task_info}\n\n请生成执行路径："),
        ])
    
    def generate_paths(
        self,
        task_plan: Dict[str, Any],
        available_tools: Optional[List[str]] = None,
    ) -> List[ExecutionPath]:
        """
        生成多个执行路径
        
        Args:
            task_plan: 任务规划信息
            available_tools: 可用工具列表（如果为None，则假设所有工具可用）
            
        Returns:
            执行路径列表
        """
        if available_tools is None:
            available_tools = [
                "code_generator",  # 代码生成器
                "test_runner",     # 测试运行器
                "file_manager",    # 文件管理器
                "git_manager",     # Git 管理器
                "log_analyzer",    # 日志分析器
            ]
        
        task_info = f"""
意图: {task_plan.get('intent', 'N/A')}
领域: {task_plan.get('domain', 'N/A')}
复杂度: {task_plan.get('complexity', 'N/A')}
步骤: {', '.join(task_plan.get('steps', []))}
可用工具: {', '.join(available_tools)}
"""
        
        prompt = self.path_generation_prompt.format_messages(task_info=task_info)
        response = self.llm.invoke(prompt)
        
        # 解析 LLM 响应并生成路径
        paths = self._parse_paths_from_response(response.content, available_tools)
        
        return paths
    
    def _parse_paths_from_response(
        self,
        response: str,
        available_tools: List[str],
    ) -> List[ExecutionPath]:
        """
        从 LLM 响应中解析执行路径
        
        Args:
            response: LLM 响应文本
            available_tools: 可用工具列表
            
        Returns:
            执行路径列表
        """
        # 简化实现：使用 LLM 直接生成结构化输出
        # 实际应用中可以使用更复杂的解析逻辑
        
        # 这里我们使用一个简化的启发式方法
        # 在实际应用中，可以使用 JSON 模式或更复杂的解析
        
        paths = []
        
        # 生成几个基础路径作为示例
        # 实际应该从 LLM 响应中解析
        
        # 路径1：直接实现
        paths.append(ExecutionPath(
            path_id="path_1",
            description="直接实现核心功能，快速验证",
            feasibility_score=0.8,
            estimated_energy_cost=30.0,
            tools_required=["code_generator", "test_runner"],
            risk_factors=["可能缺少边界情况处理"],
        ))
        
        # 路径2：渐进式实现
        paths.append(ExecutionPath(
            path_id="path_2",
            description="分阶段实现，先搭建框架再填充细节",
            feasibility_score=0.9,
            estimated_energy_cost=50.0,
            tools_required=["code_generator", "file_manager", "test_runner"],
            risk_factors=["可能过度设计"],
        ))
        
        # 路径3：测试驱动
        paths.append(ExecutionPath(
            path_id="path_3",
            description="先写测试，再实现功能",
            feasibility_score=0.7,
            estimated_energy_cost=40.0,
            tools_required=["test_runner", "code_generator"],
            risk_factors=["需要更清晰的需求"],
        ))
        
        return paths
    
    def select_optimal_path(
        self,
        paths: List[ExecutionPath],
        energy_budget: float = 100.0,
    ) -> Optional[ExecutionPath]:
        """
        选择最优执行路径
        
        Args:
            paths: 执行路径列表
            energy_budget: 能量预算
            
        Returns:
            最优路径，如果没有可行路径则返回 None
        """
        # 过滤掉超出能量预算的路径
        feasible_paths = [
            p for p in paths
            if p.estimated_energy_cost <= energy_budget
        ]
        
        if not feasible_paths:
            return None
        
        # 按可行性分数和能量效率排序
        # 使用综合评分：可行性 * 0.7 + 能量效率 * 0.3
        scored_paths = []
        for path in feasible_paths:
            energy_efficiency = 1.0 - (path.estimated_energy_cost / energy_budget)
            composite_score = (
                path.feasibility_score * 0.7 +
                energy_efficiency * 0.3
            )
            scored_paths.append((composite_score, path))
        
        # 返回得分最高的路径
        scored_paths.sort(key=lambda x: x[0], reverse=True)
        return scored_paths[0][1] if scored_paths else None
