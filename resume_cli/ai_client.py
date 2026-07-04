"""OpenAI API client with JSON repair and mock support."""

from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from resume_cli.config import Settings
from resume_cli.prompts import REPAIR_SYSTEM, REPAIR_USER

T = TypeVar("T", bound=BaseModel)


class AIClientError(Exception):
    """Raised when AI API call or JSON parsing fails."""


def _strip_json_fence(content: str) -> str:
    content = content.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if match:
        return match.group(1).strip()
    return content


def _parse_json(content: str) -> dict[str, Any]:
    cleaned = _strip_json_fence(content)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIClientError(f"JSON 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise AIClientError("模型返回的不是 JSON 对象")
    return data


class AIClient:
    def __init__(self, settings: Settings, mock: bool = False) -> None:
        self.settings = settings
        self.mock = mock
        self._client: OpenAI | None = None
        if not mock:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

    def chat(self, system: str, user: str) -> str:
        if self.mock:
            raise AIClientError("mock 模式下不应调用真实 API")
        assert self._client is not None
        try:
            response = self._client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=self.settings.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as exc:
            raise AIClientError(f"API 调用失败: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise AIClientError("API 返回空内容")
        return content

    def parse_structured(
        self,
        model_cls: type[T],
        system: str,
        user: str,
        schema_hint: str | None = None,
    ) -> T:
        raw = self.chat(system, user)
        try:
            data = _parse_json(raw)
            return model_cls.model_validate(data)
        except (AIClientError, ValidationError):
            return self._repair_and_validate(model_cls, raw, schema_hint or model_cls.model_json_schema())

    def _repair_and_validate(
        self,
        model_cls: type[T],
        raw_content: str,
        schema_hint: str | dict,
    ) -> T:
        last_error: Exception | None = None
        content = raw_content
        for _ in range(self.settings.max_retries):
            try:
                repair_user = REPAIR_USER.format(
                    schema_hint=json.dumps(schema_hint, ensure_ascii=False, indent=2),
                    raw_content=content,
                )
                repaired = self.chat(REPAIR_SYSTEM, repair_user)
                data = _parse_json(repaired)
                return model_cls.model_validate(data)
            except (AIClientError, ValidationError) as exc:
                last_error = exc
                content = repaired if "repaired" in locals() else raw_content
        raise AIClientError(
            f"JSON 修复失败（已重试 {self.settings.max_retries} 次）: {last_error}"
        ) from last_error
