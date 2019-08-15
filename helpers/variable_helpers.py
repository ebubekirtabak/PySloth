
class VariableHelpers:

    def __init__(self):
        pass

    @staticmethod
    def load_scope_variables():
        global scope_variables
        scope_variables = {}

    @staticmethod
    def set_variable(variable_name, variable_value):
        global scope_variables
        if scope_variables is None:
            VariableHelpers.load_scope_variables()

        scope_variables[variable_name] = variable_value

    @staticmethod
    def get_variable(variable_name):
        global scope_variables
        try:
            return scope_variables[variable_name]
        except Exception as e:
            print('Error: ' + str(e))
            return None
