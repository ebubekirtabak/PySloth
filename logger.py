import time
import os

from modules.file_module import FileModule
script_dir = os.path.dirname(__file__)


class Logger:

    def __init__(self):
        pass

    def set_log(self, data):
        abs_file_path = os.path.join(script_dir, 'log.txt')
        with open(abs_file_path, 'a') as the_file:
            the_file.write( str(time.strftime('%c')) + " : " + data)
            the_file.write('\n')

    def set_error_log(self, data):
        print("Error:" + data)
        FileModule().write_file_line(script_dir, file_name='error_log.txt', line='Error: ' + str(time.strftime('%c')) + " : " + data)

    def set_memory_log(self, data):
        FileModule().write_file_line(script_dir, file_name='memory_logs/error_log' + str(time.time()) + '.txt',  line=str(time.strftime('%c')) + " : " + data)
