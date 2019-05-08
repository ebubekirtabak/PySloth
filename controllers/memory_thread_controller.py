import time
import os

from collections import namedtuple
from logger import Logger

script_dir = os.path.dirname(__file__)


class MemoryThreadController:
    active_thread_array = []
    thread_array = []
    settings = {}
    empty_thread_step = 0

    def __init__(self, settings, main_scope):
        self.settings = namedtuple("SettingsModel", settings.keys())(*settings.values())
        self.multi_process = self.settings.multi_process
        self.logger = Logger()
        self.main_scope = main_scope

    def thread_controller(self):

        try:
            time.sleep(1)
            self.logger.set_log("Thread Controller : Active : " + str(len(self.active_thread_array)) + " : Array : " +
                                str(len(self.thread_array)))
            if len(self.active_thread_array) < self.settings["thread_limit"] and len(self.thread_array) > 0:
                self.main_scope.start_thread(self.thread_array[0])
                self.active_thread_array.append(self.thread_array[0])
                self.thread_array.remove(self.thread_array[0])
                self.empty_thread_step = 0
                self.save_session()
                time.sleep(2)

            elif len(self.active_thread_array) >= self.settings["thread_limit"]:
                time.sleep(1)
            elif len(self.active_thread_array) == 0 and len(self.thread_array) == 0:
                self.empty_thread_step += 1
                time.sleep(1)
                if self.empty_thread_step > 120:
                    self.logger.set_log("program exit()")
                    exit()

        except Exception as e:
            self.logger.set_error_log("Thread_Controller: " + str(e))
            time.sleep(10)
            self.thread_controller()

    def save_session(self):
        if 'session_id' in self.settings:
            self.write_file("session_" + self.settings['session_id'] + '.txt', str(self.thread_array + self.active_thread_array))

    def write_file(self, file_name, data):
        abs_file_path = os.path.join(script_dir + '/session', file_name)
        f = open(abs_file_path, "w")
        f.write(data.replace("\'", "\""))

    def auto_thread_stopper(self):
        # then timeout stop thread

        try:
            index = 0
            for thread in self.active_thread_array:
                now_time = int(round(time.time() * 1000))
                different = (now_time - thread.start_time)
                different = int(different / 1000)
                if different > self.settings['thread_time_out']:
                    print(thread.name + ' Timeout...')
                    thread.stop_time = now_time
                    self.thread_array.append(self.active_thread_array[index])
                    self.active_thread_array.remove(self.active_thread_array[index])

                index += 1

        except Exception as e:
            logger.set_error_log("auto_thread_stopper(): " + str(e))
            time.sleep(10)
            self.thread_controller()

    def add_thread(self, thread_model):
        logger.set_log("added Theread : " + thread_model.name)
        self.thread_array.append(thread_model)
        self.thread_controller()

    def remove_thread(self, name):
        index = 0
        for thread_item in self.active_thread_array:

            if thread_item.name == name:
                logger.set_log("Finish thread : " + name)
                self.active_thread_array.remove(self.active_thread_array[index])
                break
            index += 1
        self.thread_controller()

    def restart_thread(self, name):
        index = 0
        for thread_item in self.active_thread_array:

            if thread_item.name == name:
                logger.set_log("Finish thread from restart_thread(): " + name)
                self.thread_array.append(self.active_thread_array[index])
                self.active_thread_array.remove(self.active_thread_array[index])
                break

            index += 1
        self.thread_controller()

    def clear_thread_list(self):
        self.empty_thread_step = 0
        self.thread_array = []
        self.active_thread_array = []

