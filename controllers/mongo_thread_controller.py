import logger
import mongo
import time
import json
from bson import json_util

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
        print("mongo thread_controller")
        try:
            logger.set_log("Mongo Thread Controller : Active : " +
                       str(len(self.active_thread_array)) + " : Array : " +
                       str(len(self.thread_array)))
            lent = mongo.get_length(self.database, self.database_setting['thread_collection_name'])
            if len(self.active_thread_array) < self.settings["thread_limit"] and lent > 0:
                print("bhjbjh")

        except Exception as e:
            logger.set_error_log("auto_thread_stopper(): " + str(e))
            time.sleep(10)
            self.thread_controller()

    def add_thread(self, thread_model):
        logger.set_log("added Thread : " + thread_model.name)
        if len(self.active_thread_array) < self.settings['thread_limit']:
            self.active_thread_array.append(thread_model)
        else:
            dt = {}
            dt.update(vars(thread_model))
            json_model = json.dumps(dt)
            mongo.insert(self.database, self.database_setting['thread_collection_name'], json_model)

        self.thread_controller()

    def remove_thread(self):
        print("mongo thread_controller")

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
            time.sleep(10)
            self.thread_controller()