from os import environ

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

load_dotenv()

OPENAI_GENERATOR_MODEL: str = environ['OPENAI_GENERATOR_MODEL']
OPENAI_REVIEWER_MODEL: str = environ['OPENAI_REVIEWER_MODEL']

api_key = environ['OPENAI_API_KEY']
if api_key is None:
    raise ValueError('OpenAI API key is required.')
_openai_llm: OpenAI = \
    OpenAI(
        api_key=api_key,
        base_url=environ['OPENAI_BASE_URL'],
    )


def prompt_openai(
    system_prompt: str,
    user_prompt: str,
    temperature: float | int = 0.0,
    max_tokens: int = 2048,
) -> str | None:
    response = \
        _openai_llm \
            .chat \
            .completions \
            .create(
            model=OPENAI_GENERATOR_MODEL,
            messages=[
                ChatCompletionSystemMessageParam(role='system', content=system_prompt),
                ChatCompletionUserMessageParam(role='user', content=user_prompt),
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        ).choices[0] \
            .message \
            .content
    return response.strip() \
        if response is not None \
        else None
