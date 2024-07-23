from tools.tool import Tool
from deps.ASTParser import ASTParser

class CATool(Tool):
    parser: ASTParser

    def __init__(self):
        super().__init__()
        self.parser = ASTParser()
