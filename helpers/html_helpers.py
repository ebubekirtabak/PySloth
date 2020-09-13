from helpers.variable_helpers import VariableHelpers
from logger import Logger
from services.script_runner_service import ScriptRunnerService
from transactions.mongo_transactions import MongoTransactions


class HtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.scope_model = scope.scope
        self.keep_elements = {}
        self.logger = Logger()
        self.driver = None

    def parse_html_page(self, doc, script_actions):
        for action in script_actions:
            if action['type'] == "database":
                value = VariableHelpers().get_value_with_function(doc, action['selector'])
                MongoTransactions(self.scope.settings.database, value).database_action_router(doc, action)
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
        elif type == 'run_custom_script':
            script_service = ScriptRunnerService(script_actions['custom_script'])
            script_service.run()
        elif type == "rerun_actions":
            self.parse_html_page(doc, self.scope_model.script_actions)
        elif type == 'quit':
            quit(0)
            exit()
