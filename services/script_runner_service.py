import subprocess

from logger import Logger


class ScriptRunnerService:

    def __init__(self, script_options):
        self.script_options = script_options
        self.logger = Logger()

    def run(self):

        type = self.script_options['type']

        if type == "python":
            subprocess.call(['python3', self.script_options['script']])
        elif type == "python3":
            subprocess.call(['python3', self.script_options['script']])

    def get_script_result(self, *params):
        try:
            type = self.script_options['type']
            process_output = ''
            if type == "python":
                process_output = subprocess.check_output('python ' + self.script_options['script'] + ' ' + params, shell=True)
            elif type == "python3":
                command = ['python3', self.script_options['script']]
                for param in params:
                    command.append(param)

                self.logger.set_log("run script: " + str(command))
                process_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

            result = process_output.decode("utf-8")
            self.logger.set_log("script result: " + result, True)
            return result
        except Exception as e:
            self.logger.set_log("custom_script Exception: " + str(e), True)
            return ''

