"""Model configuration for OpenAI and OpenAI-compatible providers."""

import os

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI


DEFAULT_MODEL = "gpt-4.1-mini"


def build_model() -> str | OpenAIChatCompletionsModel:
    """Return the configured model for the Agents SDK.

    With no base URL, the SDK uses its normal OpenAI provider. Setting
    OPENAI_BASE_URL switches to any server that implements the OpenAI chat
    completions interface.
    """

    model_name = os.getenv("RESEARCH_ASSISTANT_MODEL", DEFAULT_MODEL)
    base_url = os.getenv("OPENAI_BASE_URL")

    if not base_url:
        return model_name

    # A local or third-party server cannot receive OpenAI trace exports.
    set_tracing_disabled(True)
    client = AsyncOpenAI(
        base_url=base_url,
        api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
    )
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=client,
    )

