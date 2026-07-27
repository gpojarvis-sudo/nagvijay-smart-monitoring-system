import httpx
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


class CloudflareClient:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token = settings.CLOUDFLARE_API_TOKEN
        self.model = settings.CLOUDFLARE_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

        self.base_url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
        conversation_id: Optional[str] = None,
        history: Optional[list] = None,
    ) -> str:
        prompt = message
        if context:
            prompt = f"{context}\n\nUser: {message}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()
        if "result" in data:
            result = data["result"]

            if isinstance(result, dict):
                if "response" in result:
                    return result["response"]

                if "text" in result:
                    return result["text"]

                if "result" in result:
                    return result["result"]

                if "choices" in result and result["choices"]:
                    choice = result["choices"][0]
                    if (
                        isinstance(choice, dict)
                        and "message" in choice
                        and isinstance(choice["message"], dict)
                        and "content" in choice["message"]
                    ):
                        return choice["message"]["content"]

        raise RuntimeError(f"Unexpected Cloudflare response: {data}")
