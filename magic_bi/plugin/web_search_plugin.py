from loguru import logger
from typing import List
from magic_bi.web_page import WebPage
from magic_bi.tools.web_search_tool import WebSearchTool
from magic_bi.plugin.base_plugin import BasePlugin
from magic_bi.utils.globals import GLOBALS

class WebSearchPlugin(BasePlugin):
    def __init__(self):
        self._web_search_tool = WebSearchTool()

    def run(self, argument: str, context: str) -> str:
        web_page_list: List[WebPage] = self._web_search_tool.process(query=argument)
        final_content: str = ""
        for web_page in web_page_list:
            # web_page_content = web_page.content
            web_page_content = self.clean_web_content(web_page.content)
            # web_page_content = self.compress_context(web_page_content)
            # web_page_content += "web_page_name:%s \n" % web_page.name
            # web_page_content += "web_page_content:%s \n" % web_page.content
            if len(web_page_content) > 0:
                final_content += web_page_content + "\n"

            if len(final_content) > self.max_context_size:
                break

        logger.debug("run suc, final_content_length:%d" % len(final_content))
        return final_content

    def clean_web_content(self, crawled_content: str) -> str:
        if crawled_content is None:
            logger.error("clean_web_content failed, crawled_content:%s" % crawled_content)
            return ""

        crawled_content = crawled_content.strip(" ")
        if len(crawled_content) == 0:
            logger.error("clean_web_content failed, crawled_content:%s" % crawled_content)
            return ""

        if len(crawled_content) > 4096:
            logger.error("clean_web_content failed, crawled_content size too large:%d" % len(crawled_content))
            return ""

        prompt = prompt_template.format(crawled_content=crawled_content)
        llm_output = GLOBALS.llm_factory.run(prompt)

        conpressed_context = decode_llm_output(llm_output)
        logger.debug("clean_web_content suc")
        return conpressed_context

prompt_template = '''
[CRAWLED_CONTENT]:
    {crawled_content}

[OUTPUT FORMAT]:
    <content>
        $CONTENT
    </content>    
    
Based on the above, clean the "crawled content" and output in the "output format".
'''

#Based on the above, output the cleaned data in the "output format".
def decode_llm_output(llm_output: str) -> str:
    import re
    context_match = re.search("<content>([\w\W]+)</content>", llm_output)
    if context_match is None:
        return ""

    return context_match.group(1)