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

    def get_script_result(self):

        type = self.script_options['type']
        process_output = ''
        if type == "python":
            process_output = subprocess.check_output(['python3', self.script_options['script']])
        elif type == "python3":
            process_output = subprocess.check_output(['python3', self.script_options['script']])

        self.logger.set_log("get_script_result: " + process_output)
        return process_output
