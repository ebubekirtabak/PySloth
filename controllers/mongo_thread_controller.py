import logger
import mongo

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

    def add_thread(self, thread_model):
        logger.set_log("added Theread : " + thread_model.name)
        if len(self.active_thread_array) < self.settings['thread_limit']:
            self.thread_array.append(thread_model)
        else:
            mongo.insert(self.database, self.database_setting['thread_collection'], thread_model)

        self.thread_controller()

    def remove_thread(self):
        print("mongo thread_controller")

    def clear_thread_list(self):
        self.empty_thread_step = 0
        self.thread_array = []
        self.active_thread_array = []
