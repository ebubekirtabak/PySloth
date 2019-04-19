class DatabaseModel:
    def __init__(self, type, name, uri, user_name, password, collections):
        self.type = type
        self.name = name
        self.uri = uri
        self.user_name = user_name
        self.password = password
        self.collections = collections

