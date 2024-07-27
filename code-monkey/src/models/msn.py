from typing import Tuple, Dict
from langchain_core.language_models.chat_models import BaseChatModel

from .registry import registry

# MSN is simile to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
# a model name/variant, and any extra flags.
#
# syntax is: service[/model[/flags]]
# where flags is a comma separated list of key=value pairs
def parse_msn(msn: str | None) -> Tuple[BaseChatModel, str | None, Dict[str, str] | None]:
    if msn is None:
        # our default
        msn = "anthropic"
    
    split_msn = msn.split("/")
    split_len = len(split_msn)

    if split_msn[0] not in registry:
        raise ValueError(f"Unknown model service: {split_msn[0]}")

    ModelServiceClass = registry[split_msn[0]]
    model_name = None
    flags_dict = None

    if split_len >= 2:
        model_name = split_msn[1]

    if split_len >= 3:
        flags = split_msn[2]

        # parse flags (which will be a , separated list of k=v) into a dict
        flags_dict = dict([ flag.split("=") for flag in flags.split(",") ])

    return (ModelServiceClass, model_name, flags_dict)
