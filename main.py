# -*- coding: utf-8 -*-
import scope
import sys

from services.scope_reader_service import ScopeReaderService

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'scope':
        scope.init_scope()
    scopeModel = ScopeReaderService().init_scope_model('Dollar')
    print('scope_model')



if __name__ == '__main__':
    main()



