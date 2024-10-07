import pandas as pd
from loguru import logger
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi import File, UploadFile, Form

from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
# from magic_bi.entity.dataset import Dataset
from magic_bi.data.data_connector_manager import DataConnectorManager
from magic_bi.data.data_connector import DataConnector, DataConnectorOrm, get_qa_template_embedding_collection_id, get_table_description_embedding_collection_id, get_domain_knowledge_embedding_collection_id
from sqlalchemy.orm.session import Session
from magic_bi.data.data_connector_knowledge.qa_template import QaTemplate
from magic_bi.data.data_connector_knowledge.table_description import TableDescription
from magic_bi.data.data_connector_knowledge.table_column_description import TableColumnDescription
from magic_bi.data.data_connector_knowledge.domain_knowledge import DomainKnowledge

DATA_CONNECTOR_MANAGER = DataConnectorManager(globals=GLOBALS)


def create_data_connector_router(prefix: str):
    data_connector_router = APIRouter(prefix=prefix)
    @data_connector_router.post("/data_connector/add")
    def add_data_connector(request: Request,body: dict):
        user_id = request.headers.get("user_id")
        data_connector_orm: DataConnectorOrm = DataConnectorOrm()
        data_connector_orm.from_dict(body)
        data_connector_orm.user_id = user_id

        qa_template_collection_id = get_qa_template_embedding_collection_id(data_connector_orm.id)
        table_description_collection_id = get_table_description_embedding_collection_id(data_connector_orm.id)
        domain_knowledge_collection_id = get_domain_knowledge_embedding_collection_id(data_connector_orm.id)

        ret1 = GLOBALS.qdrant_adapter.add_collection(qa_template_collection_id, 768)
        ret2 = GLOBALS.qdrant_adapter.add_collection(table_description_collection_id, 768)
        ret3 = GLOBALS.qdrant_adapter.add_collection(domain_knowledge_collection_id, 768)

        if ret1 != 0 or ret2 != 0 or ret3 != 0:
            logger.error("add_data_connector suc, input_body:%s" % body)
            return get_http_rsp(code=-1, msg="failed")

        ret = DATA_CONNECTOR_MANAGER.add(data_connector_orm)
        if ret != 0:
            logger.error("add_data_connector suc, input_body:%s" % body)
            return get_http_rsp(code=-1, msg="failed")

        logger.debug("add_data_connector suc, data_id:%s" % data_connector_orm.id)
        return get_http_rsp(data={"id": data_connector_orm.id})

    @data_connector_router.post("/data_connector/delete")
    def delete_data_connector(body: dict):
        data_connector_orm: DataConnectorOrm = DataConnectorOrm()
        data_connector_orm.from_dict(body)

        # data_connector: DataConnector = DataConnector()
        # data_connector.init(data_connector_orm)

        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.query(QaTemplate).filter(QaTemplate.data_connector_id == data_connector_orm.id).delete()
            session.commit()

        qa_template_collection_id = get_qa_template_embedding_collection_id(data_connector_orm.id)
        table_description_collection_id = get_table_description_embedding_collection_id(data_connector_orm.id)
        domain_knowledge_collection_id = get_domain_knowledge_embedding_collection_id(data_connector_orm.id)

        ret1 = GLOBALS.qdrant_adapter.delete_collection(qa_template_collection_id)
        ret2 = GLOBALS.qdrant_adapter.delete_collection(table_description_collection_id)
        ret3 = GLOBALS.qdrant_adapter.delete_collection(domain_knowledge_collection_id)
        if ret1 != 0 or ret2 != 0 or ret3 != 0:
            logger.error("delete_data_connector failed, data_id:%s" % data_connector_orm.id)
            return get_http_rsp(code=-1, msg="failed")

        ret = DATA_CONNECTOR_MANAGER.delete(data_connector_orm)
        if ret != 0:
            logger.error("delete_data_connector failed, data_id:%s" % data_connector_orm.id)
            return get_http_rsp(code=ret, msg="failed")

        logger.debug("delete_data_connector suc, data_id:%s" % data_connector_orm.id)
        return get_http_rsp()


    @data_connector_router.post("/data_connector/get")
    def get_data_connector(request: Request, body: dict):
        user_id = request.headers.get("user_id")
        page_index = int(body.get("page_index", 1))
        page_size = int(body.get("page_size", 10))

        data_connector_list = DATA_CONNECTOR_MANAGER.get(user_id=user_id, page_index=page_index, page_size=page_size)
        total_count = DATA_CONNECTOR_MANAGER.count(user_id)

        if data_connector_list is None:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")
        else:
            logger.debug("get suc")
            return get_http_rsp(data={"data_connector_list": [ data_connector.to_dict() for data_connector in data_connector_list ],
                                      "total_count": total_count})

    @data_connector_router.post("/data_connector/get_supported_types")
    def get_data_connector_supported_types(body: dict):
        data_connector_supported_types = [{"name":"mysql", "value":"mysql"}, {"name":"postgresql", "value":"postgresql"},
                                          {"name":"sqlite", "value":"sqlite"}]

        logger.debug("get_data_connector_supported_types suc")
        return get_http_rsp(data=data_connector_supported_types)

    @data_connector_router.post("/data_connector/delete_qa_template")
    def delete_qa_template(body: dict):
        qa_template_id = body.get("id")
        data_connector_id = body.get("data_connector_id")
        from magic_bi.data.data_connector_knowledge.qa_template import QaTemplate
        from sqlalchemy.orm import Session

        # collection_id = get_qa_template_embedding_collection_id(data_connector_id)
        # ret = GLOBALS.qdrant_adapter.delete_points(collection_id, [qa_template_id])
        # if ret != 0
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.query(QaTemplate).filter(QaTemplate.id == qa_template_id).delete()
            session.commit()

        logger.debug("delete_qa_template suc")
        return get_http_rsp()

    @data_connector_router.post("/data_connector/add_qa_template")
    def add_qa_template(body: dict):
        from magic_bi.data.data_connector_knowledge.qa_template import QaTemplate
        qa_template = QaTemplate()
        qa_template.from_dict(body)

        ret = DATA_CONNECTOR_MANAGER.add_qa_template(qa_template)
        if ret == 0:
            logger.debug("add_qa_template suc")
            return get_http_rsp(data={"id": qa_template.data_connector_id})
        else:
            logger.error("add_qa_template failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_connector_router.post("/data_connector/get_qa_template")
    def get_qa_template(body: dict):
        data_connector_id = body.get("data_connector_id", "")

        qa_template_list = DATA_CONNECTOR_MANAGER.get_qa_template(data_connector_id)

        logger.debug("get_qa_template suc")
        return get_http_rsp(data=qa_template_list)

    @data_connector_router.post("/data_connector/update_qa_template")
    def update_qa_template(body: dict):
        from magic_bi.data.data_connector_knowledge.qa_template import QaTemplate

        qa_template = QaTemplate()
        qa_template.from_dict(body)

        ret = DATA_CONNECTOR_MANAGER.update_qa_template(qa_template)
        if ret == 0:
            logger.debug("update_qa_template suc")
        else:
            logger.error("update_qa_template failed")

        return get_http_rsp()

    import io
    @data_connector_router.post("/data_connector/export_qa_template")
    def export_qa_template(body: dict):
        data_connector_id = body.get("data_connector_id", "")

        df = DATA_CONNECTOR_MANAGER.export_qa_template(data_connector_id)

        # 使用 BytesIO 将数据保存到内存中
        file_stream = io.BytesIO()
        df.to_csv(file_stream, index=False)
        file_stream.seek(0)  # 将文件指针移动到开始位置

        return StreamingResponse(file_stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=questions_and_answers.csv"})


    @data_connector_router.post("/data_connector/import_qa_template")
    # def import_qa_template(file: UploadFile = File(...), data_connector_id: Form = Form(...)):
    def import_qa_template(file: UploadFile = File(...), data_connector_id: str = ""):
        try:
            df = pd.read_csv(file.file)

            DATA_CONNECTOR_MANAGER.import_qa_template(df, data_connector_id)


            return get_http_rsp()
        except Exception as e:
            return get_http_rsp(code=-1, msg=str(e))

    @data_connector_router.post("/data_connector/add_table_description")
    def add_table_description(body: dict):
        table_description = TableDescription()
        table_description.from_dict(body)

        ret = DATA_CONNECTOR_MANAGER.add_table_description(table_description)
        if ret == 0:
            logger.debug("add_table_description suc")
            return get_http_rsp(data={"id": table_description.id})
        else:
            logger.error("add_table_description failed")
            return get_http_rsp(code=-1, msg="failed")


    @data_connector_router.post("/data_connector/delete_table_description")
    def delete_table_description(body: dict):
        id = body.get("id", "")
        data_connector_id = body.get("data_connector_id", "")

        # ret = execute_add_qa_template(body)
        ret = DATA_CONNECTOR_MANAGER.delete_table_description(data_connector_id, id)
        if ret == 0:
            logger.debug("delete_table_description suc")
            return get_http_rsp()
        else:
            logger.error("delete_table_description failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_connector_router.post("/data_connector/get_table_description")
    def get_table_description(body: dict):
        data_connector_id = body.get("data_connector_id", "")

        table_description_list = DATA_CONNECTOR_MANAGER.get_table_description(data_connector_id)
        logger.debug("add_qa_template suc")
        return get_http_rsp(data=table_description_list)

    @data_connector_router.post("/data_connector/add_table_column_description")
    def add_table_column_description(body: dict):
        table_column_description = TableColumnDescription()
        table_column_description.from_dict(body)

        ret = DATA_CONNECTOR_MANAGER.add_table_column_description(table_column_description)
        if ret == 0:
            logger.debug("add_table_column_description suc")
            return get_http_rsp(data={"id": table_column_description.id})
        else:
            logger.error("add_table_column_description failed")
            return get_http_rsp(code=-1, msg="failed")


    @data_connector_router.post("/data_connector/delete_table_column_description")
    def delete_table_column_description(body: dict):
        id = body.get("id", "")

        ret = DATA_CONNECTOR_MANAGER.delete_table_column_description(id)
        if ret == 0:
            logger.debug("delete_table_column_description suc")
            return get_http_rsp()
        else:
            logger.error("delete_table_column_description failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_connector_router.post("/data_connector/get_table_column_description")
    def get_table_column_description(body: dict):
        data_connector_id = body.get("data_connector_id", "")

        table_description_list = DATA_CONNECTOR_MANAGER.get_table_column_description(data_connector_id)
        logger.debug("get_table_column_description suc")
        return get_http_rsp(data=table_description_list)

    @data_connector_router.post("/data_connector/add_domain_knowledge")
    def add_domain_knowledge(body: dict):
        domain_knowledge = DomainKnowledge()
        domain_knowledge.from_dict(body)

        ret = DATA_CONNECTOR_MANAGER.add_domain_knowledge(domain_knowledge)
        if ret == 0:
            logger.debug("add_domain_knowledge suc")
            return get_http_rsp(data={"id": domain_knowledge.id})
        else:
            logger.error("add_domain_knowledge failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_connector_router.post("/data_connector/delete_domain_knowledge")
    def delete_domain_knowledge(body: dict):
        id = body.get("id", "")
        data_connector_id = body.get("data_connector_id", "")

        ret = DATA_CONNECTOR_MANAGER.delete_domain_knowledge(data_connector_id, id)
        if ret == 0:
            logger.debug("delete_domain_knowledge suc")
            return get_http_rsp()
        else:
            logger.error("delete_domain_knowledge failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_connector_router.post("/data_connector/get_domain_knowledge")
    def get_domain_knowledge(body: dict):
        data_connector_id = body.get("data_connector_id", "")

        domain_knowledge_list = DATA_CONNECTOR_MANAGER.get_domain_knowledge(data_connector_id)

        logger.debug("get_domain_knowledge suc")
        return get_http_rsp(data=domain_knowledge_list)

    return data_connector_router
