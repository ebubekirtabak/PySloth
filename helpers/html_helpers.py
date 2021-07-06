from helpers.condition_helpers import ConditionHelpers
from helpers.http_helpers import HttpHelpers
from helpers.lxml_element_helpers import LXMLElementHelpers
from helpers.parse_html_helpers import ParseHtmlHelpers
from helpers.parse_lxml_helpers import ParseLxmlHelpers
from helpers.variable_helpers import VariableHelpers
from logger import Logger
from services.script_runner_service import ScriptRunnerService
from transactions.mongo_transactions import MongoTransactions


class HtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.scope_model = scope
        self.keep_elements = {}
        self.logger = Logger()
        self.element_helpers = LXMLElementHelpers()
        self.driver = None

    def parse_html_page(self, doc, script_actions):
        for action in script_actions:
            if action['type'] == "database":
                value = VariableHelpers().get_value_with_function(doc, action['selector'])
                MongoTransactions(self.scope.settings["database"], value).database_action_router(doc, action)
            elif action['type'] != "**":
                self.action_router(doc, action)
            else:
                self.parse_html_page(doc, script_actions)

    def action_router(self, doc, script_actions):
        type = script_actions['type']
        if type == 'clear_variables':
            VariableHelpers().load_scope_variables()
        elif type == '$_GET_VARIABLE':
            self.get_variable(doc, script_actions)
        elif type == '$_DELETE_VARIABLE':
            self.delete_variable(script_actions)
        elif type == '$_RENAME_VARIABLE':
            self.rename_variable(script_actions)
        elif type == 'parse_html_list':
            values = ParseLxmlHelpers(doc, self.element_helpers).parse_lxml_list(doc, script_actions)
            VariableHelpers().set_variable(script_actions['variable_name'], values)
        elif type == 'run_custom_script':
            script_service = ScriptRunnerService(script_actions['custom_script'])
            script_service.run()
        elif type == 'http_request':
            HttpHelpers().send_request(script_actions["request"])
        elif type == "condition":
            new_action = ConditionHelpers(doc, script_actions).parse_condition()
            if isinstance(new_action, list):
                self.parse_html_page(doc, new_action)
            elif new_action is not None:
                self.parse_html_page(doc, [new_action])
        elif type == "rerun_actions":
            self.parse_html_page(doc, self.scope_model.script_actions)
        elif type == 'quit':
            quit(0)
            exit()

    @staticmethod
    def delete_variable(script_actions):
        VariableHelpers().delete_variable(script_actions['variable_name'])

    @staticmethod
    def rename_variable(script_actions):
        VariableHelpers().rename_variable(script_actions['variable_name'], script_actions['variable_new_name'])

    def get_variable(self, doc, script_actions):
        try:
            value = ''
            if 'value' in script_actions:
                value = script_actions['value']
            elif script_actions['selector'].startswith('@'):
                # function
                value = VariableHelpers().get_value_with_function(doc, script_actions['selector'])
            else:
                elements = doc.xpath(script_actions['selector'])
                if len(elements) == 1:
                    value = self.element_helpers.get_attribute_from_element(elements[0], script_actions)
                elif len(elements) > 1:
                    value = []
                    for element in elements:
                        element_value = self.element_helpers.get_attribute_from_element(
                            element, script_actions
                        )
                        value.append(element_value)

            if 'custom_scripts' in script_actions:
                if isinstance(value, list):
                    new_values = []
                    for val in value:
                        custom_scripts = script_actions['custom_scripts']
                        val = ScriptRunnerService(custom_scripts).get_script_result(val)
                        new_values.append(val)

                    value = new_values
                else:
                    custom_scripts = script_actions['custom_scripts']
                    value = ScriptRunnerService(custom_scripts).get_script_result(value)

            VariableHelpers().set_variable(script_actions['variable_name'], value)
        except Exception as e:
            self.logger.set_error_log("GetVariable: Error: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
        except NoSuchElementException as e:
            self.logger.set_error_log("NoSuchElementException: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

