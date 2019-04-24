import scope
import time
import logger
import json
import os
import datetime, threading
from controllers.memory_thread_controller import MemoryThreadController
from controllers.mongo_thread_controller import MongoThreadController
import sys
script_dir = os.path.dirname(__file__)


class ThreadController:

    def __init__(self, settings):
        self.settings = settings
        self.session_time = str(time.time())
        self.controller = self.controller_switcher(self.settings.multi_process.base)
        self.controller_interval()

    def controller_interval(self):
        threading.Timer(30, self.auto_thread_controller).start()

    def auto_thread_controller(self):
        print("run auto_thread_controller: " + str(datetime.datetime.now()))
        self.controller_interval()
        self.controller.auto_thread_stopper()
        self.controller.thread_controller()

    def controller_switcher(self, type):
        switcher = {
            "mongo": MongoThreadController(self.settings),
            "memory": MemoryThreadController(self.settings),
            "mysql": lambda: MemoryThreadController(self.settings),
        }

        return switcher.get(type, lambda: "nothing")

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






