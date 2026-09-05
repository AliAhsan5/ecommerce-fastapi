from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None

    action: str
    entity_type: str
    entity_id: int | None

    details: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]

    page: int
    page_size: int
    total: int