import logger
import mongo
import time
import scope
import sys
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
            lent = mongo.get_length(self.database, self.database_setting['thread_collection_name'])
            logger.set_log("Mongo Thread Controller : Active : " +
                       str(len(self.active_thread_array)) + " : Array : " +
                       str(lent))
            if len(self.active_thread_array) < self.settings["thread_limit"] and lent > 0:
                 thread_object = mongo.find_and_delete(
                        self.database,self.database_setting['thread_collection_name'], { "status": "wait" })
                 thread_model = namedtuple("ThreadModel", thread_object.keys(), rename=True)(*thread_object.values())
                 scope.start_thread(thread_model)
                 self.active_thread_array.append(thread_model)
                 print("start: ")

        except Exception as e:
            logger.set_error_log("mongo_thread_controller(): " + str(e))
            time.sleep(10)
            self.thread_controller()

    def add_thread(self, thread_model):
        logger.set_log("added Thread : " + thread_model.name)
        if len(self.active_thread_array) < self.settings['thread_limit']:
            self.active_thread_array.append(thread_model)
            scope.start_thread(thread_model)
        else:
            mongo.insert(self.database, self.database_setting['thread_collection_name'], thread_model.__dict__)

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

    def clear_thread_list(self):
        self.empty_thread_step = 0
        self.active_thread_array = []

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
                    self.add_thread(self.active_thread_array[index])
                    self.active_thread_array.remove(self.active_thread_array[index])

                index += 1

        except Exception as e:
            logger.set_error_log("auto_thread_stopper(): " + str(e))
            type, value, traceback = sys.exc_info()
            print('Error opening %s: %s' % (value.filename, value.strerror))
            time.sleep(10)
            self.thread_controller()