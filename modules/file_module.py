import time
import logger


class FileModule:

    def __init__(self, file_name):
        self.file_name = file_name

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
