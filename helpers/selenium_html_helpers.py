import os
import re
import signal
import sys
import threading
import time
import json

from collections import namedtuple

import psutil as psutil
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from event_maker import EventMaker
from helpers.auto_page_helpers import AutoPageHelpers
from helpers.condition_helpers import ConditionHelpers
from helpers.cookie_helpers import CookieHelpers
from helpers.element_helpers import ElementHelpers
from helpers.form_helpers import FormHelpers
from helpers.http_helpers import HttpHelpers
from helpers.download_helpers import DownloadHelpers
from helpers.path_helpers import PathHelpers
from helpers.template_helpers import TemplateHelpers
from helpers.recaptcha_helpers import RecaptchaHelpers
from helpers.variable_helpers import VariableHelpers
from models.thread_model import ThreadModel
from modules.file_module import FileModule
from services.script_runner_service import ScriptRunnerService

from logger import Logger

from helpers.key_press_helpers import KeyPressHelpers

from transactions.mongo_transactions import MongoTransactions

from helpers.parse_html_helpers import ParseHtmlHelpers


class SeleniumHtmlHelpers:
    def __init__(self, scope):
        self.scope = scope
        self.scope_model = scope.scope
        self.keep_elements = {}
        self.element_helpers = ElementHelpers()
        self.logger = Logger()
        self.driver = None
        if self.scope.settings.time_out > 0:
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
                self.driver.stop_client()
                self.driver.close()
        except Exception as e:
            self.logger.set_log("Driver Stop Exception: " + str(e), True)

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
                value = self.get_database_action_value(doc, action)
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
            if script_actions['to'].startswith("${"):
                params_name = re.search("{(.*?)}", script_actions['to'])
                param_value = VariableHelpers().get_variable(params_name.group(1))
                doc.get(param_value)
            else:
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
        elif type == '$_DELETE_VARIABLE':
            self.delete_variable(script_actions)
        elif type == '$_RENAME_VARIABLE':
            self.rename_variable(script_actions)
        elif type == '$_SET_VARIABLE':
            self.set_variable(doc, script_actions)
        elif type == 'parse_html_list':
            values = ParseHtmlHelpers(doc, self.element_helpers).parse_html_list(doc, script_actions)
            VariableHelpers().set_variable(script_actions['variable_name'], values)
        elif type == "import_script_actions":
            self.import_script_actions(doc, script_actions)
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
        elif type == 'http_request':
            HttpHelpers().send_request(script_actions["request"])
        elif type == '$_FORMAT_VARIABLE':
            self.format_variable(script_actions)
        elif type == 'download_file':
            DownloadHelpers(doc).download(script_actions)
        elif type == 'type_keys':
            self.type_keys(doc, script_actions)
        elif type == 'wait_for_element_to_load':
            self.wait_for(doc, script_actions, EC.visibility_of_any_elements_located)
        elif type == 'wait_for_element':
            self.wait_for(doc, script_actions, EC.presence_of_element_located)
        elif type == 'wait_for_clickable':
            self.wait_for(doc, script_actions, EC.element_to_be_clickable)
        elif type == "condition":
            new_action = ConditionHelpers(doc, script_actions).parse_condition()
            if isinstance(new_action, list):
                self.parse_html_with_js(doc, new_action)
            elif new_action is not None:
                self.parse_html_with_js(doc, [new_action])
        elif type == "driver_event":
            self.driver_action_router(doc, script_actions)
        elif type == "database":
            value = self.get_database_action_value(doc, script_actions)
            MongoTransactions(self.scope.settings.database, value)\
                .database_action_router(doc, script_actions)
        elif type == "rerun_actions":
            self.parse_html_with_js(doc, self.scope_model.script_actions)
        elif type == 'quit':
            self.force_kill()
            quit(0)
            exit()

        # event* runs its own after_actions per row, inside event_loop. Running
        # them again here fires the whole block once more on the list page, with
        # the row's variables already cleared - which is how a run ended on a
        # timeout instead of moving to the next page.
        if "after_actions" in script_actions and type != "event*":
            self.run_after_action(doc, script_actions["after_actions"])

    def driver_action_router(self, doc, driver_action):
        action = driver_action['action']
        if action == "navigation_back":
            doc.back()
        elif action == "refresh_page":
            doc.refresh()
            WebDriverWait(doc, 30).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete')
        elif action == "open_in_new_tab":
            url = VariableHelpers().get_variable(driver_action['url_variable']) \
                if 'url_variable' in driver_action else driver_action.get('url')
            # An empty url opens about:blank, where the wait that follows can
            # only time out - and that error would end the whole run. Skip
            # instead and let the scope's own condition decide what to do.
            if not isinstance(url, str) or not url.strip():
                self.logger.set_log('open_in_new_tab: no url, skipping')
                return
            url = url.strip()
            doc.execute_script("window.open(arguments[0], '_blank');", url)
            self.switch_to_new_tab(doc, driver_action.get('timeout', 15))
        elif action == "switch_to_new_tab":
            # A click opened a new tab (e.g. a Temu order detail); wait for it
            # and move to the most recently opened window.
            self.switch_to_new_tab(doc, driver_action.get('timeout', 15))
        elif action == "close_tab":
            doc.close()
            # Back to the last remaining tab, so nested tabs unwind LIFO
            # (transactions tab -> order tab -> list tab).
            if doc.window_handles:
                doc.switch_to.window(doc.window_handles[-1])
        elif action == "switch_to_last_tab":
            # Re-anchor after a submit that closed or replaced the current tab:
            # without it every later command dies with "no such window", which
            # aborts the whole run rather than the current row.
            if doc.window_handles:
                doc.switch_to.window(doc.window_handles[-1])

    def switch_to_new_tab(self, doc, timeout=15):
        """Switches to the most recently opened tab.

        The count is taken here, after the click that opened the tab, so the new
        window is usually already present: waiting for one MORE than the current
        count waits for a second tab that never comes. What is waited for is a
        tab other than the current one, which covers both the tab that is
        already there and the one still opening."""
        current = doc.current_window_handle
        try:
            wait(doc, timeout).until(
                lambda driver: driver.window_handles[-1] != current)
        except TimeoutException:
            self.logger.set_log('switch_to_new_tab: no other tab appeared')
            return
        doc.switch_to.window(doc.window_handles[-1])

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
                self.import_script_actions(doc, action)
            else:
                self.action_router(doc, action)

    def format_variable(self, script_actions):
        """Builds a string from a template and stores it: URLs assembled from a
        setting and a scraped value, without either living in the scope file."""
        VariableHelpers().set_variable(
            script_actions['variable_name'],
            TemplateHelpers.render(script_actions.get('template', ''))
        )

    def type_keys(self, doc, script_actions):
        """Types into whatever holds focus, one character at a time, as real key
        events.

        Deliberately selector-free: a field inside a shadow root cannot be
        addressed by XPath, but JS can focus it, and keystrokes follow focus.
        Some inputs also only trust real typing — a value assigned through the
        native setter is rejected where the same text typed by hand validates —
        which is the reason this exists at all.

        keys_after names trailing keys ("SPACE", "BACK_SPACE", "ESCAPE"): adding
        a character and deleting it again is what makes such a field revalidate.
        """
        value = script_actions.get('value')
        if 'variable_name' in script_actions:
            stored = VariableHelpers().get_variable(script_actions['variable_name'])
            value = '' if stored is None else str(stored)
        value = TemplateHelpers.render(value or '')

        delay = script_actions.get('key_delay', 0.1)
        target = doc.switch_to.active_element

        if 'selector' in script_actions:
            found = doc.find_elements_by_xpath(script_actions['selector'])
            if not found:
                self.logger.set_log('type_keys: selector matched nothing')
                return
            target = found[0]

        for character in value:
            target.send_keys(character)
            time.sleep(delay)

        for key_name in script_actions.get('keys_after', []):
            key = getattr(Keys, key_name.upper(), None)
            if key is None:
                self.logger.set_log('type_keys: no such key ' + str(key_name))
                continue
            target.send_keys(key)
            time.sleep(delay)

        self.logger.set_log('type_keys: typed %d characters' % len(value))

    def wait_for(self, doc, script_actions, condition):
        """Waits for a selector. The expected conditions take a (By, selector)
        locator: looking the element up first raises when it is not there yet,
        which is exactly what the wait was supposed to absorb.

        "optional": true keeps a run going when an element legitimately never
        appears (an order with no invoice modal, say) instead of aborting."""
        try:
            wait(doc, script_actions['timeout']).until(
                condition((By.XPATH, script_actions['selector'])))
        except TimeoutException:
            if not script_actions.get('optional'):
                raise
            self.logger.set_log(
                f"wait_for ({script_actions.get('type', 'wait_for')}, optional) timed out: {script_actions['selector']}" )

    def import_script_actions(self, doc, action):
        file = FileModule().read_file(file_name=PathHelpers.resolve(action['file']))
        if file['success'] is True:
            scope_data = json.loads(file['data'])
            scope_model = namedtuple("ScopeModel", scope_data.keys())(*scope_data.values())
            if hasattr(scope_model, 'script_actions'):
                self.parse_html_with_js(doc, scope_model.script_actions)
        else:
            Logger().set_log('_run_after_action FileNotFoundError: ' + action['file'] + '', True)

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

    @staticmethod
    def get_database_action_value(doc, script_actions):
        if 'selector' in script_actions:
            return VariableHelpers().get_value_with_function(doc, script_actions['selector'])
        if 'variable_names' in script_actions:
            value = {}
            for key in script_actions["variable_names"]:
                value[key["key"]] = VariableHelpers().get_variable(key["value"])

            return value

        else:
            return VariableHelpers().get_variable(script_actions['variable_name'])

    @staticmethod
    def delete_variable(script_actions):
        VariableHelpers().delete_variable(script_actions['variable_name'])

    @staticmethod
    def rename_variable(script_actions):
        VariableHelpers().rename_variable(script_actions['variable_name'], script_actions['variable_new_name'])

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
                    value = self.element_helpers.get_attribute_from_element(elements[0], script_actions)
                elif len(elements) > 1:
                    value = []
                    for element in elements:
                        element_value = self.element_helpers.get_attribute_from_element(
                            element, script_actions
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

