import logging

import httpx
from google import genai
from google.genai import errors, types

from app.core.config import get_settings
from app.core.exceptions import AppException


logger = logging.getLogger(__name__)

settings = get_settings()


# Force IPv4 because IPv6 connectivity to the
# Gemini API endpoint is unreliable on this machine.
transport = httpx.HTTPTransport(
    local_address="0.0.0.0"
)


http_client = httpx.Client(
    transport=transport,
    trust_env=False,
)


client = genai.Client(
    api_key=settings.gemini_api_key,

    http_options=types.HttpOptions(
        httpx_client=http_client,
        timeout=30_000,
    ),
)


SYSTEM_INSTRUCTION = """
You are an AI shopping assistant for an e-commerce store.

Your job is to help customers understand and find products.

Important rules:

1. Never invent products.
2. Never invent prices.
3. Never invent stock availability.
4. Never invent brands, categories, or product specifications.
5. Store-related facts must come only from information supplied
   by the application.
6. If required store information is not available, clearly say
   that you cannot verify it.
7. Keep responses helpful, clear, and concise.
8. Respond naturally in the same language style as the customer.
"""


def call_gemini_model(
    model: str,
    message: str,
) -> str:

    response = client.models.generate_content(
        model=model,

        contents=message,

        config=types.GenerateContentConfig(
            system_instruction=
                SYSTEM_INSTRUCTION,

            max_output_tokens=500,

            automatic_function_calling=
                types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
        ),
    )


    if not response.text:
        raise AppException(
            message=(
                "AI service returned "
                "an empty response."
            ),
            status_code=503,
        )


    return response.text.strip()


def generate_ai_response(
    message: str,
) -> str:

    models = [
        settings.gemini_model,
        settings.gemini_fallback_model,
    ]


    last_error = None


    for model in models:

        try:
            logger.info(
                "Sending AI request using model: %s",
                model,
            )

            return call_gemini_model(
                model=model,
                message=message,
            )


        except errors.ServerError as exc:

            last_error = exc

            logger.warning(
                "Gemini model %s unavailable. "
                "Trying fallback model.",
                model,
            )

            continue


        except AppException:
            raise


        except Exception as exc:

            logger.exception(
                "Gemini API request failed."
            )

            raise AppException(
                message=(
                    "AI service is temporarily "
                    "unavailable."
                ),
                status_code=503,
            ) from exc


    logger.exception(
        "All Gemini models are unavailable.",
        exc_info=last_error,
    )


    raise AppException(
        message=(
            "AI service is temporarily "
            "busy. Please try again shortly."
        ),
        status_code=503,
    ) from last_error