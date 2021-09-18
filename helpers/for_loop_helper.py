import re

from helpers.variable_helpers import VariableHelpers


class ForLoopHelper:

    def __init__(self, driver, action):
        self.driver = driver
        self.action = action

    def parse_for(self):
        action = self.action
        type = action["for_type"]
        if type == "$_FOR_EACH":
            for_variables = self.parse_variable_name(action["for_each"])
            each_actions = action["actions"]
            filled_actions = []
            for item in for_variables:
                filled_actions.append(self.fill_actions(item, each_actions))
            return filled_actions


    def fill_actions(self, variable, actions):
        filled_actions = []
        for action in actions:
            filled_action = self.fill_action_variables(variable, action)
            filled_actions.append(filled_action)

        return filled_actions

    def fill_action_variables(self, variable, action):
        variable_regex = r"(?<=\${).*?(?=\})"
        filled_action = {}
        for key in action.keys():
            value = action[key]
            names = re.findall(variable_regex, str(value))
            if len(names) > 0:
                value = self.fill_variables(variable, names, value)
            filled_action[key] = value

        return filled_action

    def fill_variables(self, variable, names, value):
        for name in names:
            new_value = self.get_value_from_variable(variable, name)
            value = value.replace("${" + name + "}", new_value)

        return value


    def get_value_from_variable(self, variable, name):
        name_tree = name.split("$")
        if len(name_tree) == 1:
            return variable[name_tree[0]]

    def get_variable_by_name(self, name):
        if VariableHelpers().is_exists_variable(name):
            return VariableHelpers().get_variable(name)

        return []

    def parse_variable_name(self, name):
        variable_tree = name.split("$")
        if len(variable_tree) == 1:
            return variable_tree[0]

        variable = None
        for name in variable_tree:

            if name is not "" and variable is None:
                variable = self.get_variable_by_name(name)
            elif name is not "":
                variable = variable[name]

        return variable




    def parse_for_each(self, action):
        pass



