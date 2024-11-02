from loguru import logger
from fastapi import APIRouter, Request


# from entity.collection import Collection
from magic_bi.user import User
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp

user_router = APIRouter()

# url_prefix = "magic_bi"
url_prefix = GLOBAL_CONFIG.system_config.url_prefix

def create_user_router(prefix: str):
    user_router = APIRouter(prefix=prefix)

    @user_router.post("/user/add")
    def add_user(body: dict):
        user_name = body.get("user_name")

        user: User = User()
        user.user_name = user_name


        session = GLOBALS.sql_orm.get_session()
        session.add(user)
        session.commit()

        logger.debug("add_user suc")
        return get_http_rsp(data={"user_id": user.user_id})

    @user_router.post("/user/delete")
    def delete_user(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")

        session = GLOBALS.sql_orm.get_session()
        user: User = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            logger.error("delete_user suc")
            return get_http_rsp(code=-1, msg="failed")

        session.delete(user)

        logger.debug("delete_user suc")
        return get_http_rsp()

    @user_router.post("/user/get")
    def get_user(body: dict):
        user_list = []

        session = GLOBALS.sql_orm.get_session()
        results = session.query(User).all()
        for result in results:
            user_list.append(result.to_json())

        logger.debug("get_collection suc, body:%s" % body)
        return get_http_rsp(data={"user_list": user_list})

    return user_router