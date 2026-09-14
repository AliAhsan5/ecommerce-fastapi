from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
)
from app.core.chat_rate_limit import (
    enforce_chat_rate_limit,
)
from app.db.session import (
    get_db,
)
from app.models.user import (
    User,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.ai_order_service import (
    generate_order_assistant_response,
)
from app.services.chat_service import (
    process_chat_message,
)


router = APIRouter()


# -------------------------------------
# PUBLIC PRODUCT CHAT
# -------------------------------------

@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,

    db: Session = Depends(
        get_db
    ),

    _: None = Depends(
        enforce_chat_rate_limit
    ),
):
    return process_chat_message(
        db=db,
        message=request.message,
        history=request.history,
    )


# -------------------------------------
# AUTHENTICATED PRIVATE ORDER CHAT
# -------------------------------------

@router.post(
    "/order",
    response_model=ChatResponse,
)
def order_chat(
    request: ChatRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),

    _: None = Depends(
        enforce_chat_rate_limit
    ),
):
    reply = (
        generate_order_assistant_response(
            db=db,
            current_user=current_user,
            message=request.message,
            history=request.history,
        )
    )

    return ChatResponse(
        reply=reply,
        products=[],
    )