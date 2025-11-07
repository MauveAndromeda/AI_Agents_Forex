"""
Unified LLM Client for AI-Enhanced Trading
Supports multiple providers: OpenAI, Anthropic, Google, DeepSeek
"""

import os
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"


class BaseLLMClient(ABC):
    """Base class for LLM clients"""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate completion"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-nano"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model  # 默认使用 gpt-5-nano (GPT-5 系列最快最经济的模型)

        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return ""


class GoogleClient(BaseLLMClient):
    """Google Gemini API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("Google API key not provided")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return ""


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"

        if not self.api_key:
            raise ValueError("DeepSeek API key not provided")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return ""


class UnifiedLLMClient:
    """
    Unified interface for multiple LLM providers
    Handles fallback and load balancing
    """

    def __init__(self, providers: List[LLMProvider] = None):
        """
        Initialize with list of providers in priority order

        Args:
            providers: List of LLM providers to use
        """
        if providers is None:
            providers = [LLMProvider.DEEPSEEK, LLMProvider.OPENAI]

        self.clients: Dict[LLMProvider, BaseLLMClient] = {}
        self.providers = providers

        # Initialize available clients
        for provider in providers:
            try:
                client = self._create_client(provider)
                self.clients[provider] = client
                logger.info(f"Initialized {provider.value} client")
            except Exception as e:
                logger.warning(f"Failed to initialize {provider.value}: {e}")

        if not self.clients:
            raise ValueError("No LLM clients could be initialized")

    def _create_client(self, provider: LLMProvider) -> BaseLLMClient:
        """Create client for specific provider"""
        if provider == LLMProvider.OPENAI:
            return OpenAIClient()
        elif provider == LLMProvider.ANTHROPIC:
            return AnthropicClient()
        elif provider == LLMProvider.GOOGLE:
            return GoogleClient()
        elif provider == LLMProvider.DEEPSEEK:
            return DeepSeekClient()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate(self,
                prompt: str,
                temperature: float = 0.7,
                max_tokens: int = 1000,
                preferred_provider: Optional[LLMProvider] = None) -> str:
        """
        Generate completion with automatic fallback

        Args:
            prompt: Prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            preferred_provider: Preferred provider (optional)

        Returns:
            Generated text
        """
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.clients:
            try:
                return self.clients[preferred_provider].generate(prompt, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Preferred provider {preferred_provider.value} failed: {e}")

        # Fallback to other providers
        for provider, client in self.clients.items():
            if provider == preferred_provider:
                continue
            try:
                return client.generate(prompt, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue

        logger.error("All LLM providers failed")
        return ""

    def is_available(self, provider: LLMProvider) -> bool:
        """Check if provider is available"""
        return provider in self.clients


# Example usage
if __name__ == "__main__":
    # Initialize with DeepSeek as primary
    client = UnifiedLLMClient([LLMProvider.DEEPSEEK])

    # Test generation
    prompt = "Analyze the current EURUSD market trend based on the following data: Price is at 1.0850, RSI is at 45, MACD histogram is positive. What is your trading recommendation?"

    response = client.generate(prompt, temperature=0.5)
    print(f"Response: {response}")
