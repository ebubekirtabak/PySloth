from helpers.mongo_database_helpers import MongoDatabaseHelpers


class CookieHelpers:

    def __init__(self, driver, scope):
        self.driver = driver
        self.scope = scope

    def save_cookie(self, cookie_event):
        self.cookies = self.driver.get_cookies()
        database = self.scope.settings.database
        database_helper = MongoDatabaseHelpers(database)
        database_helper.insert_many(database['cookie_collection'], self.cookies)

    def load_cookie_from_database(self):
        database = self.scope.settings.database
        database_helper = MongoDatabaseHelpers(database)
        cookie_list = database_helper.get_find_all(database['cookie_collection'])
        for cookie in cookie_list:
            del cookie['_id']
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry'])
            self.driver.add_cookie(cookie)

    def get_cookie(self):
        return self.cookies
