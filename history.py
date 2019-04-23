import mongo

''' 
    "history": {
        "to": "database",
        "collection_name": "history_collection",
        "control": {
            "from": "database",
            "progress": "skip"
        }
    } 
    '''

class history_control:

    def __init__(self, history):
        self.history = history


    def history_control(self, history, data):
        control = self.history["control"]
        switcher = {
            "database": self.database_control(history, data),
            "file": self.file_control(history),
        }

        func = switcher.get(control["from"], lambda: "nothing")
        return func

    def database_control(self, control, data):
        exit()


    def file_control(self, control, data):
        exit()


