import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from event_maker import EventMaker
from helpers.cookie_helpers import CookieHelpers
from helpers.element_helpers import ElementHelpers
from helpers.form_helpers import FormHelpers
from helpers.recaptcha_helpers import RecaptchaHelpers
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
            form_helpers = FormHelpers(doc)
            form_helpers.submit_form(script_actions)
        elif type == 'save_cookie':
            cookie_helpers = CookieHelpers(doc, self.scope)
            cookie_helpers.save_cookie(script_actions)
        elif type == 'load_cookie_from_database':
            cookie_helpers = CookieHelpers(doc, self.scope)
            cookie_helpers.load_cookie_from_database()
        elif type == '$_GET_VARIABLE':
            if 'value' in script_actions:
                VariableHelpers().set_variable(
                    script_actions['variable_name'],
                    script_actions['value'])
            else:
                element = doc.find_element_by_xpath(script_actions['selector'])
                value = ElementHelpers().get_attribute_from_element(element, script_actions['attribute_name'])
                VariableHelpers().set_variable(script_actions['variable_name'], value)
        elif type == '$_SET_VARIABLE':
            element = doc.find_element_by_xpath(script_actions['selector'])
            target = script_actions['target_attr']
            value = VariableHelpers().get_variable(script_actions['variable_name'])
            if target == 'send_keys':
                element.send_keys(value)
            else:
                doc.execute_script("arguments[0]." + target + " = '" + value + "';", element)
        elif type == 'parse_html_list':
            self.parse_html_list(doc, script_actions)
        elif type == 'switch_to_frame':
            frame = doc.find_element_by_xpath(script_actions['selector'])
            doc.switch_to.frame(frame)
        elif type == 'switch_to_parent_frame':
            doc.switch_to.default_content()
        elif type == 'run_recaptcha_helper':
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

    def parse_html_list(self, doc, action):
        selected_elements = doc.find_elements_by_xpath(action['selector'])
        parse_list = []
        index = 0
        for element in selected_elements:
            parse_list.append({})
            for action_object in action['object_list']:
                child_element = element.find_elements_by_xpath(action_object ['selector'])[0]
                parse_list[index][action_object ['name']] = self.get_attribute_from_element(
                    child_element, action_object['attribute_name']
                )
            index = index + 1
            return parse_list

    @staticmethod
    def get_attribute_from_element(element, attribute):
        try:
            index = ['text', 'html'].index(attribute)
            return element.text
        except:
            return element.get_attribute(attribute)


