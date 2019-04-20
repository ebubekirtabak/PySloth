import time
import logger
import os

script_dir = os.path.dirname(__file__)


class FileModule:

    def __init__(self, file_name):
        self.file_name = file_name


    @staticmethod
    def check_directory(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def get_short_file_name(file_name, max_len):
        try:
            while len(file_name) > max_len:
                if '?' in file_name:
                    file_name = file_name[0:file_name.index('?')]
                else:
                    file_extension = file_name[file_name.rindex('.'):len(file_name)]
                    file_name = file_name[0:file_name.rindex('.')]
                    if len(file_name) > max_len:
                        file_name = file_name[0:max_len]
                        file_name = file_name + str(time.time()) + '.' + file_extension
                    else:
                        file_name = file_name + '.' + file_extension

            return file_name
        except Exception as e:
            logger.set_error_log("File name could not be shortened. (" + file_name + "): "
                                 + str(e))
            return file_name

    @staticmethod
    def write_file_line(self, dir=script_dir, file_name=None, line=None):
        try:
            self.check_directory(dir)
            abs_file_path = os.path.join(dir, file_name)
            with open(abs_file_path, 'a') as the_file:
                the_file.write(line)
                the_file.write('\n')
        except Exception as e:
            print(e)
