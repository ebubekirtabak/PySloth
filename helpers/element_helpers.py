import inspect
import sys

from selenium.common.exceptions import NoSuchElementException

from logger import Logger


class ElementHelpers:

    def __init__(self):
        self.logger = Logger()

    def get_attribute_from_element(self, element, attr):
        if attr.startswith('style:'):
            return self.get_style_from_element(element, attr.split(':')[1])
        elif attr == 'text':
            return element.text
        elif attr == 'size':
            return element.size
        else:
            return element.get_attribute(attr)

    @staticmethod
    def get_style_from_element(element, attr):
        return element.value_of_css_property(attr)

    def get_element_value(self, action_object, element):
        try:
            elements = element.find_elements_by_xpath(action_object['selector'])
            if len(elements) == 1:
                value = ElementHelpers().get_attribute_from_element(elements[0], action_object['attribute_name'])
                return value
            elif len(elements) > 1:
                values = []
                for child_element in elements:
                    value = ElementHelpers().get_attribute_from_element(child_element, action_object['attribute_name'])
                    values.append(value)
                return values
            else:
                return ''

        except Exception as e:
            self.logger.set_error_log(
                str(inspect.currentframe().f_back.f_lineno) + "GetVariable: Error: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
            return ''
        except NoSuchElementException as e:
            self.logger.set_error_log(
                str(inspect.currentframe().f_back.f_lineno) + "NoSuchElementException: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
            return ''
