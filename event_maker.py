import time

from selenium.common.exceptions import NoSuchElementException


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
                print("start_thread_error: " + str(e))

        else:
            return None

    def set_click(self, element, action):
        element.click()

    def set_scroll(self):
        return ""

    def set_style(self, element, action):
        scriptSetAttrValue = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(scriptSetAttrValue, element, 'style', action['style'])

    def set_excute_script(self, element, action):
        self.driver.execute_script(action['script'])

    def nothing(self, element, action):
        return ""


