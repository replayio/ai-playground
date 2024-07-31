from typing import Dict, Callable
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_fireworks import ChatFireworks

type ChatModelConstructor = Callable[
    [str, Dict[str | None, str | bool] | None], BaseChatModel
]


def construct_anthropic(
    model_name: str, extra_flags: Dict[str | None, str | bool] | None
) -> BaseChatModel:
    if not model_name:
        model_name = "claude-3-5-sonnet-20240620"
    return ChatAnthropic(model_name=model_name, default_headers=extra_flags)


def construct_openai(
    model_name: str, extra_flags: Dict[str | None, str | bool] | None
) -> BaseChatModel:
    raise Exception("TODO(toshok): add model")
    return ChatOpenAI(model_name=model_name, default_headers=extra_flags)


def construct_ollama(
    model_name: str, extra_flags: Dict[str | None, str | bool] | None
) -> BaseChatModel:
    return ChatOllama(model=model_name)


def construct_fireworks(
    model_name: str, extra_flags: Dict[str, str] | None
) -> BaseChatModel:
    return ChatFireworks(model=model_name, default_headers=extra_flags)


registry: Dict[str, ChatModelConstructor] = {
    "anthropic": construct_anthropic,
    "openai": construct_openai,
    "ollama": construct_ollama,
    "fireworks": construct_fireworks,
}


def get_model_service_ctor(model_service: str) -> ChatModelConstructor:
    if model_service not in registry:
        raise ValueError(f"Unknown model service: {model_service}")
    return registry[model_service]
