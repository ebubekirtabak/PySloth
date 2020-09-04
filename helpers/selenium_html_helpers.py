import os
import signal
import sys
import threading
import time
import json

from collections import namedtuple

import psutil as psutil
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from event_maker import EventMaker
from helpers.auto_page_helpers import AutoPageHelpers
from helpers.condition_helpers import ConditionHelpers
from helpers.cookie_helpers import CookieHelpers
from helpers.element_helpers import ElementHelpers
from helpers.form_helpers import FormHelpers
from helpers.mongo_database_helpers import MongoDatabaseHelpers
from helpers.recaptcha_helpers import RecaptchaHelpers
from helpers.variable_helpers import VariableHelpers
import logger
from models.thread_model import ThreadModel
from modules.file_module import FileModule
from services.script_runner_service import ScriptRunnerService

from logger import Logger

from helpers.key_press_helpers import KeyPressHelpers

from transactions.mongo_transactions import MongoTransactions

from PySloth.helpers.parse_html_helpers import ParseHtmlHelpers


class SeleniumHtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.scope_model = scope.scope
        self.keep_elements = {}
        self.element_helpers = ElementHelpers()
        self.logger = Logger()
        self.driver = None
        if self.scope.settings.time_out:
            try:
                kill_thread = threading.Thread(target=self.force_kill_start)
                kill_thread.start()
            except Exception as e:
                self.logger.set_log("Error: " + str(e))

    def force_kill_start(self):
        time.sleep(self.scope.settings.time_out)
        self.force_kill()

    def force_kill(self):
        self.logger.set_log("Run Force Killer", True)
        try:
            self.scope.thread_controller.stop_thread_controller()
        except Exception as e:
            self.logger.set_log("ThreadKillError: " + str(e))

        try:
            if self.driver is not None:
                self.driver.close()
        except Exception as e:
            self.logger.set_log("Driver Stop Error: " + str(e), True)

        pid = os.getpid()
        self.kill_children_processes(pid)

        os.kill(pid, signal.SIGTERM)

    def kill_children_processes(self, pid):
        try:
            parent = psutil.Process(pid)
        except psutil.NoSuchProcess as e:
            self.logger.set_log("NoSuchChildrenProcess: " + str(e))
            return

        children = parent.children(recursive=True)
        for child in children:
            child.kill()

    def parse_html_with_js(self, doc, script_actions):
        self.driver = doc
        if self.scope.settings.is_page_helper:
            AutoPageHelpers(doc).check_page_elements()

        for action in script_actions:
            if action['type'] == "database":
                value = VariableHelpers().get_value_with_function(doc, action['selector'])
                MongoTransactions(self.scope.settings.database, value).database_action_router(doc, action)
            elif action['type'] == "rerun_actions":
                self.parse_html_with_js(doc, self.scope_model.script_actions)
            elif action['type'] != "**":
                self.action_router(doc, action)
            else:
               self.parse_html_with_js(doc, script_actions)

    def action_router(self, doc, script_actions):
        event_maker = EventMaker(doc, self)
        self.logger.set_log(script_actions)
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
            self.set_variable(doc, script_actions)
        elif type == 'parse_html_list':
            values = ParseHtmlHelpers(doc, self.element_helpers).parse_html_list(doc, script_actions)
            VariableHelpers().set_variable(script_actions['variable_name'], values)
        elif type == 'switch_to_frame':
            wait(doc, 10).until(
                EC.frame_to_be_available_and_switch_to_it(doc.find_element_by_xpath(script_actions['selector'])))
        elif type == 'switch_to_parent_frame':
            doc.switch_to.default_content()
        elif type == 'run_recaptcha_helper':
            self.run_recaptcha_helper(doc)
        elif type == 'solve_rechaptcha_with_stt':
            audio_file = VariableHelpers().get_variable('audio_file')
            captcha_text = RecaptchaHelpers().solve_with_speech_to_text(audio_file['path'])
            element = doc.find_element_by_xpath("//*[@id='audio-response']")
            element.send_keys(captcha_text)
        elif type == 'run_custom_script':
            script_service = ScriptRunnerService(script_actions['custom_script'])
            script_service.run()
        elif type == 'wait_for_element_to_load':
            wait(doc, script_actions['timeout']).until(
                EC.visibility_of_any_elements_located(doc.find_element_by_xpath(script_actions['selector'])))
        elif type == 'wait_for_element':
            wait(doc, script_actions['timeout']).until(
                EC.presence_of_element_located(doc.find_element_by_xpath(script_actions['selector'])))
        elif type == 'wait_for_clickable':
            wait(doc, script_actions['timeout']).until(
                EC.element_to_be_clickable(doc.find_element_by_xpath(script_actions['selector'])))
        elif type == "condition":
            new_action = ConditionHelpers(doc, script_actions).parse_condition()
            if isinstance(new_action, list):
                self.parse_html_with_js(doc, new_action)
            elif new_action is not None:
                self.parse_html_with_js(doc, [new_action])
        elif type == "driver_event":
            self.driver_action_router(doc, script_actions)
        elif type == "database":
            value = VariableHelpers().get_value_with_function(doc, script_actions['selector'])
            MongoTransactions(self.scope.settings.database, value)\
                .database_action_router(doc, script_actions)
        elif type == "rerun_actions":
            self.parse_html_with_js(doc, self.scope_model.script_actions)
        elif type == 'quit':
            self.force_kill()
            quit(0)
            exit()

        if "after_actions" in script_actions:
            self.run_after_action(doc, script_actions["after_actions"])

    def driver_action_router(self, doc, driver_action):
        action = driver_action['action']
        if action == "navigation_back":
            doc.back()
        elif action == "refresh_page":
            doc.refresh()
            WebDriverWait(doc, 30).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete')

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
                    Logger().set_log('_run_after_action FileNotFoundError: ' + action['file'] + '', True)
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

    def set_variable(self, doc, script_actions):
        element = doc.find_element_by_xpath(script_actions['selector'])
        target = script_actions['target_attr']
        if 'variable_name' in script_actions:
            value = VariableHelpers().get_variable(script_actions['variable_name'])
        elif 'value' in script_actions:
            value = VariableHelpers().get_variable(script_actions['value'])

        if target == 'send_keys':
            for key in value:
                element.send_keys(key)
                time.sleep(0.2)
        elif target == 'key_press':
            KeyPressHelpers(doc).press_key(element, script_actions)
        else:
            doc.execute_script("arguments[0]." + target + " = '" + value + "';", element)

    def get_variable(self, doc, script_actions):
        try:
            value = ''
            if 'value' in script_actions:
                value = script_actions['value']
            elif script_actions['selector'].startswith('@'):
                # function
                value = VariableHelpers().get_value_with_function(doc, script_actions['selector'])
            else:
                elements = doc.find_elements_by_xpath(script_actions['selector'])
                if len(elements) == 1:
                    value = self.element_helpers.get_attribute_from_element(elements[0], script_actions['attribute_name'])
                elif len(elements) > 1:
                    value = []
                    for element in elements:
                        element_value = self.element_helpers.get_attribute_from_element(
                            element, script_actions['attribute_name']
                        )
                        value.append(element_value)

            if 'custom_scripts' in script_actions:
                if isinstance(value, list):
                    new_values = []
                    for val in value:
                        custom_scripts = script_actions['custom_scripts']
                        val = ScriptRunnerService(custom_scripts).get_script_result(val)
                        new_values.append(val)

                    value = new_values
                else:
                    custom_scripts = script_actions['custom_scripts']
                    value = ScriptRunnerService(custom_scripts).get_script_result(value)

            VariableHelpers().set_variable(script_actions['variable_name'], value)
        except Exception as e:
            self.logger.set_error_log("GetVariable: Error: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
        except NoSuchElementException as e:
            self.logger.set_error_log("NoSuchElementException: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

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

