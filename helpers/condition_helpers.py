from selenium.common.exceptions import NoSuchElementException

from helpers.variable_helpers import VariableHelpers
from logger import Logger


class ConditionHelpers:

    def __init__(self, doc, action):
        self.doc = doc
        self.action = action
        self.logger = Logger()

    def parse_condition(self):
        for condition in self.action['conditions']:
            type = condition['type']
            if type == 'if_selector':
                return self.if_selector(condition)
            elif type == 'if_not_selector':
                return self.if_not_selector(condition)
            elif type == 'if_exists_variable':
                return self.if_exists_variable(condition)
            elif type == 'if_not_exists_variable':
                return self.if_not_exists_variable(condition)

    def if_selector(self, condition):
        selector = condition['if_selector']
        try:
            if self.doc.find_element_by_xpath(selector) is not None:
                return condition['if']
            elif 'else' in condition:
                return condition['else']
            else:
                return None
        except NoSuchElementException as e:
            self.logger.set_error_log('(if_selector) NoSuchElementException: ' + str(e))
            if 'else' in condition:
                return condition['else']
            else:
                return None

    def if_not_selector(self, condition):
        selector = condition['if_not_selector']
        try:
            if self.doc.find_element_by_xpath(selector) is None:
                return condition['if']
            elif 'else' in condition:
                return condition['else']
            else:
                return None
        except NoSuchElementException as e:
            self.logger.set_error_log('(if_not_selector) NoSuchElementException: ' + str(e))
            return condition['if']

    def if_exists_variable(self, condition):
        try:
            if VariableHelpers().is_exists_variable(condition['variable_name']):
                return condition['if']
            elif 'else' in condition:
                return condition['else']
            else:
                return None
        except Exception as e:
            self.logger.set_error_log('Error if_exists_variable: ' + str(e))
            if 'else' in condition:
                return condition['else']
            else:
                return None

    def if_not_exists_variable(self, condition):
        try:
            self.logger.set_log('if_not_exists_variable')
            if VariableHelpers().is_exists_variable(condition['variable_name']) is not True:
                return condition['if']
            elif 'else' in condition:
                return condition['else']
            else:
                return None
        except Exception as e:
            self.logger.set_error_log('Error if_exists_variable: ' + str(e))
            if 'else' in condition:
                return condition['else']
            else:
                return None

    def if_variable_not_null(self, condition):
        try:
            if VariableHelpers().is_exists_variable(condition['variable_name']):
                return condition['if']
            elif 'else' in condition:
                return condition['else']
            else:
                return None
        except Exception as e:
            self.logger.set_error_log('Error if_exists_variable: ' + str(e))
            if 'else' in condition:
                return condition['else']
            else:
                return None


