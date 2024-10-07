from queue import Queue
from loguru import logger

from magic_bi.io.base_io import BaseIo


class InputOutputIo(BaseIo):
    def __init__(self):
        self._input_queue: Queue = Queue(maxsize=10)
        self._output_queue: Queue = Queue(maxsize=10)

    def person_input(self, content: str):
        self._input_queue.put(content)

    def person_outout(self) -> str:
        return self._output_queue.get()

    def input(self) -> str:
        content = self._input_queue.get()

        logger.debug("_user_input suc, input:%s" % content)
        return content

    def output(self, content: str):
        self._output_queue.put(content)

        logger.debug("_magic_assistant_output suc, input:%s" % content)
        return 0

