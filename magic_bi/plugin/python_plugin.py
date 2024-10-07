# -*- coding: utf-8 -*-

from loguru import logger
from magic_bi.plugin.base_plugin import BasePlugin
import io
import sys


# 我想实现个功能：参数是python代码，执行结果输出到stdout，run函数返回完整的执行结果。目前这段代码会有问题，问题是会对执行结果有压缩，该如何解决呢？
class PythonPlugin(BasePlugin):

    def run(self, argument: str) -> (int, str, str):
        argument = self._clean_argument(argument)
        # 创建一个StringIO对象来捕获输出
        output_capture = io.StringIO()
        # 保存原来的标准输出对象
        original_stdout = sys.stdout
        import pandas as pd
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', None)

        try:
            # 将标准输出重定向到StringIO对象
            sys.stdout = output_capture
            # 使用exec函数执行输入的代码
            exec(argument)
        except Exception as e:
            logger.error(f"Error: {e}")
            return (-1, str(e), argument)
        finally:
            # 恢复原来的标准输出对象
            sys.stdout = original_stdout
        # 获取捕获的输出


        output = output_capture.getvalue()
        logger.debug("run suc, output length:%d" %  len(output))

        if "error" in output and "failed" in output:
            return -1, output, argument
        else:
            return 0, output, ""


    def _clean_argument(self, argument: str) -> str:
        import re
        if "```python" in argument:
            pattern = re.compile(r'```python(.*?)```', re.DOTALL)

            # 提取并清理代码块
            matches = pattern.findall(argument)
            cleaned_code = [match.strip() for match in matches]

            # 将提取到的代码合并为一个字符串
            extracted_code = '\n'.join(cleaned_code)
            return extracted_code
        else:
            return argument
