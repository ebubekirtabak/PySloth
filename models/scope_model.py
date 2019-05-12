from models.login_model import LoginModel


class ScopeModel:

    def __init__(self, settings, search_item, page, reporting, login: LoginModel):
        self.settings = settings
        self.search_item = search_item
        self.page = page
        self.reporting = reporting
        self.login = login
