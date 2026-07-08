from functools import lru_cache

from openai import OpenAI, OpenAIError


class SummarizationError(Exception):
    """Raised when the summarization request to OpenAI fails."""


INSTRUCTIONS = (
    "You are a summarization engine, not a conversational assistant. The user message contains the complete text "
    "to summarize; it may be an article, a fragment, or a list of items such as headlines. Never ask for more "
    "content and never remark on the text's length or format. If the text is a list of headlines or topics, "
    "describe the overall themes without inventing details that are not present in the text. Respond with only "
    "the summary, as one short paragraph."
)


@lru_cache(maxsize=4)
def _get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def summarize_text(text: str, api_key: str) -> str:
    client = _get_client(api_key)

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=INSTRUCTIONS,
            input=text,
        )

    except OpenAIError as exc:
        raise SummarizationError(str(exc)) from exc

    return response.output_text
