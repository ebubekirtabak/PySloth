import json
from collections import namedtuple

from modules.file_module import FileModule
from models.setting_model import SettingModel


class ScopeReaderService:

    def __init__(self):
        pass

    def get_scope(self, scope_name):
        scope = self.init_scope_model(scope_name)
        scope_model = namedtuple("ScopeModel", scope.keys())(*scope.values())
        return scope_model

    def init_scope_model(self, scope_name):
        try:
            read_file = FileModule.read_json_file(file_name='myconf.json')
            if read_file['success'] is True:
                data = read_file['data']
                print(data)
                scope = data['scope']
                for item in scope:
                    if item['scope_name'] == scope_name:
                        break
                    return item

        except Exception as e:
            print(str(e))
