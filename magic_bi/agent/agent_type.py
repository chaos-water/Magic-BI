from enum import Enum


class AGENT_TYPE(Enum):
    SQL_BY_GENERAL_LLM= "sql_by_general_llm"
    SQL_BY_FINETUNE_LLM= "sql_by_finetune_llm"
    SQL = "sql"
    RAG = "rag"
    APP_BY_GENERAL_LLM = "app_by_general_llm"
    WORK_FLOW = "work_flow"
