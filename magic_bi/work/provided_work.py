
from loguru import logger
from caseconverter import pascalcase, snakecase

from magic_bi.work.work import Work

provided_work: dict[str, Work] = {}


def get_all_provided_work_info() -> str:
    output_str = ""
    for work_name, work_intro in provided_work.items():
        work_info_row_str = "\t%s | %s\n" % (work_name, work_intro)
        output_str += work_info_row_str

    logger.debug("output_str:\n%s" % output_str)
    return output_str


def get_work(work_name: str):
    from magic_bi.utils.globals import GLOBAL_CONFIG
    try:
        work_class_name: str = pascalcase(work_name.strip("<").strip(">")) + "Work"
        work_file_name: str = f"{GLOBAL_CONFIG.system_config.url_prefix}.work." + snakecase(work_name.strip("<").strip(">")) + "_work"
        tmp_name = __import__(work_file_name)
        work_python_module = eval(work_file_name)
        work_class = getattr(work_python_module, work_class_name)
        work_obj = work_class()

        logger.debug("get_work suc, work_name:%s" % work_name)
        return work_obj

    except Exception as e:
        logger.error("get_work failed, catch exception:%s, work_name:%s" % (str(e), work_name))
        return None

def register_work():
    provided_work["InterpretImage"] = "interpret image"
    provided_work["SearchRelevantContentWork"] = "search_relevant_content_work"

    logger.debug("register_work suc, provided_work_cnt:%d" % len(provided_work))
    return 0
