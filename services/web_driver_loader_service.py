import os

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities


class WebDriverLoderService:

    def __init__(self, driver_options):
        self.driver_options = driver_options

    def init_web_driver(self):
        type = self.driver_options['driver_type']
        if type == 'chrome':
            return self.init_chrome_driver()
        elif type == 'opera':
            return self.init_opera_driver()

    def init_chrome_driver(self):
        driver = self.driver_options
        chrome_options = webdriver.ChromeOptions()
        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                chrome_options.add_argument(argument)

        capabilities = dict(DesiredCapabilities.CHROME)
        if 'proxy' in driver:
            capabilities['proxy'] = driver['proxy']

        if 'driver_path' in driver:
            chromedriver = driver['driver_path']
            os.environ["webdriver.chrome.driver"] = chromedriver
            web_driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options, desired_capabilities=capabilities)
            return web_driver
        else:
            return None

    def init_opera_driver(self, driver):
        pass
