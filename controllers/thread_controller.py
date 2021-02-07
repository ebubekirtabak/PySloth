from collections import namedtuple

import scope
import time
from logger import Logger
import json
import os
import datetime, threading
from controllers.memory_thread_controller import MemoryThreadController
from controllers.mongo_thread_controller import MongoThreadController
import sys
script_dir = os.path.dirname(__file__)


class ThreadController:

    def __init__(self, settings, main_scope):
        self.main_scope = main_scope
        self.settings = settings
        self.is_cancelled = False
        self.session_time = str(time.time())
        self.logger = Logger()
        self.multi_process = self.settings["multi_process"]
        self.controller = None
        self.timer = None
        self.init_controller()

    def init_controller(self):
        self.multi_process = namedtuple("MultiProcessModel", self.multi_process.keys())(*self.multi_process.values())
        self.controller = self.controller_switcher(self.multi_process.base)
        self.init_timer()
        self.controller_interval()

    def init_timer(self):
        self.timer = threading.Timer(30, self.auto_thread_controller)

    def controller_interval(self):
        if hasattr(self, 'timer') and self.timer.is_alive() is not True:
            self.timer.start()

    def auto_thread_controller(self):
        if hasattr(self, 'controller'):
            self.controller_interval()
            self.controller.auto_thread_stopper()
            self.controller.thread_controller()
            self.check_controller_list()
        else:
            self.stop_thread_controller()

    def controller_switcher(self, type):
        switcher = {
            "mongo": MongoThreadController(self.settings, self.main_scope),
            "memory": MemoryThreadController(self.settings, self.main_scope),
            "mysql": lambda: MemoryThreadController(self.settings, self.main_scope),
        }

        return switcher.get(type, lambda: "nothing")

    def check_controller_list(self):
        try:
            threads = self.controller.get_thread_list()
            print("Ative threads: " + str(len(threads['active_threads'])))
            if len(threads['active_threads']) == 0 and len(threads['buffer_threads']) == 0:
                self.stop_thread_controller()
                self.logger.set_log(str(datetime.datetime.now()) + " : " + "Thread Controller has been stoped.", True)
        except Exception as e:
            self.logger.set_error_log(str(datetime.datetime.now()) + " : " + str(e))

    def add_thread(self, thread_model):
        self.controller.add_thread(thread_model)

    def restart_thread(self, name):
        self.controller.restart_thread(name)

    def remove_thread(self, name):
        self.controller.remove_thread(name)

    def clear_thread_list(self):
        self.controller.clear_thread_list()

    def get_thread_size(self):
        return len(self.thread_array.length)

    def history_check(self, url):
        return self.controller.history_check(url)

    def stop_thread_controller(self):
        if self.timer.is_alive():
            self.timer.cancel()

        if hasattr(self, 'timer'):
            del self.timer

        if hasattr(self, 'controller'):
            del self.controller






