"""
PhilosopherLayer - 哲学家层
处理输入的自然语言 Vibe，将其解析为结构化意图
"""

from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .llm_factory import LLMFactory, ModelProvider
import os
from dotenv import load_dotenv

load_dotenv()


class ParsedVibe(BaseModel):
    """解析后的 Vibe 结构"""
    intent: str = Field(..., description="核心意图")
    domain: str = Field(..., description="所属领域")
    complexity: int = Field(..., ge=1, le=10, description="复杂度评分 1-10")
    required_skills: list[str] = Field(default_factory=list, description="所需技能列表")
    constraints: list[str] = Field(default_factory=list, description="约束条件")


class PhilosopherLayer:
    """
    哲学家层 - 将模糊的 Vibe 塌缩为清晰的意图结构
    """
    
    def __init__(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
    ):
        """
        初始化哲学家层
        
        Args:
            provider: LLM 提供商 ("openai" 或 "gemini")，如果为 None 则自动检测
            model_name: 使用的 LLM 模型名称，如果为 None 则使用默认值
            temperature: 温度参数（较低值保证更稳定的解析）
        """
        self.llm = LLMFactory.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
        )
        self.parser = PydanticOutputParser(pydantic_object=ParsedVibe)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一个哲学层面的意图解析器。你的任务是将模糊的自然语言"Vibe"解析为清晰的结构化意图。

解析规则：
1. 提取核心意图：用一句话概括用户真正想要什么
2. 识别领域：判断任务属于哪个领域（编程、数据分析、文本处理等）
3. 评估复杂度：1-10分，1最简单，10最复杂
4. 推断所需技能：列出完成这个任务需要的技能
5. 识别约束：找出任何限制条件或要求

{format_instructions}"""),
            ("human", "请解析以下 Vibe：\n{vibe}"),
        ])
    
    def parse_vibe(self, vibe: str) -> ParsedVibe:
        """
        解析 Vibe 为结构化意图
        
        Args:
            vibe: 原始自然语言意图
            
        Returns:
            解析后的结构化意图
        """
        prompt = self.prompt_template.format_messages(
            vibe=vibe,
            format_instructions=self.parser.get_format_instructions(),
        )
        
        response = self.llm.invoke(prompt)
        parsed = self.parser.parse(response.content)
        
        return parsed
    
    def extract_task_plan(self, parsed_vibe: ParsedVibe) -> Dict[str, Any]:
        """
        从解析后的 Vibe 生成任务规划
        
        Args:
            parsed_vibe: 解析后的 Vibe
            
        Returns:
            任务规划字典
        """
        return {
            "intent": parsed_vibe.intent,
            "domain": parsed_vibe.domain,
            "complexity": parsed_vibe.complexity,
            "steps": self._generate_steps(parsed_vibe),
            "estimated_energy_cost": parsed_vibe.complexity * 10,
        }
    
    def _generate_steps(self, parsed_vibe: ParsedVibe) -> list[str]:
        """
        根据解析结果生成执行步骤
        
        Args:
            parsed_vibe: 解析后的 Vibe
            
        Returns:
            步骤列表
        """
        # 根据复杂度和领域生成基础步骤
        base_steps = [
            "理解需求",
            "设计解决方案",
            "实现核心功能",
            "验证结果",
        ]
        
        # 根据复杂度调整步骤
        if parsed_vibe.complexity > 7:
            base_steps.insert(2, "架构设计")
            base_steps.append("性能优化")
        
        if parsed_vibe.complexity > 5:
            base_steps.insert(-1, "错误处理")
        
        return base_steps
