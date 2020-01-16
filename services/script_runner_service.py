import subprocess

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
                    command.append(param)

                self.logger.set_log("run script: " + str(command))
                process_output = subprocess.check_output(command, shell=False, stderr=subprocess.PIPE)
                result = process_output.decode("utf-8")
                self.logger.set_log("script result: " + result)
        except Exception as e:
            self.logger.set_log("custom_script Exception: " + str(e), True)

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

