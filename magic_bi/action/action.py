from loguru import logger
from pydantic import BaseModel
from caseconverter import pascalcase, snakecase

from magic_bi.plugin.base_plugin import BasePlugin
from magic_bi.utils.globals import GLOBALS


class Action(BaseModel):
    plugin_name: str
    argument: str
    # context: str = ""

    reason: str = ""
    plugin: BasePlugin = None
    result: str = ""

    def execute(self, context: str):
        if self.plugin is None:
            self.plugin = self.get_plugin()

        if self.plugin is None:
            logger.error("execute failed, get plugin failed")
            return -1

        self.result = self.plugin.run(self.argument, context)

        logger.debug("execute suc, plugin_name:%s, argument:%s, result:%s" % (self.plugin_name, self.argument, self.result))
        return 0

    def get_plugin(self):
        try:
            plugin_class_name: str = pascalcase(self.plugin_name.strip("<").strip(">")) + "Plugin"
            plugin_file_name: str = "magic_bi.plugin." + snakecase(self.plugin_name.strip("<").strip(">")) + "_plugin"
            magic_bi = __import__(plugin_file_name)
            plugin_python_module = eval(plugin_file_name)
            plugin_class = getattr(plugin_python_module, plugin_class_name)
            plugin_obj = plugin_class()

            logger.debug("get_plugin suc, plugin_name:%s" % self.plugin_name)
            return plugin_obj

        except Exception as e:
            logger.error("get_plugin failed, catch exception:%s, plugin_name:%s" % (str(e), self.plugin_name))
            return None

