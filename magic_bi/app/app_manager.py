
from loguru import logger
from sqlalchemy.orm import Session

from magic_bi.db.qdrant_adapter import QdrantPoint
from magic_bi.utils.globals import Globals
# from magic_bi.tools.doc_reader_tool import DocReaderTool
from magic_bi.data.data import Data
from magic_bi.app.app import App
from magic_bi.app.app_api import AppApi

retrieve_triples_prompt_template = """
[Text To Retrieve]
{text_to_retrieve}

Retrieve as many triples as possible from the above text. Output directly without explanation.
"""

class AppManager():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals

    def add_app(self, app: App) -> int:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.add(app)
                session.commit()

        except Exception as e:
            logger.error("add app failed")
            logger.error("catch exception:%s" % str(e))
            return -1

        logger.debug("add app suc")
        return 0


    def delete_app(self, app_id: str) -> int:
        with Session(self.globals.sql_orm.engine) as session:
            session.query(App).filter(App.id == app_id).delete()
            session.commit()

        logger.debug("delete app suc")
        return 0

    def get_app(self, user_id: str) -> list[App]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            app_list: list[App] = session.query(App).filter(App.user_id == user_id).all()

        logger.debug("get app suc, app_cnt:%d" % len(app_list))
        return app_list

    def add_app_api(self, app_api: AppApi) -> int:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.add(app_api)
                session.commit()

        except Exception as e:
            logger.error("add app_api failed")
            logger.error("catch exception:%s" % str(e))
            return -1

        logger.debug("add app_api suc")
        return 0

    def get_app_api(self, app_id: str) -> list[AppApi]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            app_api_list: list[AppApi] = session.query(AppApi).filter(AppApi.app_id == app_id).all()

        logger.debug("get app_api suc, app_api_cnt:%d" % len(app_api_list))
        return app_api_list

    def delete_app_api(self, app_api_id: str):
        with Session(self.globals.sql_orm.engine) as session:
            session.query(AppApi).filter(AppApi.id == app_api_id).delete()
            session.commit()

        logger.debug("delete app_api suc")
        return 0

    def delete_app_api_by_app_id(self, app_id: str):
        with Session(self.globals.sql_orm.engine) as session:
            session.query(AppApi).filter(AppApi.app_id == app_id).delete()
            session.commit()

        logger.debug("delete app_api suc")
        return 0

    def import_app_api(self, file_json_data: dict, user_id: str, app_id: str) -> int:
        app_api_list = self.translate_json_to_app_api(file_json_data, user_id, app_id)
        for app_api in app_api_list:
            with Session(self.globals.sql_orm.engine) as session:
                session.add(app_api)
                session.commit()

        logger.debug("import_app_api suc")
        return 0

    def translate_json_to_app_api(self, file_json_data: dict, user_id: str, app_id: str) -> list[AppApi]:
        app_api_list = []

        # 获取文档中的路径信息
        paths = file_json_data.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                # 初始化 API 信息
                api_data = {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": [],
                    "responses": {}
                }

                # 解析请求参数
                if "parameters" in details:
                    for param in details["parameters"]:
                        param_info = {
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "description": param.get("description", ""),
                            "required": param.get("required", False),
                            "schema": param.get("schema", {})
                        }
                        api_data["parameters"].append(param_info)

                # 解析请求体
                if "requestBody" in details:
                    request_body = details["requestBody"]
                    content = request_body.get("content", {})
                    api_data["request_body"] = content

                # 解析响应
                if "responses" in details:
                    for status_code, response in details["responses"].items():
                        response_info = {
                            "description": response.get("description", ""),
                            "content": response.get("content", {})
                        }
                        api_data["responses"][status_code] = response_info

                # 添加 API 数据到结果列表
                app_api: AppApi = AppApi()
                app_api.from_dict(api_data)
                app_api.user_id = user_id
                app_api.app_id = app_id
                app_api_list.append(app_api)

        logger.debug("import_app_api suc")
        return app_api_list

    def export_app_api(self, app_id: str) -> str:
        app_api_list: list[AppApi] = self.get_app_api(app_id)

