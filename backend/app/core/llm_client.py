import json
import ssl
from typing import Any, Optional

import httpx

from app.config import settings


class LLMCallError(Exception):
    pass


_ssl_context = ssl.create_default_context()


def _build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.LLM_API_BASE.rstrip("/"),
        timeout=httpx.Timeout(settings.LLM_TIMEOUT_SECONDS, connect=10.0),
        verify=_ssl_context,
    )


def _build_messages(system_prompt: str, user_prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_body(
    system_prompt: str,
    user_prompt: str,
    response_format_json: bool,
    **kwargs: Any,
) -> dict:
    body: dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "messages": _build_messages(system_prompt, user_prompt),
    }

    if response_format_json:
        body["response_format"] = {"type": "json_object"}

    if "max_tokens" not in kwargs or kwargs.get("max_tokens") is None:
        body["max_tokens"] = settings.LLM_MAX_TOKENS
    else:
        body["max_tokens"] = kwargs["max_tokens"]

    for key in ("temperature", "top_p", "frequency_penalty", "presence_penalty"):
        if kwargs.get(key) is not None:
            body[key] = kwargs[key]

    return body


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    response_format_json: bool = True,
    **kwargs: Any,
) -> dict:
    api_key = settings.LLM_API_KEY
    if not api_key:
        return {
            "success": False,
            "content": "",
            "error": "LLM_API_KEY is not configured",
        }

    body = _build_body(system_prompt, user_prompt, response_format_json, **kwargs)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    client: Optional[httpx.AsyncClient] = None
    try:
        client = _build_client()
        resp = await client.post(
            "/chat/completions",
            headers=headers,
            content=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        )

        if resp.status_code != 200:
            return {
                "success": False,
                "content": "",
                "error": f"HTTP {resp.status_code}: {resp.text[:500]}",
            }

        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return {
                "success": False,
                "content": "",
                "error": "LLM returned no choices",
            }

        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        return {
            "success": True,
            "content": content,
            "error": None,
        }
    except httpx.TimeoutException as e:
        return {"success": False, "content": "", "error": f"timeout: {e}"}
    except httpx.HTTPError as e:
        return {"success": False, "content": "", "error": f"http_error: {e}"}
    except json.JSONDecodeError as e:
        return {"success": False, "content": "", "error": f"invalid_json: {e}"}
    except Exception as e:
        return {"success": False, "content": "", "error": f"unexpected: {e}"}
    finally:
        if client is not None:
            await client.aclose()


async def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    **kwargs: Any,
) -> dict:
    result = await call_llm(system_prompt, user_prompt, response_format_json=True, **kwargs)
    if not result["success"]:
        return result

    content = result["content"]
    try:
        parsed = json.loads(content)
        return {
            "success": True,
            "content": content,
            "data": parsed,
            "error": None,
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "content": content,
            "error": f"invalid_json_response: {e}",
        }
