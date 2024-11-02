from loguru import logger


from magic_bi.work.base_work import BaseWork
from magic_bi.utils.globals import GLOBALS
from magic_bi.utils.utils import base64_to_image_bytes
from magic_bi.work.work import WorkInput, WorkOutput


class InterpretImageWork(BaseWork):
    def __init__(self):
        pass

    def execute(self, work_input: WorkInput) -> WorkOutput:
        image_base64 = work_input.file_base64_list[0]
        # image_bytes = base64_to_image_bytes(image_base64)

        ret = GLOBALS.mllm_adapter.process(work_input.text_content, image_base64)

        work_output: WorkOutput = WorkOutput()
        work_output.data = ret

        logger.debug("DescribeImageWork execute suc")
        return work_output
