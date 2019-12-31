import sys
import time
import os
import globals


from modules.file_module import FileModule
script_dir = os.path.dirname(__file__)
logs_dir = script_dir + '/logs/'

class Logger:

    def __init__(self):
        pass

    def set_log(self, data, is_print_to_console=False):
        if is_print_to_console:
            print(data)

        abs_file_path = os.path.join(script_dir, 'log.txt')
        with open(abs_file_path, 'a') as the_file:
            the_file.write( str(time.strftime('%c')) + " : " + data)
            the_file.write('\n')

    @staticmethod
    def set_error_log(data, is_print_to_console=False):
        if is_print_to_console:
            print("Error:" + data)

        session_id = globals.configs['session_id']
        FileModule().write_file_line(
            logs_dir,
            file_name='log_' + session_id + '.txt',
            line=time.strftime('%c') + " : " + str(data)
        )
        value, traceback = sys.exc_info()
        if hasattr(value, 'filename'):
            print('Error %s: %s' % (value.filename, value.strerror))
            FileModule().write_file_line(
                logs_dir,
                file_name='log_' + session_id + '.txt',
                line=time.strftime('%c') + " : " + 'Error %s: %s' % (value.filename, value.strerror)
            )

    def set_memory_log(self, data):
        from modules.file_module import FileModule
        FileModule().write_file_line(script_dir, file_name='memory_logs/error_log' + str(time.time()) + '.txt',  line=str(time.strftime('%c')) + " : " + data)
