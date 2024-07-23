from typing import Any, Optional
from langchain_core.tools import BaseTool
from deps import ASTParser

class CATool(BaseTool):
    parser: Optional[ASTParser] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.parser is None:
            self.parser = ASTParser()
