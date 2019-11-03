import sys
from collections import namedtuple

from selenium.common.exceptions import NoSuchElementException
from logger import Logger


class FormHelpers:

    def __init__(self, driver):
        self.driver = driver

    def submit_form(self, form):
        try:
            form = namedtuple("FormModel", form.keys())(*form.values())
            for input in form.inputs:
                input = namedtuple("InputModel", input.keys())(*input.values())
                input_element = self.driver.find_element_by_xpath(input.selector)
                input_element.click()
                input_element.send_keys(input.value)

            submit = self.driver.find_element_by_xpath(form.submit['selector'])
            submit.click()
        except NoSuchElementException as e:
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                print('Error %s: %s' % (value.filename, value.strerror))
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

            Logger().set_error_log('submit_form() -> ' + str(e), True)

