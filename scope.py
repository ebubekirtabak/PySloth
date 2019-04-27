# -*- coding: utf-8 -*-

import json
import os
import time
import urllib
import urllib.request
from collections import namedtuple

import kthread
import mongo

from selenium import webdriver

from models.setting_model import SettingModel
from services.http_service import HttpServices
from controllers.thread_controller import ThreadController
from event_maker import EventMaker
from models.thread_model import ThreadModel
from modules.file_module import FileModule
from logger import Logger
from models.search_item_model import SearchItemModel
from helpers.url_helpers import UrlHelpers
from lxml.html import fromstring

script_dir = os.path.dirname(__file__)
global scope
global page_count
global download_counter
global next_url
global settings
global database_driver


class Scope:

    def __init__(self, scope, database=None):
        self.scope = scope
        self.database = database
        self.settings = self.scope.settings
        self.root_search_item = scope.search_item
        self.thread_controller = ThreadController(self.settings, self)
        self.thread_controller.clear_thread_list()
        self.http_services = HttpServices(self.settings, self.thread_controller)

        # self.scope.reporting = {"download_counter": 0, "page_count": 0}

    def start(self):
        if 'database' in self.scope.settings:
            self.database = self.select_database(self.scope.settings['database'])

        if isinstance(self.settings, SettingModel) is not True:
            self.settings = namedtuple("SettingsModel", self.scope.settings.keys())(*self.scope.settings.values())

        print('starting')
        if self.settings.role == 'main' and 'url' in self.scope.page:
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
            print(html_content)
            self.parse_page(html_content, search_item)

    def call_page_with_javascript(self, url, search_item):
        # javascript is enable
        driver = self.settings
        chrome_options = webdriver.ChromeOptions()
        if 'driver_arguments' in driver:
            for argument in driver['driver_arguments']:
                chrome_options.add_argument(argument)

        if 'driver_path' in driver:
            chromedriver = driver['driver_path']
            os.environ["webdriver.chrome.driver"] = chromedriver
            driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
            driver.get(url)
            event_maker = EventMaker(driver);
            if 'events' in search_item:
                for event in search_item['events']:
                    event_maker.push_event(driver, event=event)

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
                        "attrib": attrib,
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
                    thread_model.target = 'get_items'
                    thread_model.args = {
                        "url": attrib, "thread_name": thread_model.name, "type": 'page'
                    }
                    thread_model.status = "wait"
                    thread_model.type = "get_items"
                    thread_model.start_time = 0
                    thread_model.stop_time = 0
                    self.thread_controller.add_thread(thread_model)

            if 'search_item' in search_item:
                thread_model = ThreadModel("thread_" + str(download_counter) + "_" + str(time.time()))
                thread_model.target = 'parse_page'
                thread_model.args = {
                    "url": attrib,
                    "search_item": search_item['search_item']
                }
                thread_model.status = "wait"
                thread_model.type = "search_page"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                self.thread_controller.add_thread(thread_model)

        if 'pagination' in search_item:
            pagination = search_item['pagination']
            for pag in doc.xpath(pagination['class']):
                if 'if_exists_class' in pagination and doc.find_class('if_exists_class') is not None:
                    next_url = pag.attrib[pagination['attrib']]
                else:
                    next_url = pag.attrib[pagination['attrib']]
            else:
                attr_list = doc.xpath(pagination['class'])
                if len(attr_list) > 0:
                    next_url = attr_list[0].attrib[pagination['attrib']]
                else:
                    next_url = None

            if next_url is not None:
                next_url = next_url.replace(" ", "%20")
                page_count += 1
                time.sleep(settings["search_time_sleep"])
                thread_model = ThreadModel("thread_" + str(time.time()))
                thread_model.target = 'call_page'
                thread_model.args = {
                    "url": next_url,
                    "search_item": search_item
                }
                thread_model.status = "wait"
                thread_model.type = "call_page"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                self.thread_controller.add_thread(thread_model)

    def start_thread(self, thread_model):
        global download_counter
        args = thread_model.args
        print(thread_model.type)
        if thread_model.type == "get_items":
            thread = kthread.KThread(target=get_items,
                                     args=(args["url"], args["thread_name"], args["type"]),
                                     name=args["thread_name"])
        elif thread_model.type == "download_thread":
            thread = kthread.KThread(target=self.http_services.download_file,
                                     args=(args["attrib"], args["folder_name"],
                                             args["headers"], args["thread_name"]),
                                     name=args["thread_name"])

        try:
            thread.start()
            Logger().set_log("Start Thread : " + args["thread_name"])
        except Exception as e:
            print("start_thread_error: " + str(e))
            Logger.set_error_log("start_thread_error: " + str(e))
            Logger.set_error_log("restart thread: " + args["thread_name"])
            self.thread_controller.restart_thread(args["thread_name"])

def insert_db(setting, collection, data):
    global settings
    switcher = {
        "MongoDB": mongo,
        "MySQL": mongo,
        "SQL": lambda: mongo,
    }

    func = switcher.get(setting['type'], lambda: "nothing")
    func.insert(settings['db'], collection, data)

def search_page(page_url, search_url_class):
    global scope
    global page_count
    global next_url
    global settings
    global download_counter
    print(str(page_count) + ' : Loading : ' + page_url)
    logger.set_log(str(page_count) + ' : Loading : ' + page_url)
    # if page_count > 0 and ("history" in settings):
        # history.history_control(settings["history"], page_url)

    doc = get_page_content(page_url, search_url_class["enable_javascript"], search_url_class)
    if search_url_class['type'] == 'loop':
        elements = doc.xpath(search_url_class['className'])
        # print(etree.tostring(doc))
        for el in elements:
            # get_items(el.attrib['href'])
            if "attrib" in search_url_class:
                attrib = el.attrib[search_url_class["attrib"]]
            else:
                attrib = el.attrib['href']

            if 'download_attrib' in search_url_class and search_url_class['download_attrib'] is True:
                logger.set_log("Added Download List: " + attrib)
                print("Download List: " + str(download_counter) + " : from page : "
                      + str(page_count) + " : " + search_url_class['download_folder'])
                headers = {
                    'User-Agent': scope['user_agent'],
                    'Accept-Language': scope['accept_language'],
                    'Referer': attrib
                }

                thread_model = ThreadModel("thread_" + str(download_counter) + "_" + str(time.time()))
                thread_model.target = 'http_service.download_image'
                thread_model.args = {
                    "attrib": attrib,
                    "folder_name": search_url_class['download_folder'],
                    "headers": headers,
                    "thread_name": thread_model.name
                }
                thread_model.status = "wait"
                thread_model.type = "download_thread"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                thread_controller.add_thread(thread_model)

                download_counter += 1
            else:
                thread_model = ThreadModel("thread_" + str(time.time()))
                thread_model.target = 'get_items'
                thread_model.args = {
                    "url": attrib, "thread_name": thread_model.name, "type": 'page'
                }
                thread_model.status = "wait"
                thread_model.type = "get_items"
                thread_model.start_time = 0
                thread_model.stop_time = 0
                thread_controller.add_thread(thread_model)

        if scope['isPagination']:
            pagination = scope['pagination']
            for pag in doc.xpath(pagination['urlClass']):
                if 'ifExistsClass' in pagination and doc.find_class('ifExistsClass') is not None:
                    next_url = pag.attrib[pagination['attrib']]
                else:
                    next_url = pag.attrib[pagination['attrib']]
            else:
                attr_list = doc.xpath(pagination['urlClass'])
                if len(attr_list) > 0:
                    next_url = attr_list[0].attrib[pagination['attrib']]
                else:
                    next_url = None

            if next_url is not None:
                next_url = next_url.replace(" ", "%20")
                page_count += 1
                time.sleep(settings["search_time_sleep"])
                search_page(next_url, search_url_class)


def get_items(*params):
    global scope
    global download_counter
    global page_count
    global settings
    url = params[0]
    thread_name = params[1]
    type = params[2]
    print("Reading: " + url)

    search_url_class = scope['searchUrlClass']

    if "searchUrlClass" in search_url_class  and type is not 'item':
        inside_search = search_url_class["searchUrlClass"]
        doc = get_page_content(url, inside_search["enable_javascript"], inside_search)
        elements = doc.xpath(inside_search ['className'])
        for el in elements:
            if search_url_class["attrib"] is not None:
                attrib = el.attrib[inside_search["attrib"]]
            else:
                attrib = el.attrib['href']

            thread_model = ThreadModel("thread_" + str(time.time()))
            thread_model.target = 'get_items'
            thread_model.args = {
                "url": attrib, "thread_name": thread_model.name, "type": 'item'
            }
            thread_model.status = "wait"
            thread_model.type = "get_items"
            thread_model.start_time = 0
            thread_model.stop_time = 0
            thread_controller.add_thread(thread_model)

    else:

        if 'forItem' in search_url_class:
            for_items = search_url_class['forItem']
            doc = get_page_content(url, search_url_class["enable_javascript"], search_url_class)
        else:
            inside_search = search_url_class["searchUrlClass"]
            for_items = inside_search['forItem']
            doc = get_page_content(url, inside_search["enable_javascript"], inside_search)

        item_loops(doc, for_items, url)
    thread_controller.remove_thread(thread_name)


def item_loops(doc, items, url):
    global download_counter
    for item in items:
        item_list = item['itemList']
        for list_item in item_list:
            class_name = list_item['className']
            need_attr = list_item['needAttr']
            folder_name = item['downloadFolder']

            if 'childIterator' in item:
                folder_sep = item['childIterator']
            else:
                folder_sep = os.path.sep

            folder_name = folder_name.replace("${os.sep}", folder_sep)
            if 'folderChildNameClass' in item:
                if item['childIterator'] == 'os.sep':
                   folder_sep = os.sep
                else:
                   folder_sep = item['childIterator']

                folder_name = get_folder_name(doc.xpath(item['folderChildNameClass']), folder_sep, folder_name)
            i = 0
            elements =  doc.xpath(class_name)
            if len(elements) == 0:
                logger.set_error_log("The \"" + class_name + "\" class was not found at \""
                                     + url + "\".")

            for element in elements: # get element list
                attrib = ''
                if need_attr['if'] in element.attrib:
                    attrib = element.attrib[need_attr['if']]
                else:
                    attrib = element.attrib[need_attr['else']]

                try:
                    logger.set_log("Added Download List: " + url)
                    print("Download List: " + str(download_counter) + " : from page : " + str(page_count) + " : " + folder_name)
                    headers = {
                        'User-Agent': scope['user_agent'],
                        'Accept-Language': scope['accept_language'],
                        'Referer': url
                    }

                    thread_model = ThreadModel("thread_" + str(download_counter) + "_" + str(time.time()))
                    thread_model.target = 'http_service.download_image'
                    thread_model.args = {
                        "attrib": attrib,
                        "folder_name": folder_name,
                        "headers": headers,
                        "thread_name": thread_model.name
                    }
                    thread_model.status = "wait"
                    thread_model.type = "download_thread"
                    thread_model.start_time = 0
                    thread_model.stop_time = 0
                    thread_controller.add_thread(thread_model)

                    download_counter += 1
                    time.sleep(settings["download_time_sleep"])

                except Exception as e:
                    print("Error: " + str(e))
                    abs_file_path = os.path.join(script_dir, 'error_log.txt')
                    with open(abs_file_path, 'a') as the_file:
                        the_file.write( str(page_count) + ': ' + str(e) + '\n' + folder_name)
                        the_file.write('\n')
                    time.sleep(120)
                    headers = {
                        'User-Agent': scope['user_agent'],
                        'Accept-Language': scope['accept_language'],
                        'Referer': url  # This is another valid field
                    }

                    http_service.download_image(attrib, folder_name, headers, "thread_" + str(download_counter))
                i = i + 1


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



def shutdown():
    print("All process is successfull ")
    logger.set_log("scrappy is finished...")
    exit()
