import os
from tools.utils import (
    ask_user,
    show_diff,
)
from constants import get_src_dir, get_artifacts_dir
from models import Model, get_model_service
from .base_agent import BaseAgent
from instrumentation import current_span, instrument

class Agent(BaseAgent):
    model: Model

    def __init__(self, msn: str | None):
        # TODO(toshok) these two steps should be collapsed and hidden back in the
        # models/ directory (and replaced with something like this here:
        #   self.model = construct_model(msn, self)
        Service = get_model_service(msn)
        self.model = Service(self, msn)

    # Custom Agent initialization goes here, when necessary.
    def initialize(self):
        pass

    def run_prompt(self, prompt: str):
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Running prompt: {prompt}")
        result = self.model.run_prompt(prompt)
        logger.debug(f"Prompt result: {result}")
        return result

    @instrument("Agent.handle_completion")
    def handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        current_span().set_attributes({
            "had_any_text": had_any_text,
            "num_modified_files": len(modified_files),
            "modified_files": str(modified_files)
        })

        if not had_any_text:
            print("Done.")

        if modified_files:
            print(f"Modified files: {', '.join(modified_files)}")
            for file in modified_files:
                self._handle_modified_file(file)
        return True

    @instrument("Agent._handle_modified_file")
    def _handle_modified_file(self, file: str) -> None:
        span = current_span()

        span.set_attribute("file", file)

        original_file = os.path.join(get_src_dir(), file)
        modified_file = os.path.join(get_artifacts_dir(), file)
        show_diff(original_file, modified_file)
        apply_changes = ask_user(
            f"Do you want to apply the changes to {file} (diff shown in VSCode)? (Y/n): "
        ).lower()
        if apply_changes == "y" or apply_changes == "":
            span.set_attribute("apply_changes", True)
            self._apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            span.set_attribute("apply_changes", False)
            print(f"❌ Changes not applied to {file}")

    @instrument("Agent._apply_changes")
    def _apply_changes(self, original_file: str, modified_file: str) -> None:
        current_span().set_attributes({
            "original_file": original_file,
            "modified_file": modified_file,
        })
        # TODO(toshok) we probably want the before/after size?  or something about size of the diff
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())