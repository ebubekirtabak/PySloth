# -*- coding: utf-8 -*-
import scope
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'scope':
        scope.init_scope()


if __name__ == '__main__':
    main()



