import time
import os
script_dir = os.path.dirname(__file__)


def set_log(data):
    abs_file_path = os.path.join(script_dir, 'log.txt')
    with open(abs_file_path, 'a') as the_file:
        the_file.write( str(time.strftime('%c')) + " : " + data)
        the_file.write('\n')


def set_error_log(data):
    abs_file_path = os.path.join(script_dir, 'error_log.txt')
    with open(abs_file_path, 'a') as the_file:
        the_file.write( str(time.strftime('%c')) + " : " + data)
        the_file.write('\n')

