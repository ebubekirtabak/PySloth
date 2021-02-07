import json
import re
import subprocess
import sys

from helpers.variable_helpers import VariableHelpers
from logger import Logger


class ScriptRunnerService:

    def __init__(self, script_options):
        self.script_options = script_options
        self.logger = Logger()

    def run(self):
        try:
            type = self.script_options['type']

            command = [type, self.script_options['script']]

            if 'params' in self.script_options:
                params = self.script_options['params']
                for param in params:
                    if param.startswith("${"):
                        params_name = re.search("{(.*?)}", param)
                        param_value = VariableHelpers().get_variable(params_name.group(1))
                        command.append(json.dumps(param_value))
                    else:
                        command.append(param)

            self.logger.set_log("run script: " + str(command))
            process_output = subprocess.check_output(command, shell=False, stderr=subprocess.PIPE)
            result = process_output.decode("utf-8")
            self.logger.set_log("script result: " + result)
            result = self.get_value_by_type(result)

            if 'variable_name' in self.script_options:
                VariableHelpers().set_variable(self.script_options['variable_name'], result)

        except Exception as e:
            self.logger.set_log("custom_script Exception: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

    def get_value_by_type(self, result):
        if 'variable_type' not in self.script_options or type == "json":
            result = json.loads(result)
        elif self.script_options['variable_type'] == "text":
            result = result.replace("\n", '')
        elif self.script_options['variable_type'] == "int":
            result = int(result.replace("\n", ''))

        return result

    def get_script_result(self, params):
        try:
            type = self.script_options['type']
            process_output = ''
            if type == "python":
                process_output = subprocess.check_output('python ' + self.script_options['script'] + ' ' + params, shell=True)
            elif type == "python3":
                if isinstance(params, list):
                    result = []
                    for param in params:
                        command = ['python3', self.script_options['script']]
                        command.append(param)
                        self.logger.set_log("run script: " + str(command))
                        process_output = subprocess.check_output(command, shell=False, stderr=subprocess.PIPE)
                        result.append(process_output.decode("utf-8"))
                else:
                    command = ['python3', self.script_options['script'], params]
                    self.logger.set_log("run script: " + str(command))
                    process_output = subprocess.check_output(command, shell=False, stderr=subprocess.PIPE)
                    result = process_output.decode("utf-8")
                    self.logger.set_log("script result: " + result)

            return result
        except Exception as e:
            self.logger.set_log("custom_script Exception: " + str(e), True)
            return ''

