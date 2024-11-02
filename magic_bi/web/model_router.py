from loguru import logger
from fastapi import APIRouter, Request, Query
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote


from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
from magic_bi.train.train_manager import TrainManager
from magic_bi.train.entity.domain_model import DomainModel
import json
from magic_bi.mq.mq_msg import MqMsg, MQ_MSG_TYPE

TRAIN_MANAGER = TrainManager(global_config=GLOBAL_CONFIG, globals=GLOBALS)

def create_train_model_router(prefix: str):
    train_router = APIRouter(prefix=prefix)

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
            from magic_bi.train.model_trainer import ModelTrainer
            if ModelTrainer.is_json_para_legal(body) is True:
                mq_msg: MqMsg = MqMsg()
                mq_msg.msg_type = MQ_MSG_TYPE.TRAIN_MODEL.value
                mq_msg.msg_json = body
                ret = GLOBALS.rabbitmq_producer.produce(GLOBAL_CONFIG.rabbitmq_config.internal_mq_queue, mq_msg.to_json_str())

                if ret == 0:
                    logger.debug("train_model suc")
                    return get_http_rsp()
                else:
                    logger.error("train_model failed")
                    return get_http_rsp(code=-1, msg="failed")
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
