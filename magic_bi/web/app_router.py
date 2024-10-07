import json

from loguru import logger
from fastapi import APIRouter, Request
from fastapi import File, Form

from typing import Dict

from magic_bi.app.app_api import AppApi
from magic_bi.utils.globals import GLOBALS
from magic_bi.utils.utils import get_http_rsp
from magic_bi.app.app_manager import AppManager
from magic_bi.app.app import App

APP_MANAGER = AppManager(globals=GLOBALS)


def create_app_router(prefix: str):
    app_router = APIRouter(prefix=prefix)

    @app_router.post("/app/add")
    def add_app(body: Dict):
        app: App = App()
        app.from_dict(body)

        ret = APP_MANAGER.add_app(app)
        if ret == 0:
            logger.debug("add_app suc, app_id:%s" % app.id)
            return get_http_rsp(data={"id": app.id})
        else:
            logger.error("add_app failed")
            return get_http_rsp(code=-1, msg="failed")

    @app_router.post("/app/delete")
    def delete_app(body: Dict):
        app_id = body.get("id")

        ret = APP_MANAGER.delete_app(app_id)
        if ret == 0:
            logger.debug("delete suc, app_id:%s" % app_id)
            return get_http_rsp()
        else:
            logger.error("delete failed, app_id:%s" % app_id)
            return get_http_rsp(code=ret, msg="failed")

    @app_router.post("/app/get")
    def get_app(request: Request, body: Dict):
        user_id = request.headers.get("user_id")
        # user_id = body.get("user_id")
        app_list = APP_MANAGER.get_app(user_id)

        if app_list is not None:
            logger.debug("get suc")
            return get_http_rsp(data=[ app.to_dict() for app in app_list ])
        else:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")

    @app_router.post("/app/api/add")
    def add_app_api(body: Dict):
        app_api: AppApi = AppApi()
        app_api.from_dict(body)

        ret = APP_MANAGER.add_app(app_api)
        if ret == 0:
            logger.debug("add_app_api suc, app_api_id:%s" % app_api.id)
            return get_http_rsp(data={"id": app_api.id})
        else:
            logger.error("add_file failed")
            return get_http_rsp(code=-1, msg="failed")

    @app_router.post("/app/api/delete")
    def delete_app_api(body: Dict):
        app_api_id = body.get("id", "")
        app_id = body.get("app_id", "")

        if app_id != "":
            ret = APP_MANAGER.delete_app_api_by_app_id(app_id)
        else:
            ret = APP_MANAGER.delete_app(app_api_id)
        if ret == 0:
            logger.debug("delete_app_api suc, app_api_id:%s" % app_api_id)
            return get_http_rsp()
        else:
            logger.error("delete_app_api failed, app_api_id:%s" % app_api_id)
            return get_http_rsp(code=ret, msg="failed")

    @app_router.post("/app/api/get")
    def get_app_api(body: Dict):
        app_id = body.get("app_id")

        app_api_list = APP_MANAGER.get_app_api(app_id)
        if app_api_list is not None:
            logger.debug("get_app_api suc")
            return get_http_rsp(data=[app_api.to_dict() for app_api in app_api_list])
        else:
            logger.error("get_app_api failed")
            return get_http_rsp(code=-1, msg="failed")

    @app_router.post("/app/api/import")
    def import_app_api(file=File(), user_id=Form(), app_id=Form()):
        file_bytes = file.file.read()
        file_content = file_bytes.decode()
        file_json_data = json.loads(file_content)
        ret = APP_MANAGER.import_app_api(file_json_data=file_json_data, user_id=user_id, app_id=app_id)
        if ret == 0:
            logger.debug("import_app_api suc")
            return get_http_rsp()
        else:
            logger.error("import_app_api failed")
            return get_http_rsp(code=-1, msg="failed")

    @app_router.post("/app/api/export")
    def export_app_api(user_id=Form(), app_id=Form()):
        ret = APP_MANAGER.import_app_api()
        if ret == 0:
            logger.debug("export_app_api suc")
            return get_http_rsp()
        else:
            logger.error("export_app_api failed")
            return get_http_rsp(code=-1, msg="failed")

    return app_router


