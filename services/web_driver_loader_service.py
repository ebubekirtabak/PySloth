import os

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from web_driver_services.chrome_auth_proxy_service import ChromeAuthProxyService


class WebDriverLoderService:

    def __init__(self, driver_options):
        self.driver_options = driver_options

    def init_web_driver(self):
        if 'driver_type' in self.driver_options:
            type = self.driver_options['driver_type']
        else:
            type = 'chrome'

        if type == 'chrome':
            return self.init_chrome_driver()
        elif type == 'opera':
            return self.init_opera_driver()
        elif type == 'firefox':
            return self.init_firefox_driver()

    def init_chrome_driver(self):
        driver = self.driver_options
        chrome_options = webdriver.ChromeOptions()
        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                chrome_options.add_argument(argument)

        capabilities = dict(DesiredCapabilities.CHROME)
        if 'proxy' in driver:
            capabilities['proxy'] = driver['proxy']

        if 'auth_proxy' in driver:
            proxy_extension = ChromeAuthProxyService(driver['auth_proxy']).init_proxy()
            chrome_options.add_extension(proxy_extension)

        if 'driver_path' in driver:
            chromedriver = driver['driver_path']
            os.environ["webdriver.chrome.driver"] = chromedriver
            web_driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options, desired_capabilities=capabilities)
            return web_driver
        else:
            return None

    def init_opera_driver(self, driver):
        pass
    def init_firefox_driver(self):
        driver = self.driver_options
        options = webdriver.FirefoxOptions()

        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                options.add_argument(argument)

        capabilities = dict(DesiredCapabilities.FIREFOX)
        if 'proxy' in driver:
            capabilities['proxy'] = driver['proxy']

        if 'driver_path' in driver:
            driver_path = driver['driver_path']
            os.environ["webdriver.firefox.driver"] = driver_path
            browser = webdriver.Firefox(
                executable_path=driver_path,
                firefox_options=options,
                desired_capabilities=capabilities
            )
            return browser
        else:
            return None
