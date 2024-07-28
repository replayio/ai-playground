from typing import Any
from langchain_core.tools import BaseTool
from deps import ASTParser


class CATool(BaseTool):
    parser: ASTParser

    def __init__(self, **kwargs: Any):
        if "parser" not in kwargs:
            kwargs["parser"] = ASTParser()
        super().__init__(**kwargs)
