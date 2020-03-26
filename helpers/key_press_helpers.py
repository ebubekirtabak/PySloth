
from selenium.webdriver.common.keys import Keys

from PySloth.logger import Logger


class KeyPressHelpers:

    def __init__(self, driver):
        self.driver = driver
        self.logger = Logger()
        self.key_list = {}
        self.init_key_list()

    def init_key_list(self):
        self.key_list = {
            "ADD": Keys.ADD,
            "ALT": Keys.ALT,
            "ARROW_DOWN": Keys.ARROW_DOWN,
            "ENTER": Keys.ENTER,
        }

    def press_key(self, element, actions):

        if 'keys' in actions:
            keys = actions["keys"]
            for key in keys:
                Logger().set_log("Pressing key: " + key)
                key_code = self.get_key_code(key)
                element.send_keys(key_code)

    def get_key_code(self, key):
        return self.key_list[key]
