import sys
import time
import os
import uuid
from PySloth import globals

script_dir = os.path.dirname(__file__)
logs_dir = script_dir + '/logs/'


class Logger:

    def __init__(self):
        self.check_log_dir()
        if ('session_id' in globals.configs) is False:
            print("session_id is null")
            globals.configs['session_id'] = str(uuid.uuid1())

    @staticmethod
    def set_log(data, is_print_to_console=False):
        if is_print_to_console:
            print(data)

        session_id = globals.configs['session_id']
        abs_file_path = os.path.join(logs_dir, 'log_' + session_id + '.txt')
        with open(abs_file_path, 'a') as the_file:
            the_file.write(str(time.strftime('%c')) + " : " + str(data))
            the_file.write('\n')

    @staticmethod
    def set_error_log(data, is_print_to_console=False):
        if is_print_to_console:
            print("set_error_log() Error:" + data)

        session_id = globals.configs['session_id']
        abs_file_path = os.path.join(logs_dir, 'log_' + session_id + '.txt')
        with open(abs_file_path, 'a') as the_file:
            the_file.write(str(time.strftime('%c')) + " : " + str(data))
            the_file.write('\n')

    @staticmethod
    def set_memory_log(data):
        session_id = globals.configs['session_id']
        abs_file_path = os.path.join(logs_dir, 'log_' + session_id + '.txt')
        with open(abs_file_path, 'a') as the_file:
            the_file.write(str(time.strftime('%c')) + " : " + str(data))
            the_file.write('\n')

    @staticmethod
    def check_log_dir():
        if os.path.isdir(logs_dir) is not True:
            os.mkdir(logs_dir)
