import time
import os
import sys
import logger
import json


script_dir = os.path.dirname(sys.modules['__main__'].__file__)


class FileModule:

    def __init__(self, file_name=None):
        self.file_name = file_name

    def check_directory(self, dir=script_dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def get_short_file_name(self, file_name, max_len=120):
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
    def read_file(dir=script_dir, file_name=None):
        try:
            abs_file_path = os.path.join(dir, file_name)
            if os.path.isfile(abs_file_path):
                with open(abs_file_path) as data:
                    return {"success": True, "data": data.read()}
            else:
                return {"success": False}
        except Exception as e:
            logger.set_error_log("read_file -> (" + dir + file_name + "): "
                                 + str(e))
            return {"success": False, "error_message": "File not found."}

    @staticmethod
    def read_json_file(dir=script_dir, file_name=None):
        try:
            abs_file_path = os.path.join(dir, file_name)
            if os.path.isfile(abs_file_path):
                with open(abs_file_path) as data:
                    return {"success": True, "data": json.load(data)}
            else:
                return {"success": False}
        except Exception as e:
            logger.set_error_log("read_file -> (" + dir + file_name + "): "
                                 + str(e))
            return {"success": False, "error_message": "File not found."}

    def write_file_line(self, dir=script_dir, file_name=None, line=None):
        try:
            self.check_directory(dir)
            abs_file_path = os.path.join(dir, file_name)
            with open(abs_file_path, 'a') as the_file:
                the_file.write(line)
                the_file.write('\n')
        except Exception as e:
            print(e)

    @staticmethod
    def if_exists_file(file_name):
        try:
            fh = open(file_name, 'r')
            return True
        except FileNotFoundError:
            return False
