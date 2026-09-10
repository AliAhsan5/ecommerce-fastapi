from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatHistoryMessage,
    ChatProductResponse,
    ChatResponse,
)
from app.services.ai_service import (
    generate_ai_response,
)
from app.services.product_context_service import (
    get_relevant_product_context,
)


GREETINGS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "salam",
    "salaam",
    "aoa",
    "assalamualaikum",
    "assalam o alaikum",
    "assalam-o-alaikum",
}


FOLLOW_UP_WORDS = {
    "it",
    "its",
    "this",
    "that",
    "this one",
    "that one",
    "iski",
    "iska",
    "iske",
    "uski",
    "uska",
    "uske",
    "ye",
    "yeh",
    "wo",
    "woh",
}


def is_greeting_message(
    message: str,
) -> bool:

    normalized = (
        message
        .strip()
        .lower()
    )

    return normalized in GREETINGS


def is_follow_up_message(
    message: str,
) -> bool:

    normalized = (
        message
        .strip()
        .lower()
    )

    words = normalized.split()

    if any(
        word in FOLLOW_UP_WORDS
        for word in words
    ):
        return True

    follow_up_phrases = [
        "what about",
        "how much",
        "what is the price",
        "what's the price",
        "price kya",
        "kitne ka",
        "kitnay ka",
        "stock kitna",
        "stock kitni",
    ]

    return any(
        phrase in normalized
        for phrase in follow_up_phrases
    )


def get_reference_user_message(
    history: list[ChatHistoryMessage],
) -> str | None:

    for history_message in reversed(
        history
    ):

        if (
            history_message.role == "user"
            and not is_follow_up_message(
                history_message.content
            )
        ):
            return history_message.content

    return None


def build_retrieval_message(
    message: str,
    history: list[ChatHistoryMessage],
) -> str:

    if not is_follow_up_message(
        message
    ):
        return message

    reference_message = (
        get_reference_user_message(
            history
        )
    )

    if reference_message is None:
        return message

    return reference_message


def build_history_text(
    history: list[ChatHistoryMessage],
) -> str:

    if not history:
        return "No previous conversation."

    lines = []

    for history_message in history:

        role = (
            "CUSTOMER"
            if history_message.role
            == "user"
            else "ASSISTANT"
        )

        lines.append(
            f"{role}: "
            f"{history_message.content}"
        )

    return "\n".join(lines)


def build_grounded_prompt(
    message: str,
    store_context: str,
    history: list[ChatHistoryMessage],
) -> str:

    history_text = (
        build_history_text(
            history
        )
    )

    return f"""
RECENT CONVERSATION:
{history_text}

CURRENT CUSTOMER MESSAGE:
{message}

VERIFIED RELEVANT STORE DATA:
{store_context}

INSTRUCTIONS:

Answer the CURRENT CUSTOMER MESSAGE using
the recent conversation only for conversational
context and the VERIFIED RELEVANT STORE DATA
for store facts.

Important rules:

1. Store-related factual claims must come only
   from VERIFIED RELEVANT STORE DATA.

2. Never invent products, prices, stock,
   brands, categories, variants, or SKUs.

3. Use RECENT CONVERSATION to understand
   references such as "it", "this", "iski",
   "iska", or similar follow-up language.

4. Previous assistant messages are context,
   not authoritative store data.

5. If Stock Quantity is 0, clearly say that
   the product is out of stock.

6. Never say an out-of-stock product is
   currently available.

7. When recommending products, mention only
   products supplied in VERIFIED RELEVANT
   STORE DATA.

8. Keep the answer concise and useful.

9. Respond naturally in the same language
   style as the customer.
"""


def get_chat_products(
    products: list[dict],
) -> list[ChatProductResponse]:

    chat_products = []

    for product in products:

        chat_products.append(
            ChatProductResponse(
                id=product["id"],
                name=product["name"],
                slug=product["slug"],

                variant_id=product[
                    "variant_id"
                ],

                variant_name=product[
                    "variant_name"
                ],

                effective_price=product[
                    "effective_price"
                ],

                stock_quantity=product[
                    "stock_quantity"
                ],

                image_url=product[
                    "image_url"
                ],
            )
        )

    return chat_products


def process_chat_message(
    db: Session,
    message: str,
    history: list[ChatHistoryMessage] | None = None,
) -> ChatResponse:

    history = history or []

    if is_greeting_message(
        message
    ):
        return ChatResponse(
            reply=(
                "Hi! I'm your AI shopping assistant. "
                "How can I help you find a product today?"
            ),
            products=[],
        )

    retrieval_message = (
        build_retrieval_message(
            message=message,
            history=history,
        )
    )

    store_context, products = (
        get_relevant_product_context(
            db=db,
            message=retrieval_message,
            limit=10,
        )
    )

    if not products:

        return ChatResponse(
            reply=(
                "Sorry, I couldn't find any "
                "matching verified product "
                "in our store."
            ),
            products=[],
        )

    grounded_prompt = (
        build_grounded_prompt(
            message=message,
            store_context=store_context,
            history=history,
        )
    )

    reply = generate_ai_response(
        grounded_prompt
    )

    chat_products = (
        get_chat_products(
            products
        )
    )

    return ChatResponse(
        reply=reply,
        products=chat_products,
    )