
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=200)
    email: EmailStr


class GenerationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_name: str = Field(min_length=2, max_length=200)
    issuer: str = Field(min_length=2, max_length=200)

    recipients: list[dict[str, Any]] = Field(
        min_length=1,
        max_length=1000,
    )
