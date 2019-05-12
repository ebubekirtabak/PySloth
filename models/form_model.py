
class InputModel:

    def __init__(self, selector, value):
        self.selector = selector
        self.value = value


class FormModel:

    def __init__(self, inputs: InputModel, submit):
        self.inputs = inputs
        self.submit = submit


