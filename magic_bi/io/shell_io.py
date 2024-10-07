from loguru import logger
from rich.console import Console

from magic_bi.io.base_io import BaseIo


class ShellIo(BaseIo):
    def __init__(self):
        self._console: Console = Console()

    def input(self) -> str:
        role = "USER"
        person_input = self._console.input(f"[bold]{role}: ")

        logger.debug("_user_input suc, input:%s" % person_input)
        return person_input

    def output(self, content: str):
        role = "MAGIC_ASSISTANT"
        self._console.print(f"[bold]{role}:")
        self._console.print(f"{content}")

        logger.debug("_magic_assistant_output suc, input:%s" % input)
        return 0
