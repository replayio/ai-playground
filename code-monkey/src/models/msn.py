from dataclasses import dataclass
from typing import Dict, Self
from langchain_core.language_models.chat_models import BaseChatModel

from .registry import get_model_service_ctor, ChatModelConstructor

# MSN is simile to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
# a model name/variant, and any extra flags.
#
# syntax is: service[/model[/flags]]
#
# where flags is a comma separated list of key[=value] pairs.  'key' on its own
# is treated as a boolean True flag.


@dataclass
class MSN:
    chat_model_ctor: ChatModelConstructor
    model_name: str | None
    flags: Dict[str, str | bool] | None

    @classmethod
    def from_string(cls, msn_str: str | None) -> Self:
        if msn_str is None:
            # our default
            msn_str = "anthropic/"

        split_msn = msn_str.split("/")

        chat_model_ctor = get_model_service_ctor(split_msn[0])
        model_name = split_msn[1] if len(split_msn) >= 2 else ""
        flags = parse_flags(split_msn[2]) if len(split_msn) >= 3 else None

        return cls(chat_model_ctor, model_name, flags)

    def construct_model(self) -> BaseChatModel:
        return self.chat_model_ctor(model_name=self.model_name, extra_flags=self.flags)


def parse_flags(flags: str) -> Dict[str, str | bool]:
    # parse the flags into a dict based on k=v pairs (split on the first `=`.).
    # if there's no '=', v will be True
    flags_dict = {}
    for flag in flags.split(","):
        k, v = flag.split("=", 1)
        flags_dict[k] = v if v else True
    return flags_dict
