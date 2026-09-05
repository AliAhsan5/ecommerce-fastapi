from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def list_audit_logs(
    db: Session,
    page: int,
    page_size: int,
    action: str | None = None,
    entity_type: str | None = None,
    user_id: int | None = None,
) -> tuple[list[AuditLog], int]:

    conditions = []


    if action is not None:
        conditions.append(
            AuditLog.action == action
        )


    if entity_type is not None:
        conditions.append(
            AuditLog.entity_type
            == entity_type
        )


    if user_id is not None:
        conditions.append(
            AuditLog.user_id == user_id
        )


    total = db.scalar(
        select(
            func.count(
                AuditLog.id
            )
        ).where(
            *conditions
        )
    ) or 0


    logs = list(
        db.scalars(
            select(AuditLog)
            .where(
                *conditions
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(
                (page - 1)
                * page_size
            )
            .limit(
                page_size
            )
        ).all()
    )


    return logs, total