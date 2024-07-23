from typing import Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_fireworks import ChatFireworks

def construct_anthropic(model_name: str, extra_flags: Dict[str, str] | None) -> BaseChatModel:
    return ChatAnthropic(model_name=model_name, default_headers=extra_flags)

def construct_openai(model_name: str, extra_flags: Dict[str, str] | None) -> BaseChatModel:
    return ChatOpenAI(model_name=model_name, default_headers=extra_flags)

def construct_ollama(model_name: str, extra_flags: Dict[str, str] | None) -> BaseChatModel:
    return ChatOllama(model=model_name)

def construct_fireworks(model_name: str, extra_flags: Dict[str, str] | None) -> BaseChatModel:
    return ChatFireworks(model=model_name, default_headers=extra_flags)

registry: Dict[str, BaseChatModel] = {
    "anthropic": construct_anthropic,
    "openai": construct_openai,
    "ollama": construct_ollama,
    "fireworks": construct_fireworks,
}
