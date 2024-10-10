from loguru import logger
from fastapi import APIRouter, Request
from fastapi import File, UploadFile, Form

from typing import Dict
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
from magic_bi.data.data_manager import DataManager
from magic_bi.data.data import Data

DATA_MANAGER = DataManager(globals=GLOBALS, language_name=GLOBAL_CONFIG.language_config.get_language_name())


def create_data_router(prefix: str):
    data_router = APIRouter(prefix=prefix)

    @data_router.post("/data/add_file")
    def add_file(request: Request, file = File(), dataset_id = Form()):
        data: Data = Data()
        data.dataset_id = dataset_id
        data.user_id = request.headers.get("user_id", "default")
        data.from_upload_file(file)
        ret = DATA_MANAGER.add(data)

        if ret == 0:
            logger.debug("add_file suc, data_id:%s" % data.id)
            return get_http_rsp(data={"id": data.id})
        else:
            logger.error("add_file failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_router.post("/data/delete")
    def delete_data(body: Dict):
        data: Data = Data()
        data.from_dict(body)

        ret = DATA_MANAGER.delete(data)
        if ret == 0:
            logger.debug("delete suc, data_id:%s" % data.id)
            return get_http_rsp()
        else:
            logger.error("delete failed, data_id:%s" % data.id)
            return get_http_rsp(code=ret, msg="failed")

    @data_router.post("/data/get")
    def get_data(request: Request, body: Dict):
        user_id = request.headers.get("user_id", "default")
        
        dataset_id = body.get("dataset_id")
        page_index = int(body.get("page_index", 1))
        page_size = int(body.get("page_size", 10))

        data_list = DATA_MANAGER.get(user_id, dataset_id, page_index, page_size)
        total_count = DATA_MANAGER.count(user_id, dataset_id)

        if data_list is not None:
            logger.debug("get suc")
            return get_http_rsp(data={"data_list": [ data.to_dict() for data in data_list ], "total_count": total_count})
        else:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_router.post("/data/download")
    def download_data(body: Dict):

        data_id = body.get("id")
        data_list = DATA_MANAGER.get(data_id)

        if data_list is not None:
            logger.debug("get suc")
            return get_http_rsp(data=[ data.to_dict() for data in data_list ])
        else:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_router.post("/data/segment")
    # @data_router.post("/%s/data/segment" % "magic_bi")
    def segment_doc(file: UploadFile = File()):
        file_bytes = file.file.read()
        file_name = file.filename
        from magic_bi.doc.decode_doc import decode_doc

        chunk_list = decode_doc(file_name, file_bytes, text_embedding=GLOBALS.text_embedding)

        logger.debug("segment_doc suc, chunk_list_cnt:%d" % len(chunk_list))
        return get_http_rsp(data=chunk_list)


    return data_router


