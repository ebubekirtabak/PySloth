from selenium.common.exceptions import NoSuchElementException


class ConditionHelpers:

    def __init__(self, doc, action):
        self.doc = doc
        self.action = action

    def parse_condition(self):
        for condition in self.action['conditions']:
            type = condition['type']
            if type == 'if_selector':
                return self.if_selector(condition)
            elif type == 'if_not_selector':
                return self.if_not_selector(condition)

    def if_selector(self, condition):
        selector = condition['if_selector']
        try:
            if self.doc.find_element_by_xpath(selector) is not None:
                return condition['if']
            else:
                return None
        except NoSuchElementException:
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
        except NoSuchElementException:
            return condition['if']
