import logger
import mongo
import time
import scope
import sys
import os
from models.thread_model import ThreadModel
from collections import namedtuple


class MongoThreadController:
    active_thread_array = []
    thread_array = []
    settings = {}
    empty_thread_step = 0
    databse_setting = None
    database = None

    def __init__(self, settings):
        self.settings = settings
        self.database_setting = settings['database']
        self.database = mongo.connect_database(self.database_setting)

    def thread_controller(self):
        try:
            active_thread_length = len(self.active_thread_array)
            lent = mongo.get_length(self.database, self.database_setting['thread_collection_name'])
            logger.set_log("Mongo Thread Controller : Active : " +
                       str(active_thread_length) + " : Array : " +
                       str(lent))
            if active_thread_length == 0 and lent == 0:
                scope.shutdown()
            elif active_thread_length < self.settings["thread_limit"] and lent > 0:
                 thread_object = mongo.find_and_delete(
                        self.database, self.database_setting['thread_collection_name'], { "status": "wait", "type": "download_thread" })
                 if thread_object is None:
                     thread_object = mongo.find_and_delete(self.database, self.database_setting['thread_collection_name'],
                                                            {"status": "wait" })
                 if isinstance(thread_object, ThreadModel):
                     thread_object.start_time = int(round(time.time() * 1000))
                 else:
                     thread_object["start_time"] = int(round(time.time() * 1000))

                 thread_model = namedtuple("ThreadModel", thread_object.keys(), rename=True)(*thread_object.values())
                 self.active_thread_array.append(thread_model)
                 scope.start_thread(thread_model)
                 print("start thread: ")

        except Exception as e:
            logger.set_error_log("mongo_thread_controller(): " + str(e))
            type, value, traceback = sys.exc_info()

            print(sys.exc_info()[0])
            logger.set_error_log(sys.exc_info()[0])
            time.sleep(10)
            self.thread_controller()

    def dict_from_class(self, cls):
        return dict((key, value) for (key, value) in cls)

    def add_thread(self, thread_model):
        logger.set_log("added Thread : " + thread_model.name)
        if len(self.active_thread_array) < self.settings['thread_limit']:
            if isinstance(thread_model, ThreadModel):
                thread_model.start_time = int(round(time.time() * 1000))
            else:
                logger.set_error_log("add_thread: non object error")
                thread_model = namedtuple("ThreadModel", thread_model.keys(), rename=True)(*thread_model.values())
                thread_model["start_time"] = int(round(time.time() * 1000))
            self.active_thread_array.append(thread_model)
            scope.start_thread(thread_model)
        else:
            try:
                mongo.insert(self.database, self.database_setting['thread_collection_name'], thread_model.__dict__)
            except Exception as e:
                object_thread = ThreadModel(thread_model.name, thread_model.target, thread_model.args,
                                            thread_model.status, thread_model.type, thread_model.start_time, thread_model.stop_time)
                logger.set_error_log("no __dict__: " + str( object_thread.__dict__))
                mongo.insert(self.database,
                             self.database_setting['thread_collection_name'], object_thread.__dict__)

        self.thread_controller()

    def remove_thread(self, name):
        index = 0
        for thread_item in self.active_thread_array:

            if thread_item.name == name:
                logger.set_log("Finish thread : " + name)
                del self.active_thread_array[index]
                break

            index += 1
        self.thread_controller()

    def clear_thread_list(self):
        self.empty_thread_step = 0
        self.active_thread_array = []

    def auto_thread_stopper(self):
        # then timeout stop thread

        try:
            clear = lambda: os.system('clear')
            clear()
            index = 0
            for thread in self.active_thread_array:
                now_time = int(round(time.time() * 1000))
                different = (now_time - thread.start_time)
                different = int(different / 1000)
                if different > self.settings['thread_time_out']:
                    print(thread.name + ' Timeout...')
                    '''if 'stop_time' in thread:
                        thread.stop_time = now_time'''
                    self.add_thread(self.active_thread_array[index])
                    del self.active_thread_array[index]

                index += 1

        except Exception as e:
            logger.set_error_log("auto_thread_stopper(): " + str(e))
            type, value, traceback = sys.exc_info()
            print('Error opening %s: %s' % (value.filename, value.strerror))
            logger.set_error_log('Error opening %s: %s' % (value.filename, value.strerror))

            time.sleep(10)
            self.thread_controller()

    def restart_thread(self, name):
        index = 0
        for thread_item in self.active_thread_array:
            if thread_item.name == name:
                logger.set_log("Restart thread : " + name)
                self.add_thread(self.active_thread_array[index])
                del self.active_thread_array[index]
                break

            index += 1
        self.thread_controller()
