# 这段代码中，我希望，如果是中文，就返回中文的错误msg；如果是英文，就返回英文的错误msg，可以如何实现？
from enum import Enum
from magic_bi.utils.globals import GLOBAL_CONFIG

class ERROR_CODE(Enum):
    SUC = 0
    UNKNOWN_ERROR = -1
    DUPLICATE_ADD = -2
    DATA_SOURCE_NOT_EXISTED = -3

ERROR_MSG = {
    "zh": {
         0: "suc",
        -1: "系统错误",
        -2: "重复添加",
        -3: "数据源不存在",
    },
    "en": {
         0: "suc",
        -1: "system error",
        -2: "duplicate add",
        -3: "data source not existed",
    },
}

def get_error_message(error_code: ERROR_CODE) -> str:
    return ERROR_MSG.get(GLOBAL_CONFIG.language_config.language_code, {}).get(error_code.value, -1)