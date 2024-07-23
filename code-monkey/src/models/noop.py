from agents.base_agent import BaseAgent
from instrumentation import instrument
from .model import Model, ModelName
from .registry import register_model_service

class NoopModel(Model):
    name = ModelName.Noop

    @instrument("Model.__init__", attributes={"model": "Noop"})
    def __init__(self, agent: BaseAgent) -> None:
        self.agent = agent
        super().__init__()

    @instrument("Model.run_prompt", attributes={"model": "Noop"})
    def run_prompt(self, prompt: str) -> str:
        # Noop model just returns the prompt as is.
        return prompt

register_model_service(ModelName.Noop, NoopModel)
