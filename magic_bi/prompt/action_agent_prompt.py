import re
from loguru import logger

# from magic_bi.action.action import Action

prompt_template = '''
[PROVIDED PLUGINS]:
    plugin | argument
    -----------------------
    {provided_plugins}
    
[OUTPUT ACTION FORMAT]
    <plugin>
    $PLUGIN
    </plugin>
    <argument>
    $ARGUMENT
    </argument>
    
[EXAMPLE OUTPUT ACTION]
    <plugin>
    OneExamplePlugin
    </plugin>
    <argument>
    OneExamplePluginArgument
    </argument>
    
[PERSON INPUT]:
    {person_input}
    
Based on the above, output an action to satisfy the need of the person. Choose just one of the plugin.
'''


def build_prompt(person_input: str, provided_plugins: str, chat_history: str, previous_action_result):
    return prompt_template.replace("{person_input}", person_input). \
        replace("{provided_plugins}", provided_plugins). \
        replace("{chat_history}", chat_history). \
        replace("{action_result}", previous_action_result)


# def decode_llm_output(output: str) -> Action:
#     plugin_match = re.search("<plugin>([\w\W]+)</plugin>", output)
#     argument_match = re.search("<argument>([\w\W]+)</argument>", output)
#     if plugin_match is None or argument_match is None:
#         logger.error(
#             "decode_make_plan_output failed, plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#         return None
#
#     try:
#         action = Action(plugin_name=plugin_match.group(1).strip("\n"), argument=argument_match.group(1))
#     except Exception as e:
#         logger.error("catch exception:%s" % str(e))
#         logger.error("plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#         return None
#
#     logger.debug("decode_output_action_output suc")
#     return action

#
# class ExecuteCmdPrompt(BasePrompt):
#     def build_prompt(self, person_input: str, provided_plugins: str, chat_history: str, previous_action_result):
#         return prompt_template.replace("{person_input}", person_input). \
#                                replace("{provided_plugins}", provided_plugins). \
#                                replace("{chat_history}", chat_history). \
#                                replace("{action_result}", previous_action_result)
#
#     def decode_llm_output(self, output: str) -> Action:
#         plugin_match = re.search("<plugin>([\w\W]+)</plugin>", output)
#         argument_match = re.search("<argument>([\w\W]+)</argument>", output)
#         if plugin_match is None or argument_match is None:
#             logger.error("decode_make_plan_output failed, plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#             return None
#
#         try:
#             action = Action(plugin_name=plugin_match.group(1).strip("\n"), argument=argument_match.group(1))
#         except Exception as e:
#             logger.error("catch exception:%s" % str(e))
#             logger.error("plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#             return None
#
#         logger.debug("decode_output_action_output suc")
#         return action
