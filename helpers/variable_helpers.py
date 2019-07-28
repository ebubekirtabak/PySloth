
class VariableHelpers:

    global scope_variables = {};
    def __init__(self):
        pass

    def set_variable(self, variable_name, variable_value):
        scope_variables[variable_name] = variable_value
