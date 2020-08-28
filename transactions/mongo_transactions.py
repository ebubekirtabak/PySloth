import sys

from helpers.mongo_database_helpers import MongoDatabaseHelpers
from logger import Logger


class MongoTransactions:

    def __init__(self, database, value):
        self.database = database
        self.collection_name = ""
        self.value = value

    def database_action_router(self, doc, database_action):
        action = database_action['action']
        database = self.database
        try:
            self.collection_name = database_action['collection_name']
            if ':' in self.collection_name:
                self.value, self.collection_name = self.get_collection_and_value()
        except Exception as e:
            Logger().set_error_log("database_action_router() -> " + str(e))
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror), True)

        if action == "push_to_database":
            MongoDatabaseHelpers(database).insert(
                self.collection_name,
                self.value
            )
        elif action == "upsert_to_database":
            self.upsert_to_database(database_action)
        elif action == 'push_array_to_database':
            MongoDatabaseHelpers(database).insert_many(
                self.collection_name,
                self.value
            )
        elif action == 'upsert_array_to_database':
            MongoDatabaseHelpers(database).upsert_many(
                self.collection_name,
                self.value
            )

    def get_collection_and_value(self):
        selector_items = self.collection_name.split(':')
        collection_name = selector_items[0]
        value = self.value[selector_items[1]]
        return value, collection_name

    def upsert_to_database(self, database_action):
        query = self.prepare_upsert_query(database_action["query_keys"])
        MongoDatabaseHelpers(self.database).upsert(
            self.collection_name,
            query,
            self.value
        )

    def prepare_upsert_query(self, query_keys):
        query = {}
        for key in query_keys:
            if key in self.value:
                query[key] = self.value[key]
            else:
                print("The value " + key + " was not found in the value.")

        return query
