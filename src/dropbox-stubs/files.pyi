from typing import Literal

class WriteMode:
    def __init__(self, tag: Literal["add", "overwrite", "update"]) -> None: ...
