
class VariableHelpers:

    global scope_variables = {};
    def __init__(self):
        pass

    @staticmethod
    def set_variable(variable_name, variable_value):
        scope_variables[variable_name] = variable_value
