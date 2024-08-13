from dataclasses import dataclass
from typing import Dict, Self
from langchain_core.language_models.chat_models import BaseChatModel

from .registry import get_model_service_ctor, ChatModelConstructor


# MSN is simile to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
# a model name/variant, and any extra flags.
#
# syntax is: service[/model[/flags]]
#
# where flags is a comma separated list of key=value pairs
@dataclass
class MSN:
    chat_model_ctor: ChatModelConstructor
    model_name: str
    flags: Dict[str, str]

    @classmethod
    def from_string(cls, msn_str: str) -> Self:
        split_msn = msn_str.split("/", 2)
        split_len = len(split_msn)

        if split_len < 2:
            raise ValueError(
                f"MSN must have at least a service and model name: {msn_str}"
            )

        chat_model_ctor = get_model_service_ctor(split_msn[0])
        model_name = split_msn[1]
        flags = parse_flags(split_msn[2], msn_str) if len(split_msn) >= 3 else {}

        return cls(chat_model_ctor, model_name, flags)

    def construct_model(self) -> BaseChatModel:
        return self.chat_model_ctor(self.model_name, self.flags)


def parse_flags(flags: str, source_msn_str: str) -> Dict[str, str]:
    # parse the flags into a dict based on k=v pairs (split on the first `=`.).
    flags_dict = {}
    for flag in flags.split(","):
        k, v = flag.split("=", 1)
        if v is None:
            raise ValueError(f"MSN flag {k} must have a value: {source_msn_str}")
    return flags_dict
