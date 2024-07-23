from typing import Tuple
from .model import ModelName

# MSN is simile to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
# a model name/variant, and any extra flags.
#
# syntax is: service[/model[/flags]]
# where flags is a comma separated list of key=value pairs

def parse_msn(msn: str | None) -> Tuple[str, str | None, str | None]:
    if msn is None:
        return (ModelName.Anthropic, None, None)
    
    split_msn = msn.split("/")
    if len(split_msn) == 1:
        return (split_msn[0], None, None)
    
    if len(split_msn) == 2:
        return (split_msn[0], split_msn[1], None)
    
    # split_msn length >= 3
    flags = split_msn[2]

    # parse flags (which will be a , separated list of k=v) into a dict
    flags_dict = dict([ flag.split("=") for flag in flags.split(",") ])
    return (split_msn[0], split_msn[1], flags_dict)
