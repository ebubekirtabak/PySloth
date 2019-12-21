from pymongo import MongoClient
import logger


class MongoDatabaseHelpers:

    def __init__(self, database):
        self.db = self.connect_database(database)

    def init_database(self, db):
        self.db = db

    def connect_database(self, database):
        print(database)
        client = MongoClient(database['uri'])
        try:
            if database['name'] in client.list_database_names():
                self.db = client[database['name']]
                return self.db
            else:
                logger.Logger().set_log('Database not exixts, create database: ' + database['name'], True)
                self.db = client[database['name']]
                return self.db
        except Exception as e:
            logger.Logger().set_error_log("MongoDB Helpers: connect database: " + str(e))
            return 400

    def get_server_status(self):
        try:
            return self.db.command("serverStatus")
        except Exception as e:
            logger.Logger().set_error_log("MongoDB Helpers: Server status: " + str(e))
            return 0

    def insert(self, collection, data):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                result = selected_collection.insert_one(data)
                if result.inserted_id is not None:
                    logger.Logger().set_log("insert data")
                else:
                    logger.Logger().set_error_log("mongo insert data error")
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: insert Error: " + str(e))
                return 400

    def insert_many(self, collection, data):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                result = selected_collection.insert_many(data)
                if len(result.inserted_ids) > 0:
                    logger.Logger().set_log("insert data")
                else:
                    logger.Logger().set_error_log("mongo insert data error", True)
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: insert Error: " + str(e), True)
                return 400

    def update(self, collection, data, query):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                selected_collection.update(
                    query, {"$set": data})
                logger.Logger().set_log("update collection data")
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: update Error: " + str(e), True)
                return 400

    def get_find(self, collection, query):
        return self.db[collection].find(query)

    def get_find_all(self, collection):
        return self.db[collection].find()

    def find_and_delete(self, collection, query):
        return self.db[collection].find_one_and_delete(query)

    def get_length(self, collection):
        return self.db[collection].count()

    def is_exists(self, collection, data):
        selected_collection = self.db[collection]
        return selected_collection.find(data).count() > 0
