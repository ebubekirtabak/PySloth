import os
import time
import random
from collections import namedtuple

from controllers import thread_controller
import logger
import sys
from urllib.request import urlopen
import urllib.request

from models.setting_model import SettingModel
from modules import file_module
script_dir = os.path.dirname(__file__)


class HttpServices:

    def __init__(self, settings):
        self.settings = settings
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
                filename = file_module.get_short_file_name(filename, 90)
            filename = filename + "?ty=" + str(random.randint(1,9999999))

            startTime = time.time()
            request = urllib.request.Request(url, headers=headers)
            contents = urllib.request.urlopen(request)
            endTime = time.time()
            logger.set_log("Download directory: " + script_dir + path)
            if not os.path.isdir(script_dir + path):
                os.mkdir(script_dir + path)
            abs_file_path = os.path.join(script_dir + path, filename)

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
            thread_controller.remove_thread(thread_name)

        except ConnectionResetError as e:
            logger.set_error_log('Error: ' + str(e))
            logger.set_error_log('Sleep system 300 S')
            time.sleep(300)
            logger.set_error_log('Restart thread : ' + thread_name)
            thread_controller.restart_thread(thread_name)
        except Exception as e:
            type, value, traceback = sys.exc_info()
            print('Error opening %s: %s' % (value.filename, value.strerror))
            logger.set_error_log('Error: ' + str(e))
            logger.set_error_log('Error opening %s: %s' % (value.filename, value.strerror))
            logger.set_error_log('Sleep system 300 S')
            time.sleep(300)
            logger.set_error_log('Restart thread : ' + thread_name)
            thread_controller.restart_thread(thread_name)
