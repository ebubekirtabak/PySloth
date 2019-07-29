from collections import namedtuple

import sys

from modules.file_module import FileModule
from services.scope_reader_service import ScopeReaderService
from scope import Scope


def main():
    global scope_variables
    scope_variables = {}
    if len(sys.argv) > 1 and sys.argv[1] == 'scope':
        scope_model = ScopeReaderService().get_scope(scope_name=sys.argv[2])
        Scope(scope_model).start()
    elif len(sys.argv) > 1 and sys.argv[1] == 'scope_file':
        file = FileModule().read_file(dir=sys.argv[2], file_name=sys.argv[3])
        scope_model = namedtuple("ScopeModel", file['data'].keys())(*file['data'].values())
        Scope(scope_model).start()


if __name__ == '__main__':
    main()



