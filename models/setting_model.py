class SettingModel:
    def __init__(self, driver, database, multi_process, history, role, file_settings,
                 is_go_again_history, clarifia_api_key, is_page_helper, time_out):
        self.driver = driver
        self.database = database
        self.multi_process = multi_process
        self.history = history
        self.role = role
        self.file_settings = file_settings
        self.is_go_again_history = is_go_again_history
        self.is_page_helper = is_page_helper
        self.clarifia_api_key = clarifia_api_key
        self.time_out = time_out

