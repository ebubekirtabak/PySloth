import mongo

''' "history": {
    "to": "database",
    "collection_name": "history_collection",
    "control": {
        "from": "database",
        "progress": "skip"
    }
    } '''




def history_control(history, data):
    control = history["control"]
    switcher = {
        "database": database_control(history, data),
        "file": file_control(history),
    }

    func = switcher.get(contro["from"], lambda: "nothing")
    return func

def database_control(control, data):
    exit()

