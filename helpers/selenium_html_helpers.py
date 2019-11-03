import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from event_maker import EventMaker
from helpers.form_helpers import FormHelpers
from helpers.variable_helpers import VariableHelpers
from models.thread_model import ThreadModel


class SeleniumHtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.keep_elements = {}

    def parse_html_with_js(self, doc, script_actions):
        for action in script_actions:
            if action['type'] != "**":
                self.action_router(doc, action)
            else:
               WebDriverWait(doc, 30).until(
                    expected_conditions.invisibility_of_element_located((By.ID, 'ajax_loader'))
               )
               self.parse_html_with_js(doc, script_actions)

    def action_router(self, doc, script_actions):
        event_maker = EventMaker(doc, self)
        type = script_actions['type']
        if type == "event*":
            self.event_loop(doc, script_actions)
        elif type == 'navigate_to':
            doc.get(script_actions['to'])
        elif type == "download_loop":
            self.download_loop(doc, script_actions)
        elif type == "event":
            event_maker.push_event(doc, script_actions)
        elif type == "excute_script":
            event_maker.push_event(doc, script_actions)
        elif type == "function":
            event_maker.push_event(doc, script_actions)
        elif type == "form":
            self.form_helpers = FormHelpers(doc)
            self.form_helpers.submit_form(script_actions)
        elif type == '$_GET_VARIABLE':
            if 'value' in script_actions:
                VariableHelpers().set_variable(
                    script_actions['variable_name'],
                    script_actions['value'])
            else:
                element = doc.find_element_by_xpath(script_actions['selector'])
                VariableHelpers().set_variable(script_actions['variable_name'], element.get_attribute(script_actions['attribute_name']))
        elif type == '$_SET_VARIABLE':
            element = doc.find_element_by_xpath(script_actions['selector'])
            target = script_actions['target_attr']
            value = VariableHelpers().get_variable(script_actions['variable_name'])
            if target == 'send_keys':
                element.send_keys(value)
            else:
                doc.execute_script("arguments[0]." + target + " = '" + value + "';", element)

    def event_loop(self, doc, action):
        event_maker = EventMaker(doc, self)
        elements = doc.find_elements_by_xpath(action['selector'])
        for element in elements:
            if self.is_not_exists_element(element.id, action):
                event_maker.push_event_to_element(element, action['events'])

    def download_loop(self, doc, action):
        if 'selector' in action:
            elements = doc.find_elements_by_xpath(action['selector'])
        elif 'selectors' in action:
            elements = []
            for selector in action['selectors']:
                selector_elements = doc.find_elements_by_xpath(selector)
                elements = elements + selector_elements

        for element in elements:
            download = action['download']
            '''if 'is_wait_for_load_element' in action and action['is_wait_for_load_element'] is True:
                WebDriverWait(self.doc, 30).until(
                    expected_conditions.invisibility_of_element_located(element)
                )'''

            url = element.get_attribute(download['download_attribute'])
            thread_model = ThreadModel("thread_" + str(time.time()))
            thread_model.target = 'http_service.download_image'
            thread_model.args = {
                "url": url,
                "folder_name": download['download_folder'],
                "headers": download['headers'],
                "thread_name": thread_model.name
            }
            thread_model.status = "wait"
            thread_model.type = "download_thread"
            thread_model.start_time = 0
            thread_model.stop_time = 0
            self.scope.thread_controller.add_thread(thread_model)

    def is_not_exists_element(self, id, event):
        if 'keep_element_id' in event:
            if event['keep_element_id'] in self.keep_elements:
                element_list = self.keep_elements[event['keep_element_id']]
                if id in element_list:
                    return False
                else:
                    self.keep_elements[event['keep_element_id']].append(id)
                    return True
            else:
                self.keep_elements[event['keep_element_id']] = []
                self.keep_elements[event['keep_element_id']].append(id)
                return True
        else:
            return True

