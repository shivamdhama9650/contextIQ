import logging

from langchain_core.language_models import BaseChatModel

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_llm() -> BaseChatModel:
    """
    Get the configured LangChain chat model based on environment settings.
    Falls back dynamically based on available environment variables.
    """
    provider = settings.llm_provider.lower()

    if provider == "mock":
        return build_mock_llm()

    if _is_placeholder_key(settings.gemini_api_key) and _is_placeholder_key(
        settings.groq_api_key
    ):
        logger.warning("No usable LLM API keys found. Falling back to Mock LLM.")
        return build_mock_llm()

    # Dynamic auto-detection if provider settings or API keys suggest a preference
    if not settings.gemini_api_key and not settings.groq_api_key:
        logger.warning("No LLM API keys found. Falling back to Mock LLM.")
        return build_mock_llm()

    # Default to Gemini if key is present or provider is explicitly gemini
    if provider == "gemini" or (
        not _is_placeholder_key(settings.gemini_api_key)
        and _is_placeholder_key(settings.groq_api_key)
    ):
        if _is_placeholder_key(settings.gemini_api_key):
            raise ValueError("GEMINI_API_KEY is not set but 'gemini' was requested.")

        from langchain_google_genai import ChatGoogleGenerativeAI

        model_name = settings.llm_model or "gemini-1.5-flash"
        logger.info(f"Initializing Gemini Chat Model: {model_name}")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.gemini_api_key,
            temperature=0.0,
        )

    # Groq provider
    elif provider == "groq" or (
        not _is_placeholder_key(settings.groq_api_key)
        and _is_placeholder_key(settings.gemini_api_key)
    ):
        if _is_placeholder_key(settings.groq_api_key):
            raise ValueError("GROQ_API_KEY is not set but 'groq' was requested.")

        from langchain_groq import ChatGroq

        model_name = settings.llm_model or "llama-3.1-8b-instant"
        logger.info(f"Initializing Groq Chat Model: {model_name}")
        return ChatGroq(
            model=model_name,
            groq_api_key=settings.groq_api_key,
            temperature=0.0,
        )

    else:
        raise ValueError(f"Unknown or unsupported LLM provider configuration: {provider}")


def _is_placeholder_key(value: str | None) -> bool:
    if value is None:
        return True

    normalized = value.strip()
    return not normalized or normalized.upper().startswith("YOUR_")


def build_mock_llm() -> BaseChatModel:
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage

    logger.info("Initializing Fake Messages Chat Model for testing/fallback.")
    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content=(
                    "[MOCK ANSWER] This is a mock response from the Knowledge "
                    "Assistant. Configure GEMINI_API_KEY or GROQ_API_KEY for "
                    "real answers."
                )
            )
        ]
    )
