# -*- coding: utf-8 -*-

import os
import time
import sys
from collections import namedtuple

import kthread
import mongo

from selenium import webdriver

from helpers.selenium_html_helpers import SeleniumHtmlHelpers
from models.setting_model import SettingModel
from models.user_model import UserModel
from services.http_service import HttpServices
from controllers.thread_controller import ThreadController
from event_maker import EventMaker
from models.thread_model import ThreadModel
from modules.file_module import FileModule
from helpers.form_helpers import FormHelpers
from logger import Logger
from models.search_item_model import SearchItemModel
from helpers.url_helpers import UrlHelpers
from lxml.html import fromstring

script_dir = os.path.dirname(__file__)


class Scope:

    def __init__(self, scope, database=None):
        self.scope = scope
        self.database = database
        self.settings = self.scope.settings
        self.thread_controller = ThreadController(self.settings, self)
        self.thread_controller.clear_thread_list()
        self.http_services = HttpServices(self.settings, self.thread_controller)
        self.form_helpers = None
        self.user_model = UserModel()

        # self.scope.reporting = {"download_counter": 0, "page_count": 0}

    def start(self):
        if 'database' in self.scope.settings:
            self.database = self.select_database(self.scope.settings['database'])

        if isinstance(self.settings, SettingModel) is not True:
            self.settings = namedtuple("SettingsModel", self.scope.settings.keys())(*self.scope.settings.values())

        print('starting')
        if self.settings.role == 'main' and 'url' in self.scope.page:
            if hasattr(self.scope, 'script_actions'):
                self.call_page_with_javascript(self.scope.page['url'], None)
            else:
                self.root_search_item = self.scope.search_item
                self.call_page(self.scope.page['url'], self.scope.search_item)

    def select_database(self, database_setting):
        switcher = {
            "MongoDB": mongo.connect_database,
            "MySQL": mongo.connect_database,
            "SQL": lambda: mongo.connect_database,
        }

        func = switcher.get(database_setting['type'], lambda: "nothing")
        return func(database_setting)

    def call_page(self, url, search_item):
        if isinstance(search_item, SearchItemModel) is not True:
            search_item = namedtuple("SearchItemModel", search_item.keys())(*search_item.values())

        if 'data' in search_item:
            data = search_item.data
        else:
            data = None

        if search_item.enable_javascript is not True:
            html_content = UrlHelpers().get_page_html_content(url=url, data=data, headers=search_item.headers)
            self.parse_page(html_content, search_item)
        else:
            # javascript enable
            self.call_page_with_javascript(url, search_item)

    def call_page_with_javascript(self, url, search_item):
        # javascript is enable
        driver = self.settings.driver
        chrome_options = webdriver.ChromeOptions()
        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                chrome_options.add_argument(argument)

        if 'driver_path' in driver:
            chromedriver = driver['driver_path']
            os.environ["webdriver.chrome.driver"] = chromedriver
            driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
            driver.get(url)
            event_maker = EventMaker(driver)

            if hasattr(self.scope, 'login') and self.user_model.is_login is not True:
                self.form_helpers = FormHelpers(driver)
                for event in self.scope.login['events']:
                    event_maker.push_event(driver, event=event)

                forms = self.scope.login['forms']
                for form in forms:
                    self.form_helpers.submit_form(form)

            if hasattr(self.scope, 'script_actions'):
                selenium_html_helper = SeleniumHtmlHelpers()
                selenium_html_helper.parse_html_with_js(driver, self.scope.script_actions)

            if hasattr(self.scope, 'search_item'):
                if 'events' in search_item:
                    for event in search_item['events']:
                        event_maker.push_event(driver, event=event)

                self.parse_page(driver, search_item)

        response = driver.page_source
        doc = fromstring(response)
        doc.make_links_absolute(url)
        driver.quit()

    def parse_page(self, doc, search_item):

        for class_name in search_item.class_names:
            elements = doc.xpath(class_name)
            for element in elements:
                if "attrib" in search_item or hasattr(search_item, 'attrib'):
                    attrib = element.attrib[search_item.attrib]
                else:
                    attrib = element.attrib['href']

                if 'download_attrib' in search_item or hasattr(search_item, 'download_attrib') and search_item.download_attrib is True:
                    Logger().set_log("Added Download List: " + attrib)
                    print("Download List: " + str(self.scope.reporting["download_counter"]) + " : from page : "
                          + str(self.scope.reporting["page_count"]) + " : " + search_item.download_folder)
                    if 'headers' in search_item or hasattr(search_item, 'headers'):
                        headers = search_item.headers
                    else:
                        headers = self.root_search_item.headers

                    headers["Referer"] = attrib
                    thread_model = ThreadModel("thread_" + str(time.time()))
                    thread_model.target = 'http_service.download_image'
                    thread_model.args = {
                        "url": attrib,
                        "folder_name": search_item.download_folder,
                        "headers": headers,
                        "thread_name": thread_model.name
                    }
                    thread_model.status = "wait"
                    thread_model.type = "download_thread"
                    thread_model.start_time = 0
                    thread_model.stop_time = 0
                    self.thread_controller.add_thread(thread_model)

                    self.scope.reporting["download_counter"] += 1
                else:
                    thread_model = ThreadModel("thread_" + str(time.time()))
                    thread_model.target = 'item_loops'
                    thread_model.args = {
                        "url": attrib,
                        "thread_name": thread_model.name,
                        "for_item": search_item.for_item
                    }
                    thread_model.status = "wait"
                    thread_model.type = "item_loops"
                    thread_model.start_time = 0
                    thread_model.stop_time = 0
                    self.thread_controller.add_thread(thread_model)

            if 'search_item' in search_item:
                thread_model = ThreadModel("thread_" + str(time.time()))
                thread_model.target = 'parse_page'
                thread_model.args = {
                    "url": attrib,
                    "search_item": search_item['search_item']
                }
                thread_model.status = "wait"
                thread_model.type = "call_page"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                self.thread_controller.add_thread(thread_model)

        if hasattr(search_item, 'pagination'):
            pagination = search_item.pagination
            for pag in doc.xpath(pagination['url_class']):
                if 'if_exists_class' in pagination and doc.find_class('if_exists_class') is not None:
                    next_url = pag.attrib[pagination['attrib']]
                else:
                    next_url = pag.attrib[pagination['attrib']]
            else:
                attr_list = doc.xpath(pagination['url_class'])
                if len(attr_list) > 0:
                    next_url = attr_list[0].attrib[pagination['attrib']]
                else:
                    next_url = None

            if next_url is not None:
                next_url = next_url.replace(" ", "%20")
                self.scope.reporting["page_count"] += 1
                time.sleep(self.settings.search_time_sleep)
                thread_model = ThreadModel("thread_" + str(time.time()))
                thread_model.target = 'call_page'
                thread_model.args = {
                    "url": next_url,
                    "search_item": search_item,
                    "thread_name": thread_model.name
                }
                thread_model.status = "wait"
                thread_model.type = "call_page"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                self.thread_controller.add_thread(thread_model)

    def start_thread(self, thread_model):
        args = thread_model.args
        print(thread_model.type)
        url = args["url"]
        if self.settings.is_go_again_history is False and self.thread_controller.history_check(url) is True:
            return None
        else:
            database_setting = self.scope.settings['database']
            mongo.insert(self.database, database_setting['history_collection_name'], {"url": url})
        if thread_model.type == "item_loops":
            thread = kthread.KThread(target=self.item_loops,
                                     args=(args["url"], args["for_item"], args["thread_name"]),
                                     name=args["thread_name"])
        elif thread_model.type == "download_thread":
            thread = kthread.KThread(target=self.http_services.download_file,
                                     args=(args["url"], args["folder_name"],
                                            args["headers"], args["thread_name"]),
                                     name=args["thread_name"])
        elif thread_model.type == "call_page":
            thread = kthread.KThread(target=self.call_page,
                                     args=(args["url"], args["search_item"], args["thread_name"]),
                                     name=args["thread_name"])

        try:
            thread.start()
            if hasattr(thread_model, 'thread_referance'):
                thread_model.thread_referance = thread

            Logger().set_log("Start Thread : " + args["thread_name"])
            return thread
        except Exception as e:
            print("start_thread_error: " + str(e))
            Logger().set_error_log("start_thread_error: " + str(e))
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                print('Error %s: %s' % (value.filename, value.strerror))
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

            Logger().set_error_log("restart thread: " + args["thread_name"])
            self.thread_controller.restart_thread(args["thread_name"])

    def item_loops(self, *args):
        url = args[0]
        for_items = args[1]
        thread_name = args[2]

        html_content = UrlHelpers().get_page_html_content(url=url, data=None, headers=self.root_search_item['headers'])
        for item in for_items:
            item_list = item['item_list']
            for list_item in item_list:
                class_name = list_item['class_name']
                need_attr = list_item['need_attr']
                folder_name = item['download_folder']
                if 'custom_seperator' in item:
                    folder_sep = item['custom_seperator']

                if 'dynamic_folder' in item:
                    dynamic_folder = item['dynamic_folder']
                    if 'custom_seperator' in dynamic_folder:
                        dynamic_folder_sep = dynamic_folder['custom_seperator']
                    else:
                        dynamic_folder_sep = os.path.sep

                    if 'child_name_class' in item:
                        folder_name = get_folder_name(html_content.xpath(item['child_name_class']), dynamic_folder_sep, folder_name)

                    folder_name = folder_name.replace("${os.sep}", folder_sep)

                i = 0
                elements = html_content.xpath(class_name)
                if len(elements) == 0:
                    Logger().set_error_log("The \"" + class_name + "\" class was not found at \""
                                            + url + "\".")

                for element in elements:  # get element list
                    if need_attr['if'] in element.attrib:
                        attrib = element.attrib[need_attr['if']]
                    else:
                        attrib = element.attrib[need_attr['else']]

                    try:
                        Logger().set_log("Added Download List: " + url)
                        print("Download List: " + str(self.scope.reporting["download_counter"]) + " : from page : " + str(self.scope.reporting["page_count"]) + " : " + folder_name)
                        if 'headers' in item:
                            headers = item['headers']
                        else:
                            headers = self.root_search_item['headers']

                        headers['Referer'] = url
                        thread_model = ThreadModel("thread_" + str(time.time()))
                        thread_model.target = 'http_service.download_image'
                        thread_model.args = {
                            "url": attrib,
                            "folder_name": folder_name,
                            "headers": headers,
                            "thread_name": thread_model.name
                        }
                        thread_model.status = "wait"
                        thread_model.type = "download_thread"
                        thread_model.start_time = 0
                        thread_model.stop_time = 0
                        self.thread_controller.add_thread(thread_model)

                        self.scope.reporting["download_counter"] += 1
                        time.sleep(self.settings.download_time_sleep)

                    except Exception as e:
                        print("Error: " + str(e))
                        type, value, traceback = sys.exc_info()
                        Logger().set_error_log('Error: ' + str(e))
                        if hasattr(value, 'filename'):
                            print('Error opening %s: %s' % (value.filename, value.strerror))
                            Logger().set_error_log('Error opening %s: %s' % (value.filename, value.strerror))

                        time.sleep(120)
                        if 'headers' in item:
                            headers = item['headers']
                        else:
                            headers = self.root_search_item['headers']

                        headers['Referer'] = url
                        self.http_services.download_file(attrib, folder_name, headers,
                                                         "thread_" + str(self.scope.reporting["download_counter"]))
                    i = i + 1
                    self.thread_controller.remove_thread(thread_name)


    def shutdown(self):
        print("All process is successfull ")
        Logger().set_log("scrappy is finished...")
        exit(0)

def insert_db(setting, collection, data):
    global settings
    switcher = {
        "MongoDB": mongo,
        "MySQL": mongo,
        "SQL": lambda: mongo,
    }

    func = switcher.get(setting['type'], lambda: "nothing")
    func.insert(settings['db'], collection, data)


def get_folder_name(list, iterator, folder_name):
    filter_chars = ['-', '.', '_', '?', '=']
    child_name = ''
    for element in list:
        if element.text_content().strip() not in filter_chars:
            child_name += iterator + element.text_content().strip()
    directory = os.sep + folder_name
    directory += child_name.replace(' ', iterator)

    if not os.path.isdir(directory):
        path = script_dir
        for folder in directory.split(os.sep):
            path += folder + os.sep
            if not os.path.isdir(path):
                os.mkdir(path)
    return directory
