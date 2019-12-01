class ConditionHelpers:

    def __init__(self, doc, action):
        self.doc = doc
        self.action = action

    def parse_condition(self):
        for condition in self.action['conditions']:
            type = condition['type']
            if type == 'if_selector':
                return self.if_selector(condition)

    def if_selector(self, condition):
        selector = condition['if_selector']
        if self.doc.find_element_by_xpath(selector) is not None:
            return condition['if']
        else:
            return None
