from loguru import logger
from sqlalchemy.orm import Session

from magic_bi.work.work_flow import WorkOfFlow
from magic_bi.work.work import Work, WorkInput, WorkOutput
from magic_bi.work.provided_work import get_work
from magic_bi.utils.globals import Globals

internal_workflow: dict[str, dict] = {"1": [{"work_name": "InterpretImage"}, {"work_name": "SearchRelevantContent"}],
                                      "2": [{"work_name": "SearchRelevantContent"}],
                                      "3": [{"work_name": "SearchRelevantContent"}, {"work_name": "SummarizeContext"}]
                                      }

class WorkFlowAgent():
    def __init__(self):
        self.work_of_flow_list: list = []
        self.globals: Globals = None

    def init(self, workflow_id: str, globals: Globals) -> int:
        self.globals = globals

        if workflow_id in internal_workflow:
            work_of_flow_dict_list = internal_workflow[workflow_id]
            for work_of_flow_dict in work_of_flow_dict_list:
                work_of_flow: WorkOfFlow = WorkOfFlow()
                work_of_flow.from_dict(work_of_flow_dict)
                self.work_of_flow_list.append(work_of_flow)
        else:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                self.work_of_flow_list: list[WorkOfFlow] = session.query(WorkOfFlow).filter(WorkOfFlow.work_flow_id == workflow_id).all()

        if len(self.work_of_flow_list) > 0:
            logger.debug("init suc")
            return 0
        else:
            logger.error("init failed")
            return -1

    def process(self, work_input: WorkInput) -> WorkOutput:
        if len(self.work_of_flow_list) == 0:
            logger.error("WorkFlowAgent process failed")
            return None

        work_index: int = 0
        for work_of_flow in self.work_of_flow_list:
            work_index += 1
            work = get_work(work_of_flow.work_name)
            if work is None:
                logger.error("WorkFlowAgent process failed, work_name: %s not found" % work_of_flow.work_name)
                return None

            work_output: WorkOutput = work.execute(work_input)
            if work_index < len(self.work_of_flow_list):
                work_input.text_content = work_output.data

        logger.debug("execute suc")
        return work_output
