import time
import json

from collections import namedtuple
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import logger
from event_maker import EventMaker
from helpers.auto_page_helpers import AutoPageHelpers
from helpers.condition_helpers import ConditionHelpers
from helpers.cookie_helpers import CookieHelpers
from helpers.element_helpers import ElementHelpers
from helpers.form_helpers import FormHelpers
from helpers.mongo_database_helpers import MongoDatabaseHelpers
from helpers.recaptcha_helpers import RecaptchaHelpers
from helpers.variable_helpers import VariableHelpers
from models.thread_model import ThreadModel
from modules.file_module import FileModule


class SeleniumHtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.scope_model = scope.scope
        self.keep_elements = {}

    def parse_html_with_js(self, doc, script_actions):
        AutoPageHelpers(doc).check_page_elements()
        for action in script_actions:
            if action['type'] == "condition":
                new_action = ConditionHelpers(doc, action).parse_condition()
                if isinstance(new_action, list):
                    for action_item in new_action:
                        self.action_router(doc, action_item)
                elif new_action is not None:
                    self.action_router(doc, new_action)
            elif action['type'] == "database":
                self.database_action_router(doc, action)
            elif action['type'] == "rerun_actions":
                self.parse_html_with_js(doc, script_actions)
            elif action['type'] != "**":
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
            form_helpers = FormHelpers(doc)
            form_helpers.submit_form(script_actions)
        elif type == 'save_cookie':
            cookie_helpers = CookieHelpers(doc, self.scope)
            cookie_helpers.save_cookie(script_actions)
        elif type == 'load_cookie_from_database':
            cookie_helpers = CookieHelpers(doc, self.scope)
            cookie_helpers.load_cookie_from_database()
        elif type == 'clear_variables':
            VariableHelpers().load_scope_variables()
        elif type == '$_GET_VARIABLE':
            self.get_variable(doc, script_actions)
        elif type == '$_SET_VARIABLE':
            element = doc.find_element_by_xpath(script_actions['selector'])
            target = script_actions['target_attr']
            value = VariableHelpers().get_variable(script_actions['variable_name'])
            if target == 'send_keys':
                for key in value:
                    element.send_keys(key)
                    time.sleep(0.2)
            else:
                doc.execute_script("arguments[0]." + target + " = '" + value + "';", element)
        elif type == 'parse_html_list':
            values = self.parse_html_list(doc, script_actions)
            VariableHelpers().set_variable(script_actions['variable_name'], values)
        elif type == 'switch_to_frame':
            frame = doc.find_element_by_xpath(script_actions['selector'])
            doc.switch_to.frame(frame)
        elif type == 'switch_to_parent_frame':
            doc.switch_to.default_content()
        elif type == 'run_recaptcha_helper':
            self.run_recaptcha_helper(doc)
        elif type == 'solve_rechaptcha_with_stt':
            audio_file = VariableHelpers().get_variable('audio_file')
            captcha_text = RecaptchaHelpers().solve_with_speech_to_text(audio_file['path'])
            element = doc.find_element_by_xpath("//*[@id='audio-response']")
            element.send_keys(captcha_text)
        elif type == "driver_event":
            self.driver_action_router(doc, script_actions)
        elif type == "rerun_actions":
            self.parse_html_with_js(doc, self.scope_model.script_actions)
        elif type == 'quit':
            self.scope.thread_controller.stop_thread_controller()
            quit(0)

    def driver_action_router(self, doc, driver_action):
        action = driver_action['action']
        if action == "navigation_back":
            doc.back()
        elif action == "refresh_page":
            doc.refresh()

    def database_action_router(self, doc, database_action):
        action = database_action['action']
        database = self.scope.settings.database
        value = VariableHelpers().get_value_with_function(database_action['selector'])
        collection_name = database_action['collection_name']
        if ':' in database_action['collection_name']:
            selector_items = database_action['collection_name'].split(':')
            collection_name = selector_items[0]
            value = value[selector_items[1]]

        if action == "push_to_database":
            MongoDatabaseHelpers(database).insert(
                collection_name,
                value
            )
        elif action == 'push_array_to_database':
            MongoDatabaseHelpers(database).insert_many(
                collection_name,
                value
            )

    def event_loop(self, doc, action):
        event_maker = EventMaker(doc, self)
        element_list = doc.find_elements_by_xpath(action['selector'])
        index = 0
        while index < len(element_list):
            element_list = doc.find_elements_by_xpath(action['selector'])
            element = element_list[index]
            if self.is_not_exists_element(element.id, action):
                event_maker.push_event_to_element(element, action['events'])
                if "after_actions" in action:
                    self.run_after_action(doc, action["after_actions"])
            index += 1

    def run_after_action(self, doc, actions):
        for action in actions:
            type = action['type']
            if type == "import_script_actions":
                file = FileModule().read_file(file_name=action['file'])
                if file['success'] is True:
                    scope_data = json.loads(file['data'])
                    scope_model = namedtuple("ScopeModel", scope_data.keys())(*scope_data.values())
                    if hasattr(scope_model, 'script_actions'):
                        self.parse_html_with_js(doc, scope_model.script_actions)
                else:
                    print('FileNotFoundError: ' + action['file'] + '')
            else:
                self.action_router(doc, action)

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
            url = element.get_attribute(download['download_attribute'])
            thread_model = ThreadModel("thread_" + str(time.time()))
            thread_model.target = 'http_service.download_image'
            thread_model.args = {
                "url": url,
                "folder_name": download['download_folder'],
                "headers": download['headers'],
                "thread_name": thread_model.name,
                "file_referance": download['file_referance'],
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

    def parse_html_list(self, doc, action):
        selected_elements = doc.find_elements_by_xpath(action['selector'])
        parse_list = []
        index = 0
        for element in selected_elements:
            parse_list.append({})
            for action_object in action['object_list']:
                value = self.get_object_value(action_object, element)
                parse_list[index][action_object['variable_name']] = value
            index = index + 1

        return parse_list

    def get_object_value(self, action_object, element):
        if action_object['type'] == 'parse_html_list':
            value = self.parse_html_list(element, action_object)
            return value
        else:
            value = self.get_element_value(action_object, element)
            return value

    def get_element_value(self, action_object, element):
        try:
            elements = element.find_elements_by_xpath(action_object['selector'])
            values = []
            for child_element in elements:
                value = ElementHelpers().get_attribute_from_element(child_element, action_object['attribute_name'])
                values.append(value)
            return values

        except Exception as e:
            logger.Logger().set_error_log("GetVariable: Error: " + str(e), True)
            return ''
        except NoSuchElementException as e:
            logger.Logger().set_error_log("NoSuchElementException: " + str(e), True)
            return ''

    @staticmethod
    def get_variable(doc, script_actions):
        try:
            if 'value' in script_actions:
                VariableHelpers().set_variable(
                    script_actions['variable_name'],
                    script_actions['value'])
            elif script_actions['selector'].startswith('@'):
                # function
                value = VariableHelpers().get_value_with_function(script_actions['selector'])
                VariableHelpers().set_variable(script_actions['variable_name'], value)
            else:
                elements = doc.find_elements_by_xpath(script_actions['selector'])
                index = 0
                for element in elements:
                    value = ElementHelpers().get_attribute_from_element(element, script_actions['attribute_name'])
                    VariableHelpers().set_variable(script_actions['variable_name'] + '[' + str(index) + ']', value)
                    index = index + 1
        except Exception as e:
            logger.Logger().set_error_log("GetVariable: Error: " + str(e), True)
        except NoSuchElementException as e:
            logger.Logger().set_error_log("NoSuchElementException: " + str(e), True)

    @staticmethod
    def get_attribute_from_element(element, attribute):
        try:
            index = ['text', 'html'].index(attribute)
            return element.text
        except:
            return element.get_attribute(attribute)

    def run_recaptcha_helper(self, doc):
        image_url = VariableHelpers().get_variable('recaptcha_image')
        keyword = VariableHelpers().get_variable('recaptcha_keyword')
        size = VariableHelpers().get_variable('size')
        image_size = VariableHelpers().get_variable('image_size')
        image_results = RecaptchaHelpers().solve_captcha(image_url, keyword, size, self.scope.settings.clarifia_api_key,
                                                         image_size)
        table_rows = doc.find_elements_by_xpath("//div[@class='rc-imageselect-target']/table/tbody/tr")
        for result in image_results:
            if result['is_exists']:
                print('W: ' + str(result['w']) + ' h: ' + str(result['h']))
                row = table_rows[result['h']]
                columns = row.find_elements_by_xpath("./td[@role='button']")
                column = columns[result['w']]
                column.click()

        time.sleep(2)
        verify_button = doc.find_element_by_xpath("//*[@id='recaptcha-verify-button']")
        verify_button.click()

