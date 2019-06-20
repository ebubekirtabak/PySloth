import scope
import sys

from services.scope_reader_service import ScopeReaderService
from scope import Scope


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'scope':
        scope_model = ScopeReaderService().get_scope(scope_name=sys.argv[2])
        Scope(scope_model).start()



if __name__ == '__main__':
    main()



