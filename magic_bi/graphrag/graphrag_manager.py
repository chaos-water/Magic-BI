from loguru import logger
from magic_bi.utils.globals import GLOBALS, Globals


sql_db_create_schema_prompt_template = """
sql_db_ddl
{sql_db_ddl}

Base on the above sql db ddl, create a graph schema, which is used to translate the db data into graph data.

"""

class GraphRagManager(object):
    def __init__(self):
        self.globals: Globals = None
        pass

    def init(self, globals: Globals) -> int:
        self.globals = globals
        logger.debug("init suc")

    def create_schema(self, data_connector_id: str, graph_id: str) -> int:
        # data_connector_id = ""
        from sqlalchemy.orm.session import Session
        from sqlalchemy import update
        from magic_bi.web.data_connector_router import DATA_CONNECTOR_MANAGER
        from magic_bi.data.data_connector import DataConnector
        from magic_bi.graphrag.graphrag import GraphRag
        data_connector: DataConnector = DATA_CONNECTOR_MANAGER.get(id=data_connector_id)

        data_connector.get_db_ddl()

        prompt = sql_db_create_schema_prompt_template.replace("", data_connector.db_ddl)
        graph_schema_llm_output = self.globals.general_llm_adapter.process(prompt)

        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            stmt = update(GraphRag).where(GraphRag.graph_id == graph_id).values(schema=graph_schema_llm_output)
            session.execute(stmt)
            session.commit()

        logger.debug("create_schema suc")
        return 0

    def update_graphrag_schema(self, graph_id: str, schema: str) -> int:
        from sqlalchemy.orm.session import Session
        from sqlalchemy import update
        from magic_bi.graphrag.graphrag import GraphRag
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            stmt = update(GraphRag).where(GraphRag.graph_id == graph_id).values(schema=schema)
            session.execute(stmt)
            session.commit()


        logger.debug("update_graphrag_schema suc")
        return 0

    # def create_graphrag(self, body: Dict):
    #     user_list = []
    #
    #     session = GLOBALS.sql_orm.get_session()
    #     results = session.query(User).all()
    #     for result in results:
    #         user_list.append(result.to_json())
    #
    #     logger.debug("create_graphrag suc, body:%s" % body)
    #     return get_http_rsp(data={"user_list": user_list})
    #
    # @user_router.post("/%s/graphrag/update_data" % url_prefix)
    # def update_graphrag_data(self, body: Dict):
    #     user_list = []
    #
    #     session = GLOBALS.sql_orm.get_session()
    #     results = session.query(User).all()
    #     for result in results:
    #         user_list.append(result.to_json())
    #
    #     logger.debug("update_graphrag_data suc, body:%s" % body)
    #     return get_http_rsp(data={"user_list": user_list})
    #
    # def get_graphrag(self, body: Dict):
    #     user_list = []
    #
    #     session = GLOBALS.sql_orm.get_session()
    #     results = session.query(User).all()
    #     for result in results:
    #         user_list.append(result.to_json())
    #
    #     logger.debug("get_graphrag suc, body:%s" % body)
    #     return get_http_rsp(data={"user_list": user_list})
    #
    # def delete_graphrag(self, body: Dict):
    #     user_list = []
    #
    #     session = GLOBALS.sql_orm.get_session()
    #     results = session.query(User).all()
    #     for result in results:
    #         user_list.append(result.to_json())
    #
    #     logger.debug("delete_graphrag suc, body:%s" % body)
    #     return get_http_rsp(data={"user_list": user_list})