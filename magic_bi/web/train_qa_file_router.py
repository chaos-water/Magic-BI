from loguru import logger
from fastapi import APIRouter, Request, Query
from fastapi import File, Form
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from urllib.parse import quote



from magic_bi.mq.mq_msg import MqMsg, MQ_MSG_TYPE
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
from magic_bi.train.train_manager import TrainManager
from magic_bi.train.entity.train_data import TrainData
from magic_bi.train.entity.train_qa_file import TrainQaFile
from magic_bi.train.entity.domain_model import DomainModel
from magic_bi.utils.utils import generate_excel_file
import json
from magic_bi.train.entity.train_data_original_item import TrainDataOriginalItem
from magic_bi.train.entity.train_data_prompted_item import TrainDataPromptedItem
from magic_bi.train.train_data_type import TRAIN_DATA_GENERATE_METHOD
from magic_bi.mq.mq_msg import MqMsg, MQ_MSG_TYPE
from magic_bi.train.pure_conversion_train_data_generator import PureConversionTrainDataGenerator
from magic_bi.train.pro.few_shot_train_data_generator import FewShotTrainDataGenerator
from magic_bi.train.pro.zero_shot_train_data_generator import ZeroShotTrainDataGenerator

TRAIN_MANAGER = TrainManager(global_config=GLOBAL_CONFIG, globals=GLOBALS)

def create_train_qa_file_router(prefix: str):
    train_router = APIRouter(prefix=prefix)

    @train_router.post("/train/qa_file/import")
    def import_qa_file(request: Request, file = File()):
        train_qa_file: TrainQaFile = TrainQaFile()
        train_qa_file.from_upload_file(file)
        train_qa_file.user_id = request.headers.get("user_id", "default")

        train_qa_file_id = TRAIN_MANAGER.import_qa_file(train_qa_file)
        if train_qa_file_id != "":
            logger.debug(f"import_qa_file suc, train_qa_file_id:{train_qa_file_id}")
            return get_http_rsp(data={"id": train_qa_file_id})
        else:
            logger.error("import_qa_file failed")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/qa_file/get")
    def get_qa_file(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")

        train_qa_file_list = TRAIN_MANAGER.get_train_qa_file(user_id)

        logger.debug("get_qa_file suc, train_qa_file_list cnt:%d" % len(train_qa_file_list))
        return get_http_rsp(data=train_qa_file_list)

    @train_router.post("/train/qa_file/delete")
    def delete_qa_file(request: Request, body: dict):
        try:
            train_qa_file_id: str = body["id"]
            ret = TRAIN_MANAGER.delete_train_qa_file(train_qa_file_id)
            if ret == 0:
                logger.debug("delete_qa_file suc, id:%s" % train_qa_file_id)
                return get_http_rsp()
            else:
                logger.error("delete_qa_file failed")
                return get_http_rsp(code=-1, msg="failed")

        except Exception as e:
            logger.error("catch exeption: %s" % str(e))
            logger.error("delete_qa_file failed")
            return get_http_rsp(code=-1, msg="failed")

    return train_router
