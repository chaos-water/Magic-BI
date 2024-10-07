import json
from magic_bi.action.action import Action

def action_to_json_str(action: Action):
    previous_action = {"plugin": action.plugin_name, "argument": action.argument, "result": action.result}
    return json.dumps(previous_action, ensure_ascii=False)

# def to_str(self):
#     return self.to_str_json()

def action_to_list_str(action: Action):
    output = "%s | %s | %s" % (action.plugin_name, action.argument, action.result.replace("\n", " "))
    return output

def action_to_xml_str(action: Action):
    output = ""
    if action.plugin_name == "":
        return output

    output += "<plugin>%s</plugin>\n" % action.plugin_name
    output += "<argument>%s</argument>\n" % action.argument
    # output += "<result>%s</result>" % action.result.lstrip("\n").rstrip("\n")

    return output