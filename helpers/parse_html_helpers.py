import sys
from PySloth.event_maker import EventMaker
from PySloth.logger import Logger
from PySloth.services.script_runner_service import ScriptRunnerService


class ParseHtmlHelpers:

    def __init__(self, driver, element_helpers):
        self.driver = driver
        self.element_helpers = element_helpers

    def parse_html_list(self, parent, action):
        try:
            selected_elements = parent.find_elements_by_xpath(action['selector'])
            parse_list = []
            index = 0
            for element in selected_elements:
                parse_list.append({})
                for action_object in action['object_list']:
                    value = self.get_object_value(action_object, element)

                    if value is not None:
                        if 'custom_scripts' in action_object:
                            custom_scripts = action_object['custom_scripts']
                            if isinstance(value, list):
                                new_values = []
                                for val in value:
                                    val = ScriptRunnerService(custom_scripts).get_script_result(val)
                                    new_values.append(val)

                                value = new_values
                            else:
                                value = ScriptRunnerService(custom_scripts).get_script_result(value)

                        parse_list[index][action_object['variable_name']] = value

                index = index + 1

            return parse_list
        except Exception as e:
            Logger().set_log('ParseHtmlListException: ' + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

    def parse_element_action(self, action_object, element):
        event_maker = EventMaker(self.driver, self)
        if action_object['type'] == 'event*':
            event_maker.push_event(element, action_object)
        return None

    def get_object_value(self, action_object, element):
        if action_object['type'] == 'parse_html_list':
            value = self.parse_html_list(element, action_object)
            return value
        elif action_object['type'] == "event*":
            return self.parse_element_action(action_object, element)
        else:
            value = self.element_helpers.get_element_value(action_object, element)
            return value