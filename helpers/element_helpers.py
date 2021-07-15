import inspect
import sys

from selenium.common.exceptions import NoSuchElementException

from logger import Logger
from helpers.image_helpers import ImageHelpers


class ElementHelpers:

    def __init__(self):
        self.logger = Logger()

    def get_attribute_from_element(self, element, action_object):
        attr = action_object['attribute_name']
        if attr.startswith('style:'):
            return self.get_style_from_element(element, attr.split(':')[1])
        elif attr == 'text':
            return element.text
        elif attr == 'size':
            return element.size
        elif attr == 'src':
            return self.get_src_from_element(element, action_object)
        else:
            return element.get_attribute(attr)

    def get_src_from_element(self, element, action_object):
        attr = action_object['attribute_name']
        src = element.get_attribute(attr)
        if "as" in action_object:
            return self.encode_image(src, action_object)
        else:
            return src

    @staticmethod
    def encode_image(image_url, action_object):
        convert_type = action_object["as"]
        if convert_type == "base64":
            return ImageHelpers().encode_base64_from_url(image_url)

    @staticmethod
    def get_style_from_element(element, attr):
        return element.value_of_css_property(attr)

    def get_element_value(self, action_object, element):
        try:
            elements = element.find_elements_by_xpath(action_object['selector'])
            if len(elements) == 1:
                value = ElementHelpers().get_attribute_from_element(elements[0], action_object)
                return value
            elif len(elements) > 1:
                values = []
                for child_element in elements:
                    value = ElementHelpers().get_attribute_from_element(child_element, action_object)
                    values.append(value)
                return values
            else:
                return ''

        except Exception as e:
            self.logger.set_error_log(
                str(inspect.currentframe().f_back.f_lineno) + " GetVariable: Error: " + str(e), True)
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
