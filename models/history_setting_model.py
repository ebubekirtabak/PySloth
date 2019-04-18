'''
"history": {
    "collection_name": "history_collection",
    "source": "mysql, mongo"
    "clear_on_exit": true
}
'''


class HistorySettingModel:

    def __init__(self, source, collection_name, clear_on_exit):
        self.source = source
        self.collection_name = collection_name
        self.clear_on_exit = clear_on_exit
