import pandas as pd
from loguru import logger
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi import File, UploadFile, Form

from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
# from magic_bi.entity.dataset import Dataset
from magic_bi.data.data_source_manager import DataSourceManager
from magic_bi.data.data_source import DataSource, DataSourceOrm, get_qa_template_embedding_collection_id, get_table_description_embedding_collection_id, get_domain_knowledge_embedding_collection_id
from sqlalchemy.orm.session import Session
from magic_bi.data.data_source_knowledge.qa_template import QaTemplate
from magic_bi.data.data_source_knowledge.table_description import TableDescription
from magic_bi.data.data_source_knowledge.table_column_description import TableColumnDescription
from magic_bi.data.data_source_knowledge.domain_knowledge import DomainKnowledge

DATA_SOURCE_MANAGER = DataSourceManager(globals=GLOBALS, lanuage_config=GLOBAL_CONFIG.language_config)


def create_data_source_router(prefix: str):
    data_source_router = APIRouter(prefix=prefix)
    @data_source_router.post("/data_source/add")
    def add_data_source(request: Request,body: dict):
        user_id = request.headers.get("user_id", "default")
        data_source_orm: DataSourceOrm = DataSourceOrm()
        data_source_orm.from_dict(body)
        data_source_orm.user_id = user_id

        code, msg = DATA_SOURCE_MANAGER.add(data_source_orm)
        if code != 0:
            logger.error("add_data_source suc, input_body:%s" % body)
            return get_http_rsp(code=code, msg=msg)

        logger.debug("add_data_source suc, data_id:%s" % data_source_orm.id)
        return get_http_rsp(data={"id": data_source_orm.id})

    @data_source_router.post("/data_source/delete")
    def delete_data_source(body: dict):
        data_source_orm: DataSourceOrm = DataSourceOrm()
        data_source_orm.from_dict(body)

        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.query(QaTemplate).filter(QaTemplate.data_source_id == data_source_orm.id).delete()
            session.commit()

        qa_template_collection_id = get_qa_template_embedding_collection_id(data_source_orm.id)
        table_description_collection_id = get_table_description_embedding_collection_id(data_source_orm.id)
        domain_knowledge_collection_id = get_domain_knowledge_embedding_collection_id(data_source_orm.id)

        ret1 = GLOBALS.qdrant_adapter.delete_collection(qa_template_collection_id)
        ret2 = GLOBALS.qdrant_adapter.delete_collection(table_description_collection_id)
        ret3 = GLOBALS.qdrant_adapter.delete_collection(domain_knowledge_collection_id)
        if ret1 != 0 or ret2 != 0 or ret3 != 0:
            logger.error("delete_data_source failed, data_id:%s" % data_source_orm.id)
            return get_http_rsp(code=-1, msg="failed")

        ret = DATA_SOURCE_MANAGER.delete(data_source_orm)
        if ret != 0:
            logger.error("delete_data_source failed, data_id:%s" % data_source_orm.id)
            return get_http_rsp(code=ret, msg="failed")

        logger.debug("delete_data_source suc, data_id:%s" % data_source_orm.id)
        return get_http_rsp()


    @data_source_router.post("/data_source/get")
    def get_data_source(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")
        page_index = int(body.get("page_index", 1))
        page_size = int(body.get("page_size", 10))

        data_source_list = DATA_SOURCE_MANAGER.get(user_id=user_id, page_index=page_index, page_size=page_size)
        total_count = DATA_SOURCE_MANAGER.count(user_id)

        if data_source_list is None:
            logger.error("get failed")
            return get_http_rsp(code=-1, msg="failed")
        else:
            logger.debug("get suc")
            return get_http_rsp(data={"data_source_list": [ data_source.to_dict() for data_source in data_source_list ],
                                      "total_count": total_count})

    @data_source_router.post("/data_source/get_supported_types")
    def get_data_source_supported_types(body: dict):
        data_source_supported_types = [{"name":"mysql", "value":"mysql"}, {"name":"postgresql", "value":"postgresql"},
                                          {"name":"sqlite", "value":"sqlite"}]

        logger.debug("get_data_source_supported_types suc")
        return get_http_rsp(data=data_source_supported_types)

    @data_source_router.post("/data_source/delete_qa_template")
    def delete_qa_template(body: dict):
        qa_template_id = body.get("id")
        data_source_id = body.get("data_source_id")
        from magic_bi.data.data_source_knowledge.qa_template import QaTemplate
        from sqlalchemy.orm import Session

        # collection_id = get_qa_template_embedding_collection_id(data_source_id)
        # ret = GLOBALS.qdrant_adapter.delete_points(collection_id, [qa_template_id])
        # if ret != 0
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.query(QaTemplate).filter(QaTemplate.id == qa_template_id).delete()
            session.commit()

        logger.debug("delete_qa_template suc")
        return get_http_rsp()

    @data_source_router.post("/data_source/add_qa_template")
    def add_qa_template(body: dict):
        from magic_bi.data.data_source_knowledge.qa_template import QaTemplate
        qa_template = QaTemplate()
        qa_template.from_dict(body)

        ret = DATA_SOURCE_MANAGER.add_qa_template(qa_template)
        if ret == 0:
            logger.debug("add_qa_template suc")
            return get_http_rsp(data={"id": qa_template.data_source_id})
        else:
            logger.error("add_qa_template failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_source_router.post("/data_source/get_qa_template")
    def get_qa_template(body: dict):
        data_source_id = body.get("data_source_id", "")

        qa_template_list = DATA_SOURCE_MANAGER.get_qa_template(data_source_id)

        logger.debug("get_qa_template suc")
        return get_http_rsp(data=qa_template_list)

    @data_source_router.post("/data_source/update_qa_template")
    def update_qa_template(body: dict):
        from magic_bi.data.data_source_knowledge.qa_template import QaTemplate

        qa_template = QaTemplate()
        qa_template.from_dict(body)

        ret = DATA_SOURCE_MANAGER.update_qa_template(qa_template)
        if ret == 0:
            logger.debug("update_qa_template suc")
        else:
            logger.error("update_qa_template failed")

        return get_http_rsp()

    import io
    @data_source_router.post("/data_source/export_qa_template")
    def export_qa_template(body: dict):
        data_source_id = body.get("data_source_id", "")

        df = DATA_SOURCE_MANAGER.export_qa_template(data_source_id)

        # 使用 BytesIO 将数据保存到内存中
        file_stream = io.BytesIO()
        df.to_csv(file_stream, index=False)
        file_stream.seek(0)  # 将文件指针移动到开始位置

        return StreamingResponse(file_stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=questions_and_answers.csv"})


    @data_source_router.post("/data_source/import_qa_template")
    # def import_qa_template(file: UploadFile = File(...), data_source_id: Form = Form(...)):
    def import_qa_template(file: UploadFile = File(...), data_source_id: str = ""):
        try:
            df = pd.read_csv(file.file)

            DATA_SOURCE_MANAGER.import_qa_template(df, data_source_id)


            return get_http_rsp()
        except Exception as e:
            return get_http_rsp(code=-1, msg=str(e))

    @data_source_router.post("/data_source/add_table_description")
    def add_table_description(body: dict):
        table_description = TableDescription()
        table_description.from_dict(body)

        ret = DATA_SOURCE_MANAGER.add_table_description(table_description)
        if ret == 0:
            logger.debug("add_table_description suc")
            return get_http_rsp(data={"id": table_description.id})
        else:
            logger.error("add_table_description failed")
            return get_http_rsp(code=-1, msg="failed")


    @data_source_router.post("/data_source/delete_table_description")
    def delete_table_description(body: dict):
        id = body.get("id", "")
        data_source_id = body.get("data_source_id", "")

        # ret = execute_add_qa_template(body)
        ret = DATA_SOURCE_MANAGER.delete_table_description(data_source_id, id)
        if ret == 0:
            logger.debug("delete_table_description suc")
            return get_http_rsp()
        else:
            logger.error("delete_table_description failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_source_router.post("/data_source/get_table_description")
    def get_table_description(body: dict):
        data_source_id = body.get("data_source_id", "")

        table_description_list = DATA_SOURCE_MANAGER.get_table_description(data_source_id)
        logger.debug("add_qa_template suc")
        return get_http_rsp(data=table_description_list)

    @data_source_router.post("/data_source/add_table_column_description")
    def add_table_column_description(body: dict):
        table_column_description = TableColumnDescription()
        table_column_description.from_dict(body)

        ret = DATA_SOURCE_MANAGER.add_table_column_description(table_column_description)
        if ret == 0:
            logger.debug("add_table_column_description suc")
            return get_http_rsp(data={"id": table_column_description.id})
        else:
            logger.error("add_table_column_description failed")
            return get_http_rsp(code=-1, msg="failed")


    @data_source_router.post("/data_source/delete_table_column_description")
    def delete_table_column_description(body: dict):
        id = body.get("id", "")

        ret = DATA_SOURCE_MANAGER.delete_table_column_description(id)
        if ret == 0:
            logger.debug("delete_table_column_description suc")
            return get_http_rsp()
        else:
            logger.error("delete_table_column_description failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_source_router.post("/data_source/get_table_column_description")
    def get_table_column_description(body: dict):
        data_source_id = body.get("data_source_id", "")

        table_description_list = DATA_SOURCE_MANAGER.get_table_column_description(data_source_id)
        logger.debug("get_table_column_description suc")
        return get_http_rsp(data=table_description_list)

    @data_source_router.post("/data_source/add_domain_knowledge")
    def add_domain_knowledge(body: dict):
        domain_knowledge = DomainKnowledge()
        domain_knowledge.from_dict(body)

        ret = DATA_SOURCE_MANAGER.add_domain_knowledge(domain_knowledge)
        if ret == 0:
            logger.debug("add_domain_knowledge suc")
            return get_http_rsp(data={"id": domain_knowledge.id})
        else:
            logger.error("add_domain_knowledge failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_source_router.post("/data_source/delete_domain_knowledge")
    def delete_domain_knowledge(body: dict):
        id = body.get("id", "")
        data_source_id = body.get("data_source_id", "")

        ret = DATA_SOURCE_MANAGER.delete_domain_knowledge(data_source_id, id)
        if ret == 0:
            logger.debug("delete_domain_knowledge suc")
            return get_http_rsp()
        else:
            logger.error("delete_domain_knowledge failed")
            return get_http_rsp(code=-1, msg="failed")

    @data_source_router.post("/data_source/get_domain_knowledge")
    def get_domain_knowledge(body: dict):
        data_source_id = body.get("data_source_id", "")

        domain_knowledge_list = DATA_SOURCE_MANAGER.get_domain_knowledge(data_source_id)

        logger.debug("get_domain_knowledge suc")
        return get_http_rsp(data=domain_knowledge_list)

    return data_source_router
