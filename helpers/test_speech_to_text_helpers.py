import os
import unittest
import globals

from helpers.speech_to_text_helpers import SpeechToTextHelpers


class TestSpeechToTextHelpers(unittest.TestCase):

    def test_solve_captcha(self):
        file_name = os.path.join(
            globals.script_dir,
            'resources',
            'audio.mp3')
        SpeechToTextHelpers().convert_to_text(file_name)

if __name__ == '__main__':
    unittest.main()