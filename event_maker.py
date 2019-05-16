import sys
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from logger import Logger


class EventMaker:

    driver = None

    def __init__(self, driver):
        self.driver = driver
        pass

    def push_event(self, driver, event):
        if driver is not None:

            try:
                element = driver.find_element_by_xpath(event['selector'])
                if element is not None:
                    if 'delay' in event:
                        time.sleep(event['delay'])

                    for action in event['actions']:
                        if 'delay' in action:
                            time.sleep(action['delay'])

                        switcher = {
                            "click": self.set_click,
                            "scroll": self.set_scroll,
                            "style": self.set_style,
                            "excute_script": self.set_excute_script,
                            "nothing": lambda: self.nothing,
                        }

                        func = switcher.get(action['type'], lambda: "nothing")
                        func(element, action)

                    if 'sleep' in event:
                        time.sleep(event['sleep'])

            except NoSuchElementException as e:
                print("-- NoSuchElementException: " + str(e))

            except Exception as e:
                print("Push Event ->: " + str(e))

        else:
            return None

    def push_event_to_element(self, element, events):
        try:
            for event in events:
                if 'delay' in event:
                    time.sleep(event['delay'])
                if 'selector' in event:
                    element = element.find_element_by_xpath(event['selector'])

                for action in event['actions']:
                    if 'delay' in action:
                        time.sleep(action['delay'])



                    switcher = {
                        "click": self.set_click,
                        "click_with_command": self.set_click_with_command,
                        "scroll": self.set_scroll,
                        "style": self.set_style,
                        "set_attr": self.set_attr,
                        "excute_script": self.set_excute_script,
                        "nothing": lambda: self.nothing,
                    }

                    func = switcher.get(action['type'], lambda: "nothing")
                    func(element, action)

                if 'sleep' in event:
                    time.sleep(event['sleep'])

        except NoSuchElementException as e:
            print("-- NoSuchElementException: " + str(e))

        except Exception as e:
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                print('Error %s: %s' % (value.filename, value.strerror))
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

            print("Push Event To Element () ->: " + str(e))

    def set_click_with_command(self, element, action):
        action = ActionChains(self.driver).key_down(Keys.CONTROL)
        action.move_to_element(element)
        action.click()
        action.perform()

    def set_click(self, element, action):
        element.click()

    def set_scroll(self):
        return ""

    def set_style(self, element, action):
        scriptSetAttrValue = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(scriptSetAttrValue, element, 'style', action['style'])

    def set_attr(self, element, action):
        scriptSetAttrValue = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(scriptSetAttrValue, element, action['attr'], action['attr_value'])

    def set_excute_script(self, element, action):
        self.driver.execute_script(action['script'])

    def nothing(self, element, action):
        return ""


