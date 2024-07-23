from typing import Dict
from .model import Model, ModelName
from .msn import parse_msn

registry: Dict[str, Model] = {}

def register_model_service(model_name: str, Service: Model):
    global registry

    if model_name in registry:
        raise Exception(f"Model {model_name} already registered")
    
    registry[model_name] = Service

def get_model_service(msn: str | None) -> Model:
    # default if no msn provided is Anthropic
    if msn is None:
        return registry[ModelName.Anthropic]
    
    [ service, _, _ ] = parse_msn(msn)

    if service not in registry:
        raise Exception(f"Unknown model service: '{service}'")

    return registry[service]
