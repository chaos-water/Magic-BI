from loguru import logger
from fastapi import APIRouter
from typing import Dict

from magic_bi.user import User
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp

from magic_bi.graphrag.graphrag_manager import GraphRagManager
GRAPH_RAG_MANAGER = GraphRagManager()

user_router = APIRouter()
# url_prefix = "magic_bi"
url_prefix = GLOBAL_CONFIG.web_config.url_prefix

@user_router.post("/%s/graphrag/generate_schema" % url_prefix)
def generate_schema(body: Dict):
    user_name = body.get("user_name")

    user: User = User()
    user.user_name = user_name


    session = GLOBALS.sql_orm.get_session()
    session.add(user)
    session.commit()

    logger.debug("add_user suc")
    return get_http_rsp(data={"user_id": user.user_id})

@user_router.post("/%s/graphrag/create_schema" % url_prefix)
def update_graphrag_schema(body: Dict):
    user_id = body.get("user_id")

    session = GLOBALS.sql_orm.get_session()
    user: User = session.query(User).filter(User.user_id == user_id).first()
    if user is None:
        logger.error("delete_user suc")
        return get_http_rsp(code=-1, msg="failed")

    session.delete(user)

    logger.debug("delete_user suc")
    return get_http_rsp()

@user_router.post("/%s/graphrag/update_schema" % url_prefix)
def update_graphrag_schema(body: Dict):
    user_id = body.get("user_id")

    session = GLOBALS.sql_orm.get_session()
    user: User = session.query(User).filter(User.user_id == user_id).first()
    if user is None:
        logger.error("delete_user suc")
        return get_http_rsp(code=-1, msg="failed")

    session.delete(user)

    logger.debug("delete_user suc")
    return get_http_rsp()

@user_router.post("/%s/graphrag/create"
                  "" % url_prefix)
def create_graphrag(body: Dict):
    user_list = []

    session = GLOBALS.sql_orm.get_session()
    results = session.query(User).all()
    for result in results:
        user_list.append(result.to_json())

    logger.debug("get_collection suc, body:%s" % body)
    return get_http_rsp(data={"user_list": user_list})

@user_router.post("/%s/graphrag/update_data" % url_prefix)
def update_graphrag_data(body: Dict):
    user_list = []

    session = GLOBALS.sql_orm.get_session()
    results = session.query(User).all()
    for result in results:
        user_list.append(result.to_json())

    logger.debug("get_collection suc, body:%s" % body)
    return get_http_rsp(data={"user_list": user_list})

@user_router.post("/%s/graphrag/get" % url_prefix)
def get_graphrag(body: Dict):
    user_list = []

    session = GLOBALS.sql_orm.get_session()
    results = session.query(User).all()
    for result in results:
        user_list.append(result.to_json())

    logger.debug("get_collection suc, body:%s" % body)
    return get_http_rsp(data={"user_list": user_list})

@user_router.post("/%s/graphrag/delete" % url_prefix)
def delete_graphrag(body: Dict):
    user_list = []

    session = GLOBALS.sql_orm.get_session()
    results = session.query(User).all()
    for result in results:
        user_list.append(result.to_json())

    logger.debug("get_collection suc, body:%s" % body)
    return get_http_rsp(data={"user_list": user_list})