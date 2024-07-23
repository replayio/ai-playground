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

    if split_msn[0] not in registry:
        raise ValueError(f"Unknown model service: {split_msn[0]}")

    if len(split_msn) == 1:
        return (registry[split_msn[0]], None, None)
    
    if len(split_msn) == 2:
        return (registry[split_msn[0]], split_msn[1], None)
    
    # split_msn length >= 3
    flags = split_msn[2]

    # parse flags (which will be a , separated list of k=v) into a dict
    flags_dict = dict([ flag.split("=") for flag in flags.split(",") ])
    return (registry[split_msn[0]], split_msn[1], flags_dict)
