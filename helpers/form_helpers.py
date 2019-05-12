from collections import namedtuple


class FormHelpers:

    def __init__(self, driver):
        self.driver = driver
        pass

    def submit_form(self, form):
        form = namedtuple("FormModel", form.keys())(*form.values())
        for input in form.inputs:
            input = namedtuple("InputModel", input.keys())(*input.values())
            input_element = self.driver.find_element_by_xpath(input.selector)
            input_element.send_keys(input.value)

        submit = self.driver.find_element_by_xpath(form.submit['selector'])
        submit.click()
