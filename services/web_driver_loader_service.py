import os

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome import webdriver


class WebDriverLoderService:

    def __init__(self, driver_options):
        self.driver_options = driver_options

    def init_web_driver(self):
        type = self.driver_options['driver_type']
        if type == 'chrome':
            return self.init_chrome_driver(self.driver_options)
        elif type == 'opera':
            return self.init_opera_driver(self.driver_options)

    def init_chrome_driver(self):
        driver = self.driver_options
        chrome_options = webdriver.ChromeOptions()
        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                chrome_options.add_argument(argument)

        if 'driver_path' in driver:
            proxy = {'address': '185.195.213.132:3199'}
            capabilities = dict(DesiredCapabilities.CHROME)
            capabilities['proxy'] = {
                'proxyType': 'MANUAL',
                'httpProxy': proxy['address'],
                'ftpProxy': proxy['address'],
                'sslProxy': proxy['address'],
                'noProxy': '',
                'class': "org.openqa.selenium.Proxy",
                'autodetect': False,
                'socksUsername': 'uojvnupuj-rtf3j',
                'socksPassword': 'Ur7hX0gRmJ'
            }

            chromedriver = driver['driver_path']
            os.environ["webdriver.chrome.driver"] = chromedriver
            web_driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options, desired_capabilities=capabilities)
            return web_driver
        else:
            return None

    def init_opera_driver(self, driver):
        pass
