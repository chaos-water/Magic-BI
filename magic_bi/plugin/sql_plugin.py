from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from loguru import logger
from magic_bi.plugin.base_plugin import BasePlugin
from magic_bi.utils.utils import format_db_url
class SqlPlugin(BasePlugin):
    def run(self, sql_cmd: str, db_url: str) -> (int, str):
        sql_cmd = self._clean_argument(sql_cmd)

        try:
            db_url = format_db_url(db_url)
            engine = create_engine(db_url)

            # 创建会话
            Session = sessionmaker(bind=engine)
            session = Session()

            # 执行查询并将结果转化为 Pandas DataFrame
            result = session.execute(text(sql_cmd))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

            logger.debug("sql plugin run suc")
            return (0, df.to_string())

        except Exception as e:
            logger.error("sql plugin run failed")
            logger.error("catch exception:%s" % str(e))
            return (-1, str(e))

        finally:
            session.close()
            engine.dispose()

    def _clean_argument(self, argument: str) -> str:
        import re
        if "```sql" in argument:
            pattern = re.compile(r'```sql(.*?)```', re.DOTALL)

            # 提取并清理代码块
            matches = pattern.findall(argument)
            cleaned_code = [match.strip() for match in matches]

            # 将提取到的代码合并为一个字符串
            extracted_code = '\n'.join(cleaned_code)
            return extracted_code
        else:
            return argument