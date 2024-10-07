# PROVIDED_PLUGINS = '''
#     Shell | shell command (non-interactive, single line)
#     WebSearch | keywords
#     DocReader | file path or file url (support file types: docx, doc, pptx, ppt and pdf)
#     SummarizePlugin | text
#     AskUser | question
# '''
#
# PROVIDED_PLUGINS_SIMPLE = '''
#     Shell | shell command (non-interactive, single line)
#     WebSearch | keywords
#     DocReader | file path or file url (support file types: docx, doc, pptx, ppt and pdf)
#     SummarizePlugin | text (which would be summarized)
# '''

from loguru import logger

provided_plugins = {}


def get_provided_plugins() -> str:
    output_str = ""
    for plugin_name, plugin_intro in provided_plugins.items():
        plugin_info_row_str = "\t%s | %s\n" % (plugin_name, plugin_intro)
        output_str += plugin_info_row_str

    logger.debug("output_str:\n%s" % output_str)
    return output_str


def register_plugin():
    provided_plugins["Shell"] = "shell command (non-interactive, single line)"
    provided_plugins["WebSearch"] = "keywords"
    provided_plugins["DocWriter"] = "doc subject, source material"
    provided_plugins["FileReader"] = "file path or file url (support file types: docx, doc, pptx, ppt and pdf)"

    logger.debug("register_plugin suc, provided_plugins_cnt:%d" % len(provided_plugins))
    return 0
