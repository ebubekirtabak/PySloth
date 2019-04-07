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


global thread_array
global active_thread_array
global settings
global empty_thread_step
global session_time
global controller

def on_load(_settings):
    global settings
    global session_time
    global controller
    settings = _settings
    session_time = str(time.time())
    controller = controller_switcher(settings['thread_controller'])
    controller_interval()
    # controller_thread = Thread(target = thread_controller, args=())
    # controller_thread.start()

def controller_interval():
    threading.Timer(30, auto_thread_controller).start()

def auto_thread_controller():
    print("run auto_thread_controller" + str(datetime.datetime.now()))
    controller_interval()
    controller.auto_thread_stopper()
    controller.thread_controller()

def controller_switcher(type):
    global settings
    switcher = {
        "mongo": MongoThreadController(settings),
        "memory": MemoryThreadController(settings),
        "mysql": lambda: MemoryThreadController(settings),
    }

    return switcher.get(type, lambda: "nothing")

def restore_session():
    global thread_array
    global settings
    if 'session_id' in settings:
        try:
            abs_file_path = os.path.join(script_dir, "session/session_" + settings['session_id'] + '.txt')
            with open(abs_file_path) as json_file:
                thread_array = json.load(json_file)
                return True
        except Exception as e:
            print( "Error: " + str(e) )
            abs_file_path = os.path.join(script_dir, 'error_log.txt')
            with open(abs_file_path, 'a') as the_file:
                the_file.write('restore_session' + ': ' + str(e))
                the_file.write('\n')
                return False

def add_thread(thread_model):
    global controller
    controller.add_thread(thread_model)

def restart_thread(name):
    global controller
    controller.restart_thread(name)

def remove_thread(name):
    global controller
    controller.remove_thread(name)

def clear_thread_list():
    global controller
    controller.clear_thread_list()

def get_thread_size():
    global thread_array
    return len(thread_array.length)



