import unittest
import globals

from services.script_runner_service import ScriptRunnerService


class TestScriptRunnerService(unittest.TestCase):
    test_value = "https://translate.googleusercontent.com/translate_c?anno=2&depth=1&hl=tr&rurl=translate.google.com.tr&sl=auto&sp=nmt4&tl=tr&u=https://www.linkedin.com/company/evolute-inc-%3Ftrk%3Dpublic_profile_topcard_current_company&xid=25657,15700021,15700186,15700191,15700256,15700259,15700262,15700265,15700271,15700283&usg=ALkJrhgaYERksqMB_esVCPR1SE2EEYbIIw"
    test_array = [
        "https://translate.googleusercontent.com/translate_c?anno=2&depth=1&hl=tr&rurl=translate.google.com.tr&sl=auto&sp=nmt4&tl=tr&u=https://www.linkedin.com/company/evolute-inc-%3Ftrk%3Dpublic_profile_topcard_current_company&xid=25657,15700021,15700186,15700191,15700256,15700259,15700262,15700265,15700271,15700283&usg=ALkJrhgaYERksqMB_esVCPR1SE2EEYbIIw",
        "https://translate.googleusercontent.com/translate_c?anno=2&depth=1&hl=tr&rurl=translate.google.com.tr&sl=auto&sp=nmt4&tl=tr&u=https://www.linkedin.com/company/evolute-inc-%3Ftrk%3Dpublic_profile_topcard_current_company&xid=25657,15700021,15700186,15700191,15700256,15700259,15700262,15700265,15700271,15700283&usg=ALkJrhgaYERksqMB_esVCPR1SE2EEYbIIw"
    ]
    correct_value = "https://www.linkedin.com/company/evolute-inc-?trk=public_profile_topcard_current_company\n"
    correct_array = [
        'https://www.linkedin.com/company/evolute-inc-?trk=public_profile_topcard_current_company\n',
        'https://www.linkedin.com/company/evolute-inc-?trk=public_profile_topcard_current_company\n'
    ]

    def test_get_scope(self):
        globals.configs['session_id'] = "TestScriptRunnerService"
        options = {
                  "type": "python3",
                  "script": "../custom_scripts/url_fixer.py"
                }
        script_runner = ScriptRunnerService(options)
        new_value = script_runner.get_script_result(self.test_value)
        self.assertEqual(new_value, self.correct_value)

    def test_array_get_scope(self):
        globals.configs['session_id'] = "TestScriptRunnerService"
        options = {
                  "type": "python3",
                  "script": "../custom_scripts/url_fixer.py"
                }
        script_runner = ScriptRunnerService(options)
        new_value = script_runner.get_script_result(self.test_array)
        self.assertListEqual(new_value, self.correct_array)

