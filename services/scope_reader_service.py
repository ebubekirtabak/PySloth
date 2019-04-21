import json

from modules.file_module import FileModule


class ScopeReaderService:

    def __init__(self):
        pass

    @staticmethod
    def init_scope_model(scope_name):
        try:
            read_file = FileModule.read_json_file(file_name='myconf.json')
            if read_file['success'] is True:
                data = read_file['data']
                print(data)
                scope = data['scope']
                for item in scope:
                    if item['scope_name'] == scope_name:
                        return item
        except Exception as e:
            print(str(e))
