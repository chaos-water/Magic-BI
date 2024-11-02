from loguru import logger
from fastapi import APIRouter, Request, Query
from fastapi import File, Form
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from urllib.parse import quote


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
from magic_bi.train.pro.few_shot_train_data_generator import FewShotTrainDataGenerator
from magic_bi.train.pro.zero_shot_train_data_generator import ZeroShotTrainDataGenerator

TRAIN_MANAGER = TrainManager(global_config=GLOBAL_CONFIG, globals=GLOBALS)

def create_train_router(prefix: str):
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

    @train_router.post("/train/data/get")
    def generate_train_data(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")

        train_data_list = TRAIN_MANAGER.get_train_data(user_id)
        logger.debug("generate_train_data suc, user_id:%s" % user_id)
        return get_http_rsp(data=train_data_list)

    @train_router.get("/train/data/export")
    def export_data(id = Query(..., description="Train data ID"),
                    file_type=Query(..., description="file type, excel or json"),
                    valid_filter = Query(..., description="Valid state filter")):
        if not id or not file_type or not valid_filter or file_type.lower() not in ["excel", "json"] or valid_filter not in ["valid", "invalid"]:
            raise HTTPException(status_code=400, detail="Train data ID is required")

        data_to_export = []
        train_data: TrainData = TRAIN_MANAGER.get_train_data_by_id(id)
        if file_type.lower() == "excel":
            file_name = train_data.name + ".xlsx"
            train_orginal_item_list: list[TrainDataOriginalItem]  = TRAIN_MANAGER.get_train_data_original_item(train_data_id=id, valid_filter_flag=valid_filter)
            if train_orginal_item_list != []:
                for train_original_item in train_orginal_item_list:
                    data_to_export.append([train_original_item.input, train_original_item.output])

                excel_file_bytes: bytes = generate_excel_file("Sheet1", ["问题", "sql"], data_to_export)
            else:
                excel_file_bytes = "".encode()

            file_stream = BytesIO(excel_file_bytes)

        elif file_type.lower() == "json":
            # 这段代码有个问题，json_str是正确的json数据。但是浏览器下载时，得到的文件是空的。请分析和解决。
            file_name = train_data.name + ".json"
            train_prompted_item_list: list[TrainDataPromptedItem]  = TRAIN_MANAGER.get_train_data_prompted_item(train_data_id=id)

            for train_prompted_item in train_prompted_item_list:
                data_to_export.append({"instruction": train_prompted_item.instruction, "input": train_prompted_item.input,
                                       "output": train_prompted_item.output})

            file_stream = BytesIO()
            json_str = json.dumps(data_to_export, ensure_ascii=False, indent=4)
            file_stream.write(json_str.encode('utf-8'))
            file_stream.seek(0)

            return StreamingResponse(file_stream, media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
            })

        try:
            return StreamingResponse(file_stream, media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
            })

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error exporting model: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @train_router.post("/train/data/generate/resume")
    def resume_generate_train_data(request: Request, body: dict):
        try:
            train_data_id = body["train_data_id"]

            mq_msg: MqMsg = MqMsg()
            mq_msg.msg_json = body

            mq_msg.msg_type = MQ_MSG_TYPE.RESUME_GENERATE_TRAIN_DATA.value

            ret = GLOBALS.rabbitmq_producer.produce(GLOBAL_CONFIG.rabbitmq_config.internal_mq_queue,
                                                    mq_msg.to_json_str())
            if ret == 0:
                logger.debug(f"resume_generate_train_data suc")
                return get_http_rsp()
            else:
                logger.error(f"resume_generate_train_data failed, body:{body}")
                return get_http_rsp(code=-1, msg="failed")

        except Exception as e:
            logger.error(f"catch exception:{str(e)}")
            logger.error(f"resume_generate_train_data failed, body:{body}")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/data/generate/start")
    def start_generate_train_data(request: Request, body: dict):
        try:
            mq_msg: MqMsg = MqMsg()
            generate_method = body["generate_method"]
            body["user_id"] = request.headers.get("user_id", "default")

            mq_msg.msg_type = MQ_MSG_TYPE.START_GENERATE_TRAIN_DATA.value
            if generate_method == TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION.value:
                if FewShotTrainDataGenerator.is_start_json_para_legal(body) is False:
                    logger.error(f"start_generate_train_data failed, para {body} illegal")
                    return get_http_rsp(code=-1, msg="failed")

            elif generate_method == TRAIN_DATA_GENERATE_METHOD.FEW_SHOT.value:
                if FewShotTrainDataGenerator.is_start_json_para_legal(body) is False:
                    logger.error(f"start_generate_train_data failed, para {body} illegal")
                    return get_http_rsp(code=-1, msg="failed")

            elif generate_method == TRAIN_DATA_GENERATE_METHOD.ZERO_SHOT.value:
                if ZeroShotTrainDataGenerator.is_start_json_para_legal(body) is False:
                    logger.error(f"start_generate_train_data failed, para {body} illegal")
                    return get_http_rsp(code=-1, msg="failed")

            else:
                logger.error(f"start_generate_train_data failed, unsupported generator method: {generate_method}")
                return get_http_rsp(code=-1, msg="failed")

            mq_msg.msg_json = body
            ret = GLOBALS.rabbitmq_producer.produce(GLOBAL_CONFIG.rabbitmq_config.internal_mq_queue, mq_msg.to_json_str())
            if ret == 0:
                logger.debug(f"start_generate_train_data suc")
                return get_http_rsp()
            else:
                logger.error(f"start_generate_train_data failed, body:{body}")
                return get_http_rsp(code=-1, msg="failed")

        except Exception as e:
            logger.error(f"catch exception:{str(e)}")
            logger.error(f"start_generate_train_data failed, body:{body}")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/model/add")
    def add_model(request: Request, body: dict):
        domain_model: DomainModel = DomainModel()
        domain_model.from_dict(body)
        domain_model.user_id = request.headers.get("user_id", "default")

        ret = TRAIN_MANAGER.add_model(domain_model)
        if ret == 0:
            logger.debug("add_model suc")
            return get_http_rsp(data={"id": domain_model.id})
        else:
            logger.error("add_model failed")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/model/get")
    def get_model(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")
        train_model_list = TRAIN_MANAGER.get_domain_model(user_id)

        logger.debug("get_model suc")
        return get_http_rsp(data=train_model_list)

    @train_router.post("/train/model/delete")
    def delete_model(body: dict):
        try:
            train_model_id = body["train_model_id"]
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("delete_model failed")
            return get_http_rsp(code=-1, msg="failed")

        ret = TRAIN_MANAGER.delete_model(train_model_id)
        if ret == 0:
            logger.debug("delete_model suc")
            return get_http_rsp()
        else:
            logger.error("delete_model failed")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/model/train")
    def train_model(body: dict):
        try:
            mq_msg: MqMsg = MqMsg()
            mq_msg.msg_type = MQ_MSG_TYPE.TRAIN_MODEL.value
            ret = GLOBALS.rabbitmq_producer.produce(GLOBAL_CONFIG.rabbitmq_config.internal_mq_queue, json.dumps(body))

            if ret == 0:
                logger.debug("train_model suc")
                return get_http_rsp()
            else:
                logger.error("train_model failed")
                return get_http_rsp(code=-1, msg="failed")
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("train_model failed")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.post("/train/model/deploy")
    def deploy_model(body: dict):
        try:
            mq_msg: MqMsg = MqMsg()
            mq_msg.msg_type = MQ_MSG_TYPE.DEPLOY_MODEL.value
            ret = GLOBALS.rabbitmq_producer.produce(GLOBAL_CONFIG.rabbitmq_config.internal_mq_queue, json.dumps(body))

            if ret == 0:
                logger.debug("deploy_model suc")
                return get_http_rsp()
            else:
                logger.error("deploy_model failed")
                return get_http_rsp(code=-1, msg="failed")
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("deploy_model failed")
            return get_http_rsp(code=-1, msg="failed")

    @train_router.get("/train/model/export")
    def export_model(id = Query(..., description="Domain model ID")):
        if not id:
            raise HTTPException(status_code=400, detail="Domain model ID is required")

        domain_model: DomainModel = TRAIN_MANAGER.get_domain_model_by_id(id)
        if domain_model is None:
            raise HTTPException(status_code=400, detail="Domain model ID not found")
        bucket_name = "default"

        try:
            file_stream = GLOBALS.oss_factory.stream_file(bucket_name, id)
            file_name = f"{domain_model.name}.zip"

            return StreamingResponse(file_stream, media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
            })

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error exporting model: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return train_router
