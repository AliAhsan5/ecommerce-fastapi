from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class ChatHistoryMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=1000,
    )


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )

    history: list[
        ChatHistoryMessage
    ] = Field(
        default_factory=list,
        max_length=6,
    )


class ChatProductResponse(BaseModel):
    id: int
    name: str
    slug: str

    variant_id: int
    variant_name: str

    effective_price: Decimal
    stock_quantity: int

    image_url: str | None = None


class ChatResponse(BaseModel):
    reply: str

    products: list[
        ChatProductResponse
    ] = Field(
        default_factory=list
    )