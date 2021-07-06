import random
import time
from datetime import datetime

from logger import Logger


class VariableHelpers:

    def __init__(self):
        self.logger = Logger()

    @staticmethod
    def load_scope_variables():
        global scope_variables
        scope_variables = {}

    @staticmethod
    def set_variable(variable_name, variable_value):
        try:
            global scope_variables
            if isinstance(variable_value, list):
                Logger().set_log("Variable name: " + variable_name + " : value: " + str(variable_value))
            elif isinstance(variable_value, str):
                Logger().set_log("Variable name: " + variable_name + " : value: " + variable_value)

            if scope_variables is None:
                VariableHelpers.load_scope_variables()
            if variable_name in scope_variables:
                if type(scope_variables[variable_name]).__name__ == 'list':
                    scope_variables[variable_name].append(variable_value)
                elif type(scope_variables[variable_name]).__name__ == 'dict':
                    value = scope_variables[variable_name]
                    scope_variables[variable_name] = [value, variable_value]
            else:
                scope_variables[variable_name] = variable_value
        except Exception as e:
            Logger().set_log('set_variable Error: ' + str(e))

    @staticmethod
    def get_variable(variable_name):
        global scope_variables
        try:
            return scope_variables[variable_name]
        except Exception as e:
            Logger().set_log('get_variable Error: ' + str(e))
            return VariableHelpers.find_object_by_name(variable_name)

    def find_object_by_name(variable_name):
        obj = None
        global scope_variables
        for key in scope_variables.keys():
            search_key = variable_name + '.'
            index = key.find(search_key)
            if index > -1:
                if obj is None:
                    obj = {}

                name = key[(len(search_key) + index):]
                obj[name] = scope_variables[key]

        return obj

    @staticmethod
    def delete_variable(variable_name):
        del scope_variables[variable_name]

    @staticmethod
    def rename_variable(variable_name, new_name):
        scope_variables[new_name] = scope_variables[variable_name]
        del scope_variables[variable_name]

    @staticmethod
    def get_value_with_function(doc, selector):
        if selector == "@generate_uniq_number":
            return VariableHelpers.generate_uniq_number()
        elif selector == "@get_scope_variables":
            return VariableHelpers.get_scope_variables()
        elif selector == "@get_unix_time":
            return VariableHelpers.get_unix_time()
        elif selector == "@get_utc_time":
            return VariableHelpers.get_utc_time()
        elif selector == "@get_time":
            return VariableHelpers.get_time()
        elif selector == "@get_page_source":
            return doc.page_source
        elif selector == "@screenshot_as_base64":
            return doc.get_screenshot_as_base64()

    @staticmethod
    def generate_uniq_number():
        random.seed(datetime.now())
        return random.random()

    @staticmethod
    def get_scope_variables():
        global scope_variables
        return scope_variables

    @staticmethod
    def get_unix_time():
        return time.time()

    @staticmethod
    def get_utc_time():
        return datetime.utcnow()

    @staticmethod
    def get_time():
        return datetime.now()

    @staticmethod
    def is_exists_variable(variable_name):
        global scope_variables
        if ":" in variable_name:
            names = variable_name.split(':')
            variable = scope_variables[names[0]]
            names = names[1:]
            for name in names:
                if variable is None:
                    return False
                elif name in variable:
                    variable = variable[name]
                else:
                    return False

            return True

        elif variable_name in scope_variables and len(scope_variables[variable_name]) != 0:
            return True
        else:
            return False
