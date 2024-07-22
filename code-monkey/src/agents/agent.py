import os
from tools.utils import (
    ask_user,
    show_diff,
    artifacts_dir,
)
from constants import src_dir
from models import Model, Claude
from .base_agent import BaseAgent


class Agent(BaseAgent):
    model: Model

    def __init__(self):
        self.model = Claude(self)

    # Custom Agent initialization goes here, when necessary.
    def initialize(self):
        pass

    def run_prompt(self, prompt: str):
        return self.model.run_prompt(prompt)

    def handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        if not had_any_text:
            print("Done.")

        if modified_files:
            print(f"Modified files: {', '.join(modified_files)}")
            for file in modified_files:
                self._handle_modified_file(file)
        return True

    def _handle_modified_file(self, file: str) -> None:
        original_file = os.path.join(src_dir, file)
        modified_file = os.path.join(artifacts_dir, file)
        show_diff(original_file, modified_file)
        apply_changes = ask_user(
            f"Do you want to apply the changes to {file} (diff shown in VSCode)? (Y/n): "
        ).lower()
        if apply_changes == "y" or apply_changes == "":
            self._apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            print(f"❌ Changes not applied to {file}")

    def _apply_changes(self, original_file: str, modified_file: str) -> None:
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())
