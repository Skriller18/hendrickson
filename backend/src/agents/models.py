from typing import Optional
from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: str = ""
    context_window: int = 128000
    max_output_tokens: int = 16384
    supports_vision: bool = False
    supports_tools: bool = True
    cost_level: str = "medium"


PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": [
            ModelInfo(
                id="gpt-5.6-sol",
                name="GPT-5.6 Sol",
                provider="openai",
                description="Flagship model for complex reasoning and professional-grade coding",
                context_window=200000,
                max_output_tokens=32768,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="gpt-5.6-terra",
                name="GPT-5.6 Terra",
                provider="openai",
                description="Standard workhorse — balances intelligence with cost-efficiency",
                context_window=200000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="gpt-5.6-luna",
                name="GPT-5.6 Luna",
                provider="openai",
                description="Entry-level cost-optimized model for high-volume workloads",
                context_window=128000,
                max_output_tokens=16384,
                cost_level="low",
            ),
            ModelInfo(
                id="gpt-5.5-pro",
                name="GPT-5.5 Pro",
                provider="openai",
                description="Alternative high-compute model for specialized needs",
                context_window=200000,
                max_output_tokens=32768,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="gpt-5.4-mini",
                name="GPT-5.4 Mini",
                provider="openai",
                description="Smaller, faster model for lightweight tasks",
                context_window=128000,
                max_output_tokens=16384,
                cost_level="low",
            ),
            ModelInfo(
                id="o3",
                name="o3",
                provider="openai",
                description="Standard reasoning model for deep logical analysis",
                context_window=200000,
                max_output_tokens=100000,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="o3-pro",
                name="o3 Pro",
                provider="openai",
                description="Compute-intensive o3 variant for highest-accuracy solutions",
                context_window=200000,
                max_output_tokens=100000,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="o4-mini",
                name="o4 Mini",
                provider="openai",
                description="Fast, cost-efficient reasoning model",
                context_window=200000,
                max_output_tokens=100000,
                cost_level="low",
            ),
            ModelInfo(
                id="o4-mini-high",
                name="o4 Mini High",
                provider="openai",
                description="o4-mini with extended deliberation time",
                context_window=200000,
                max_output_tokens=100000,
                cost_level="medium",
            ),
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            ModelInfo(
                id="claude-fable-5",
                name="Claude Fable 5",
                provider="anthropic",
                description="Most capable generally available Claude model",
                context_window=200000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="claude-opus-5",
                name="Claude Opus 5",
                provider="anthropic",
                description="Strongest for complex agentic and enterprise work",
                context_window=200000,
                max_output_tokens=32768,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="claude-sonnet-5",
                name="Claude Sonnet 5",
                provider="anthropic",
                description="New default — high performance-to-speed ratio",
                context_window=200000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="claude-haiku-4-5",
                name="Claude Haiku 4.5",
                provider="anthropic",
                description="Efficient, low-latency model for simple tasks",
                context_window=200000,
                max_output_tokens=8192,
                supports_vision=True,
                cost_level="low",
            ),
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": [
            ModelInfo(
                id="deepseek-v4-pro",
                name="DeepSeek V4 Pro",
                provider="deepseek",
                description="Complex reasoning, agentic coding, and large architecture tasks",
                context_window=128000,
                max_output_tokens=32768,
                cost_level="medium",
            ),
            ModelInfo(
                id="deepseek-v4-flash",
                name="DeepSeek V4 Flash",
                provider="deepseek",
                description="Efficient, high-volume workloads and routine tasks",
                context_window=128000,
                max_output_tokens=16384,
                cost_level="low",
            ),
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "models": [
            ModelInfo(
                id="openai/gpt-5.6-terra",
                name="GPT-5.6 Terra (OpenRouter)",
                provider="openrouter",
                description="OpenAI GPT-5.6 Terra via OpenRouter",
                context_window=200000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="openai/gpt-5.6-sol",
                name="GPT-5.6 Sol (OpenRouter)",
                provider="openrouter",
                description="OpenAI GPT-5.6 Sol via OpenRouter",
                context_window=200000,
                max_output_tokens=32768,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="openai/o3",
                name="o3 (OpenRouter)",
                provider="openrouter",
                description="OpenAI o3 reasoning via OpenRouter",
                context_window=200000,
                max_output_tokens=100000,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="openai/o4-mini",
                name="o4 Mini (OpenRouter)",
                provider="openrouter",
                description="OpenAI o4-mini reasoning via OpenRouter",
                context_window=200000,
                max_output_tokens=100000,
                cost_level="low",
            ),
            ModelInfo(
                id="anthropic/claude-sonnet-5",
                name="Claude Sonnet 5 (OpenRouter)",
                provider="openrouter",
                description="Anthropic Claude Sonnet 5 via OpenRouter",
                context_window=200000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="anthropic/claude-opus-5",
                name="Claude Opus 5 (OpenRouter)",
                provider="openrouter",
                description="Anthropic Claude Opus 5 via OpenRouter",
                context_window=200000,
                max_output_tokens=32768,
                supports_vision=True,
                cost_level="high",
            ),
            ModelInfo(
                id="anthropic/claude-haiku-4-5",
                name="Claude Haiku 4.5 (OpenRouter)",
                provider="openrouter",
                description="Anthropic Claude Haiku 4.5 via OpenRouter",
                context_window=200000,
                max_output_tokens=8192,
                supports_vision=True,
                cost_level="low",
            ),
            ModelInfo(
                id="deepseek/deepseek-v4-pro",
                name="DeepSeek V4 Pro (OpenRouter)",
                provider="openrouter",
                description="DeepSeek V4 Pro via OpenRouter",
                context_window=128000,
                max_output_tokens=32768,
                cost_level="medium",
            ),
            ModelInfo(
                id="deepseek/deepseek-v4-flash",
                name="DeepSeek V4 Flash (OpenRouter)",
                provider="openrouter",
                description="DeepSeek V4 Flash via OpenRouter",
                context_window=128000,
                max_output_tokens=16384,
                cost_level="low",
            ),
            ModelInfo(
                id="google/gemini-2.5-pro",
                name="Gemini 2.5 Pro (OpenRouter)",
                provider="openrouter",
                description="Google Gemini 2.5 Pro via OpenRouter",
                context_window=1000000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="google/gemini-2.5-flash",
                name="Gemini 2.5 Flash (OpenRouter)",
                provider="openrouter",
                description="Google Gemini 2.5 Flash via OpenRouter",
                context_window=1000000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="low",
            ),
            ModelInfo(
                id="meta-llama/llama-4-maverick",
                name="Llama 4 Maverick (OpenRouter)",
                provider="openrouter",
                description="Meta Llama 4 Maverick via OpenRouter",
                context_window=128000,
                max_output_tokens=16384,
                cost_level="low",
            ),
        ],
    },
    "gemini": {
        "name": "Google Gemini",
        "models": [
            ModelInfo(
                id="gemini-2.5-pro",
                name="Gemini 2.5 Pro",
                provider="gemini",
                description="Google's most capable model for complex reasoning and coding",
                context_window=1000000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="medium",
            ),
            ModelInfo(
                id="gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                provider="gemini",
                description="Fast, cost-efficient model for high-volume tasks",
                context_window=1000000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="low",
            ),
            ModelInfo(
                id="gemini-2.5-flash-lite",
                name="Gemini 2.5 Flash Lite",
                provider="gemini",
                description="Most cost-effective Gemini model for simple tasks",
                context_window=1000000,
                max_output_tokens=16384,
                supports_vision=True,
                cost_level="low",
            ),
        ],
    },
    "ollama": {
        "name": "Ollama (Local)",
        "models": [
            ModelInfo(
                id="llama3.2",
                name="Llama 3.2",
                provider="ollama",
                description="Meta Llama 3.2 — local, fast, general purpose",
                context_window=128000,
                max_output_tokens=8192,
                cost_level="free",
            ),
            ModelInfo(
                id="llama3.1:70b",
                name="Llama 3.1 70B",
                provider="ollama",
                description="Meta Llama 3.1 70B — larger local model",
                context_window=128000,
                max_output_tokens=8192,
                cost_level="free",
            ),
            ModelInfo(
                id="qwen2.5:72b",
                name="Qwen 2.5 72B",
                provider="ollama",
                description="Alibaba Qwen 2.5 72B — strong coding model",
                context_window=128000,
                max_output_tokens=8192,
                cost_level="free",
            ),
            ModelInfo(
                id="qwen2.5-coder:32b",
                name="Qwen 2.5 Coder 32B",
                provider="ollama",
                description="Alibaba Qwen 2.5 Coder — specialized for code generation",
                context_window=128000,
                max_output_tokens=8192,
                cost_level="free",
            ),
            ModelInfo(
                id="codestral:22b",
                name="Codestral 22B",
                provider="ollama",
                description="Mistral Codestral — code-focused model",
                context_window=32000,
                max_output_tokens=8192,
                cost_level="free",
            ),
            ModelInfo(
                id="deepseek-r1:70b",
                name="DeepSeek R1 70B",
                provider="ollama",
                description="DeepSeek R1 reasoning model — local",
                context_window=128000,
                max_output_tokens=32768,
                cost_level="free",
            ),
            ModelInfo(
                id="phi4:14b",
                name="Phi-4 14B",
                provider="ollama",
                description="Microsoft Phi-4 — compact, strong reasoning",
                context_window=16384,
                max_output_tokens=4096,
                cost_level="free",
            ),
            ModelInfo(
                id="gemma3:27b",
                name="Gemma 3 27B",
                provider="ollama",
                description="Google Gemma 3 — efficient open model",
                context_window=128000,
                max_output_tokens=8192,
                cost_level="free",
            ),
        ],
    },
}


def get_all_models() -> list[ModelInfo]:
    models = []
    for provider_data in PROVIDERS.values():
        models.extend(provider_data["models"])
    return models


def get_models_by_provider(provider: str) -> list[ModelInfo]:
    if provider in PROVIDERS:
        return PROVIDERS[provider]["models"]
    return []


def get_model_by_id(model_id: str) -> Optional[ModelInfo]:
    for model in get_all_models():
        if model.id == model_id:
            return model
    return None


def get_provider_for_model(model_id: str) -> Optional[str]:
    model = get_model_by_id(model_id)
    return model.provider if model else None
