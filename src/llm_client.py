"""Small provider abstraction for JSON-generating LLM calls."""

import json
from typing import Any, Dict

from src.config import Settings


class LLMConfigurationError(RuntimeError):
    """Raised when the selected provider is not configured."""


class LLMClient:
    """Generate JSON responses through the configured provider."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        provider = self.settings.llm_provider.lower()
        if provider == "openai":
            response_text = self._generate_openai(system_prompt, user_prompt)
        elif provider == "gemini":
            response_text = self._generate_gemini(system_prompt, user_prompt)
        else:
            raise LLMConfigurationError(f"Unsupported LLM provider: {provider}")

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid JSON") from exc

    def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.openai_api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured")

        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def _generate_gemini(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.gemini_api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured")

        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name=self.settings.llm_model,
            system_instruction=system_prompt,
        )
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        return response.text