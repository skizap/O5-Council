from __future__ import annotations

from typing import Any

import httpx

from o5_council.config import OPENROUTER_BASE_URL, OPENROUTER_REFERER, OPENROUTER_TITLE


class OpenRouterError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        *,
        site_url: str | None = None,
        site_name: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        if not api_key.strip():
            raise OpenRouterError("An OpenRouter API key is required.")
        self.api_key = api_key.strip()
        self.site_url = (site_url or OPENROUTER_REFERER).strip()
        self.site_name = (site_name or OPENROUTER_TITLE).strip()
        self.timeout_seconds = timeout_seconds

    def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-OpenRouter-Title": self.site_name,
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip()
            raise OpenRouterError(
                f"OpenRouter returned HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OpenRouterError(f"Network error while contacting OpenRouter: {exc}") from exc

        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise OpenRouterError("OpenRouter returned a response without choices.")
        return data

    @staticmethod
    def extract_text(response_data: dict[str, Any]) -> str:
        choice = response_data["choices"][0]
        message = choice.get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            return "\n".join(part.strip() for part in parts if part.strip()).strip()
        return str(content).strip()
