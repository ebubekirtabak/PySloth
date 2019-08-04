import sys
import json

from collections import namedtuple

from helpers.variable_helpers import VariableHelpers
from modules.file_module import FileModule
from services.scope_reader_service import ScopeReaderService
from scope import Scope


def main():
    VariableHelpers().load_scope_variables()
    if len(sys.argv) > 1 and sys.argv[1] == 'scope':
        scope_model = ScopeReaderService().get_scope(scope_name=sys.argv[2])
        Scope(scope_model).start()
    elif len(sys.argv) > 1 and sys.argv[1] == 'scope_file':
        file = FileModule().read_file(file_name=sys.argv[2] + sys.argv[3])
        if file['success'] is True:
            scope_data = json.loads(file['data'])
            scope_model = namedtuple("ScopeModel", scope_data.keys())(*scope_data.values())
            Scope(scope_model).start()
        else:
            print('FileNotFoundError: ' + sys.argv[2] + sys.argv[3] + '')



if __name__ == '__main__':
    main()



