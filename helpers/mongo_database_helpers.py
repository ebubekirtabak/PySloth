from pymongo import MongoClient

from PySloth import logger


class MongoDatabaseHelpers:

    def __init__(self, database):
        self.db = self.connect_database(database)

    def init_database(self, db):
        self.db = db

    def connect_database(self, database):
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
            print("MongoDB Helpers: connect database: " + str(e))
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
                    logger.Logger().set_log('--------- DATA ----------')
                    logger.Logger().set_log(data)
                    logger.Logger().set_log('--------- DATA ----------')
                else:
                    logger.Logger().set_error_log("mongo insert data error", True)
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: insert Error: " + str(e), True)
                return 400

    def upsert(self, collection, key, data):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                result = selected_collection.update(key, {"$set": data}, upsert=True)
                if hasattr(result, "matched_count") or hasattr(result, "inserted_id"):
                    logger.Logger().set_log('--------- DATA ----------')
                    logger.Logger().set_log(data)
                else:
                    logger.Logger().set_log(str(result), True)
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: upsert Error: " + str(e), True)
                return 400

    def upsert_many(self, collection, data):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                for item in data:
                    result = selected_collection.update_one(item, {"$set": item}, upsert=True)
                    if result.matched_count > 0:
                        logger.Logger().set_log('--------- DATA ----------')
                        logger.Logger().set_log(data)
                    else:
                        logger.Logger().set_error_log("mongo upsert data error")

            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: upsert Error: " + str(e))
                return 400

    def insert_many(self, collection, data):
        if self.db != 400:
            try:
                selected_collection = self.db[collection]
                result = selected_collection.insert_many(data)
                if len(result.inserted_ids) > 0:
                    logger.Logger().set_log("insert data")
                    logger.Logger().set_log('--------- DATA ----------')
                    logger.Logger().set_log(data)
                    logger.Logger().set_log('--------- DATA ----------')
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
                    query, {"$set": data}
                )
                logger.Logger().set_log("update collection data")
            except Exception as e:
                logger.Logger().set_error_log("MongoDB Helpers: update Error: " + str(e), True)
                return 400

    def delete(self, collection, query):
        self.db[collection].delete_one(query)

    def delete_one(self, collection, query):
        self.db[collection].delete_one(query)

    def get_find(self, collection, query):
        return self.db[collection].find(query)

    def get_find_one(self, collection, query):
        return self.db[collection].find_one(query)

    def get_find_all(self, collection):
        return self.db[collection].find()

    def find_and_delete(self, collection, query):
        return self.db[collection].find_one_and_delete(query)

    def find_and_modify(self, collection, query, sort, update):
        return self.db[collection].find_and_modify(query, sort=sort, update=update)

    def get_length(self, collection):
        return self.db[collection].count()

    def is_exists(self, collection, data):
        selected_collection = self.db[collection]
        return selected_collection.find(data).count() > 0

    def is_exists_field(self, collection, query):
        results = self.db[collection].find(query)
        return results.count() > 0
