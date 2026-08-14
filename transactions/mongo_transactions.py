import sys

from helpers.mongo_database_helpers import MongoDatabaseHelpers
from logger import Logger


class MongoTransactions:

    EMPTY_VALUES = ("", "-", "--", "n/a", "none", "null")

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
        values, set_on_insert = self.split_preserved_values(
            database_action.get("preserve_fields", [])
        )
        MongoDatabaseHelpers(self.database).upsert(
            self.collection_name,
            query,
            values,
            set_on_insert
        )

    def split_preserved_values(self, preserve_fields):
        """Splits the scraped document into the values that may overwrite what
        is already stored and the "preserve_fields" whose scraped value is
        unusable (empty or masked). Marketplaces hide the buyer details once an
        order is delivered ("Ali Veli" -> "********"), upserting that over an
        existing document would destroy the data scraped while the order was
        still open, so those values are only written on insert."""
        if not preserve_fields or not isinstance(self.value, dict):
            return self.value, {}

        values = {}
        set_on_insert = {}
        for key, value in self.value.items():
            if key in preserve_fields and not self.is_usable_value(value):
                set_on_insert[key] = value
                Logger().set_log(
                    "Preserved field: " + key + " the scraped value is empty or masked."
                )
            else:
                values[key] = value

        return values, set_on_insert

    @staticmethod
    def is_masked_value(value):
        return isinstance(value, str) and '*' in value

    @staticmethod
    def is_usable_value(value):
        if value is None:
            return False

        if isinstance(value, str):
            if MongoTransactions.is_masked_value(value):
                return False
            return value.strip().lower() not in MongoTransactions.EMPTY_VALUES

        if isinstance(value, dict):
            return any(MongoTransactions.is_usable_value(item) for item in value.values())

        if isinstance(value, (list, tuple)):
            if any(MongoTransactions.is_masked_value(item) for item in value):
                return False
            return any(MongoTransactions.is_usable_value(item) for item in value)

        return True

    def prepare_upsert_query(self, query_keys):
        query = {}
        for key in query_keys:
            if key in self.value:
                query[key] = self.value[key]
            else:
                print("The value " + key + " was not found in the value.")

        return query
