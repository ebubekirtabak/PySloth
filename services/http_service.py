import os
import time
import random
import sys

import globals
from collections import namedtuple
from logger import Logger


from urllib.request import urlopen
import urllib.request

from models.setting_model import SettingModel
from modules import file_module
from modules.file_module import FileModule


class HttpServices:

    def __init__(self, settings, thread_controller):
        self.settings = settings
        self.file_module = FileModule
        self.logger = Logger()
        self.thread_controller = thread_controller
        if isinstance(self.settings, SettingModel):
            self.settings = namedtuple("SettingModel", self.settings.keys())(*self.settings.values())

        self.file_settings = self.settings["file_settings"]

    def download_file(self, *kwargs):
        try:
            url = kwargs[0]
            headers = kwargs[2]
            path = kwargs[1]
            thread_name = kwargs[3]

            print("Downloaded: " + url)
            filename = url.split('/')[-1]
            if "max_file_length" in self.file_settings:
                filename = FileModule().get_short_file_name(filename, self.file_settings["max_file_length"])
            # filename = filename + "?ty=" + str(random.randint(1,9999999))

            startTime = time.time()
            request = urllib.request.Request(url, headers=headers)
            contents = urllib.request.urlopen(request)
            endTime = time.time()
            self.logger.set_log("Download directory: " + globals.script_dir + path)
            if not os.path.exists(globals.script_dir + path):
                os.makedirs(globals.script_dir + path)

            abs_file_path = os.path.join(globals.script_dir + path, filename)

            with open(abs_file_path , 'wb') as f:
                while True:
                    tmp = contents.read(1024)
                    if not tmp:
                        break
                    f.write(tmp)

            totalTimeTaken = str(float(round((endTime - startTime), 3)))
            # print("Size: " + len(r.content) )
            # print("Elapsed: " + str(r.elapsed))
            print("Time Taken: " + totalTimeTaken)
            print("thread_name: " + thread_name)
            self.thread_controller.remove_thread(thread_name)

        except ConnectionResetError as e:
            self.logger.set_error_log('Error: ' + str(e))
            self.logger.set_error_log('Sleep system 300 S')
            time.sleep(300)
            self.logger.set_error_log('Restart thread : ' + thread_name)
            self.thread_controller.restart_thread(thread_name)
        except Exception as e:
            type, value, traceback = sys.exc_info()
            self.logger.set_error_log('Error: ' + str(e))
            if hasattr(value, 'filename'):
                print('Error opening %s: %s' % (value.filename, value.strerror))
                self.logger.set_error_log('Error opening %s: %s' % (value.filename, value.strerror))

            self.logger.set_error_log('Sleep system 300 S')
            time.sleep(300)
            self.logger.set_error_log('Restart thread : ' + thread_name)
            self.thread_controller.restart_thread(thread_name)
