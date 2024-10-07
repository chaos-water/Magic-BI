from loguru import logger
from fastapi import APIRouter, Request

from magic_bi.utils.globals import GLOBALS
from magic_bi.utils.utils import get_http_rsp
from magic_bi.data.dataset import Dataset
from magic_bi.data.dataset_manager import DatasetManager

dataset_router = APIRouter()

DATASET_MANAGER = DatasetManager(globals=GLOBALS)

url_prefix = "magic_bi"

def create_dataset_router(prefix: str):
    dataset_router = APIRouter(prefix=prefix)

    @dataset_router.post("/dataset/add")
    def add_dataset(body: dict):
        dataset: Dataset = Dataset()
        dataset.from_dict(body)

        ret = DATASET_MANAGER.add(dataset)
        if ret == 0:
            logger.debug("add_dataset suc, data_id:%s" % dataset.id)
            return get_http_rsp(data={"id": dataset.id})
        else:
            logger.error("add_dataset suc, input_body:%s" % body)
            return get_http_rsp(code=-1, msg="failed")

    @dataset_router.post("/dataset/delete")
    def delete_dataset(body: dict):
        dataset: Dataset = Dataset()
        dataset.from_dict(body)

        ret = DATASET_MANAGER.delete(dataset)
        if ret == 0:
            logger.debug("delete_dataset suc, data_id:%s" % dataset.id)
            return get_http_rsp()
        else:
            logger.error("delete_dataset failed, data_id:%s" % dataset.id)
            return get_http_rsp(code=ret, msg="failed")


    @dataset_router.post("/dataset/get")
    def get_dataset(request: Request, body: dict):
        user_id = request.headers.get("user_id")

        dataset_list = DATASET_MANAGER.get(user_id)
        dataset_count = DATASET_MANAGER.count(user_id)
        if dataset_list is None:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")
        else:
            logger.debug("get suc")
            return get_http_rsp(data={"dataset_list": [ dataset.to_dict() for dataset in dataset_list ], "total_count": dataset_count})


    return dataset_router