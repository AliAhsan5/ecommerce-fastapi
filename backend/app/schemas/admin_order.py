from typing import Literal

from pydantic import BaseModel


OrderStatus = Literal[
    "pending",
    "confirmed",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus