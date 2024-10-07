from loguru import logger
import re
from magic_bi.plugin.base_plugin import BasePlugin
from magic_bi.utils.globals import GLOBALS

prompt_template = '''
[SOURCE MATERIAL]:
    {source_material}

[DOC SUBJECT]:
    {doc_subject}
    
[OUTPUT FORMAT]:
    <content>
        $CONTENT
    </content>
    
Based on the above, refer to the source material, write a document. Output in the output format.
'''

def decode_llm_output(llm_output: str):
    content_match = re.search("<content>([\w\W]+)</content>", llm_output)
    if content_match is not None:
        logger.debug("decode_llm_output suc")
        content = content_match.group(1)
    else:
        logger.error("decode_llm_output failed, llm_output:%s" % llm_output)
        content = ""

    return content


class DocWriterPlugin(BasePlugin):
    def run(self, argument: str, context: str) -> str:
        prompt = prompt_template.format(doc_subject=argument, source_material=context)
        llm_output = GLOBALS.llm_factory.run(prompt)
        content = decode_llm_output(llm_output)

        logger.debug("run suc, content:%s" % content)
        return content
