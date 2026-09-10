from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import (
    process_chat_message,
)


router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    return process_chat_message(
        db=db,
        message=request.message,
        history=request.history,
    )