from typing import Dict, Callable
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_fireworks import ChatFireworks

type ChatModelConstructor = Callable[[str, Dict[str, str]], BaseChatModel]


def construct_anthropic(model_name: str, extra_flags: Dict[str, str]) -> BaseChatModel:
    return ChatAnthropic(
        model_name=model_name,
        default_headers=extra_flags,
        # for some reason these don't have default values in ChatAnthropic.__init__
        timeout=None,
        stop=None,
        base_url=None,
        api_key=None,
    )


def construct_openai(model_name: str, extra_flags: Dict[str, str]) -> BaseChatModel:
    return ChatOpenAI(name=model_name, default_headers=extra_flags)

def construct_ollama(model_name: str, extra_flags: Dict[str, str]) -> BaseChatModel:
    return ChatOllama(model=model_name)


def construct_fireworks(model_name: str, extra_flags: Dict[str, str]) -> BaseChatModel:
    return ChatFireworks(
        model=model_name,
        # no default value for this one
        stop_sequences=None,
    )


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
