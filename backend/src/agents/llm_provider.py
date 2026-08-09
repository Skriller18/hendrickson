from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ollama import AsyncClient as OllamaAsyncClient

from src.agents.models import get_provider_for_model


class LLMProvider:
    def __init__(
        self,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        deepseek_api_key: str = "",
        openrouter_api_key: str = "",
        ollama_base_url: str = "http://localhost:11434",
        default_model: str = "gpt-5.6-terra",
    ):
        self._openai_key = openai_api_key
        self._anthropic_key = anthropic_api_key
        self._deepseek_key = deepseek_api_key
        self._openrouter_key = openrouter_api_key
        self.ollama_base_url = ollama_base_url
        self.default_model = default_model
        self._user_keys: dict[str, str] = {}
        self._rebuild_clients()

    def _rebuild_clients(self):
        openai_key = self._user_keys.get("openai") or self._openai_key
        anthropic_key = self._user_keys.get("anthropic") or self._anthropic_key
        deepseek_key = self._user_keys.get("deepseek") or self._deepseek_key
        openrouter_key = self._user_keys.get("openrouter") or self._openrouter_key

        self.openai = AsyncOpenAI(api_key=openai_key) if openai_key else None
        self.anthropic = AsyncAnthropic(api_key=anthropic_key) if anthropic_key else None
        self.deepseek = (
            AsyncOpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
            if deepseek_key
            else None
        )
        self.openrouter = (
            AsyncOpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Hendrickson"},
            )
            if openrouter_key
            else None
        )

    def set_user_keys(self, keys: dict[str, str]):
        self._user_keys = keys
        self._rebuild_clients()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "",
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        model = model or self.default_model
        provider = get_provider_for_model(model) or self._infer_provider(model)

        if provider == "openai":
            return await self._openai_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._anthropic_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == "deepseek":
            return await self._deepseek_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == "openrouter":
            return await self._openrouter_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == "ollama":
            return await self._ollama_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        else:
            return await self._auto_generate(system_prompt, user_prompt, model, temperature, max_tokens)

    def _infer_provider(self, model: str) -> str:
        if model.startswith(("gpt-", "o1", "o3", "o4")):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("deepseek"):
            return "deepseek"
        elif "/" in model:
            return "openrouter"
        return "ollama"

    async def _auto_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        for client, provider_name in [
            (self.openai, "openai"),
            (self.anthropic, "anthropic"),
            (self.deepseek, "deepseek"),
            (self.openrouter, "openrouter"),
        ]:
            if client:
                try:
                    if provider_name == "openai":
                        return await self._openai_generate(system_prompt, user_prompt, model, temperature, max_tokens)
                    elif provider_name == "anthropic":
                        return await self._anthropic_generate(system_prompt, user_prompt, model, temperature, max_tokens)
                    elif provider_name == "deepseek":
                        return await self._deepseek_generate(system_prompt, user_prompt, model, temperature, max_tokens)
                    elif provider_name == "openrouter":
                        return await self._openrouter_generate(system_prompt, user_prompt, model, temperature, max_tokens)
                except Exception:
                    continue

        try:
            return await self._ollama_generate(system_prompt, user_prompt, model, temperature, max_tokens)
        except Exception:
            raise ValueError(
                "No LLM provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, "
                "DEEPSEEK_API_KEY, OPENROUTER_API_KEY, or ensure Ollama is running."
            )

    async def _openai_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        if not self.openai:
            raise ValueError("OpenAI not configured")
        resp = await self.openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    async def _anthropic_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        if not self.anthropic:
            raise ValueError("Anthropic not configured")
        resp = await self.anthropic.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.content[0].text if resp.content else ""

    async def _deepseek_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        if not self.deepseek:
            raise ValueError("DeepSeek not configured")
        resp = await self.deepseek.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    async def _openrouter_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        if not self.openrouter:
            raise ValueError("OpenRouter not configured")
        resp = await self.openrouter.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    async def _ollama_generate(
        self, system_prompt: str, user_prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        client = OllamaAsyncClient(host=self.ollama_base_url)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        resp = await client.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        return resp["message"]["content"]
