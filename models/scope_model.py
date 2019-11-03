from models.login_model import LoginModel
from models.script_action_model import ScriptActionModel


class ScopeModel:

    def __init__(self, settings, search_item, page, reporting, login: LoginModel, script_actions: [ScriptActionModel],
                 before_actions: [ScriptActionModel]):
        self.settings = settings
        self.search_item = search_item
        self.page = page
        self.reporting = reporting
        self.login = login
        self.before_actions = before_actions
        self.script_actions = script_actions
