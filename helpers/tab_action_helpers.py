class TabActionHelpers:

    def __init__(self, driver):
        self.driver = driver

    def run_tab_action(self, action):
        self.tab_action_router(action)

    def tab_action_router(self, action):
        type = action["action"]
        if type == "close":
            self.close_tab(action)

    def close_tab(self, action):
        close_index = action["close_index"]
        switch_to_index = action["switch_to_index"]
        switch_tab = self.driver.window_handles[switch_to_index]
        close_tab = self.driver.window_handles[close_index]
        self.driver.switch_to.window(close_tab)
        self.driver.close()
        self.driver.switch_to.window(switch_tab)
