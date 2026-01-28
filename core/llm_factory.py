"""
LLM Factory - 支持多种 LLM 提供商的工厂类
"""

from typing import Optional, Literal
from langchain_openai import ChatOpenAI as LangChainChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
import os
from dotenv import load_dotenv

load_dotenv()

ModelProvider = Literal["openai", "gemini"]
ModelName = Literal[
    "gpt-4", "gpt-3.5-turbo",  # OpenAI
    "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro",  # Gemini
]


class LLMFactory:
    """
    LLM 工厂类 - 统一创建不同提供商的 LLM 实例
    """
    
    @staticmethod
    def create_llm(
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ) -> BaseChatModel:
        """
        创建 LLM 实例
        
        Args:
            provider: 提供商 ("openai" 或 "gemini")，如果为 None 则自动检测
            model_name: 模型名称，如果为 None 则使用默认值
            temperature: 温度参数
            
        Returns:
            LLM 实例
        """
        # 自动检测提供商
        if provider is None:
            provider = LLMFactory._detect_provider()
        
        # 设置默认模型名称：参数 > env(按 provider) > env(全局) > 内置默认
        if model_name is None:
            model_name = LLMFactory._resolve_model_name_from_env(provider)
        
        if provider == "openai":
            return LLMFactory._create_openai_llm(model_name, temperature)
        elif provider == "gemini":
            return LLMFactory._create_gemini_llm(model_name, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _resolve_model_name_from_env(provider: ModelProvider) -> str:
        """
        从环境变量解析默认 model_name。

        优先级：
        1) {PROVIDER}_MODEL_NAME（如 GEMINI_MODEL_NAME / OPENAI_MODEL_NAME）
        2) LLM_MODEL_NAME（全局默认）
        3) 内置默认（OpenAI -> gpt-4, Gemini -> gemini-1.5-flash）
        """
        provider_key = "GEMINI_MODEL_NAME" if provider == "gemini" else "OPENAI_MODEL_NAME"
        by_provider = (os.getenv(provider_key) or "").strip()
        if by_provider:
            print(f"[LLMFactory] 从环境变量读取 {provider_key}: {by_provider}")
            return by_provider

        global_default = (os.getenv("LLM_MODEL_NAME") or "").strip()
        if global_default:
            print(f"[LLMFactory] 从环境变量读取 LLM_MODEL_NAME: {global_default}")
            return global_default

        default_model = "gemini-1.5-flash" if provider == "gemini" else "gpt-4"
        print(f"[LLMFactory] 使用内置默认模型: {default_model}")
        return default_model
    
    @staticmethod
    def _detect_provider() -> ModelProvider:
        """
        自动检测应该使用哪个提供商
        
        优先级：
        1. 如果设置了 LLM_PROVIDER 环境变量，使用它
        2. 如果设置了 GEMINI_API_KEY，使用 Gemini
        3. 如果设置了 OPENAI_API_KEY，使用 OpenAI
        4. 默认使用 OpenAI
        """
        explicit_provider = os.getenv("LLM_PROVIDER", "").lower()
        if explicit_provider in ["openai", "gemini"]:
            return explicit_provider
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gemini_key and not openai_key:
            return "gemini"
        elif openai_key:
            return "openai"
        else:
            # 默认尝试 OpenAI，如果失败会在使用时报错
            return "openai"
    
    @staticmethod
    def _create_openai_llm(model_name: str, temperature: float) -> LangChainChatOpenAI:
        """
        创建 OpenAI LLM 实例
        
        Args:
            model_name: 模型名称
            temperature: 温度参数
            
        Returns:
            ChatOpenAI 实例
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set OPENAI_API_KEY in your .env file."
            )
        
        return LangChainChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )
    
    @staticmethod
    def _create_gemini_llm(model_name: str, temperature: float) -> ChatGoogleGenerativeAI:
        """
        创建 Gemini LLM 实例
        
        Args:
            model_name: 模型名称（例如 "gemini-2.0-flash-exp"）
            temperature: 温度参数
            
        Returns:
            ChatGoogleGenerativeAI 实例
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set GEMINI_API_KEY in your .env file."
            )
        
        # 映射模型名称
        # Gemini 模型名称映射（支持多种命名方式）
        # 注意：只映射已知不存在的模型名称，如果用户明确指定了模型名称，优先使用用户指定的
        model_mapping = {
            # 只映射已知不存在的模型名称
            "gemini-2.0-flash-exp": "gemini-1.5-flash",  # 这个模型不存在
            "gemini-flash": "gemini-1.5-flash",  # 通用别名
            # 保留用户明确指定的模型名称（如 gemini-2.5-flash, gemini-2.0-flash 等）
            # 如果这些模型不存在，API 会返回错误，让用户知道需要修改配置
        }
        
        # 如果模型名称在映射表中，使用映射后的名称
        # 否则直接使用用户指定的模型名称
        actual_model_name = model_mapping.get(model_name.lower(), model_name)

        print(f"[LLMFactory] 使用 Gemini 模型: {actual_model_name} (原始: {model_name})")
        
        return ChatGoogleGenerativeAI(
            model=actual_model_name,
            temperature=temperature,
            google_api_key=api_key,
        )
