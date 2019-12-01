import unittest
from urllib.request import urlopen

from helpers.recaptcha_helpers import RecaptchaHelpers


class TestRecaptchaHelpers(unittest.TestCase):

    def test_solve_captcha(self):
        size = {'height': 100, 'width': 100}
        keyword = 'bike'
        url = './payload.jpeg'
        api_key = ''
        RecaptchaHelpers().solve_captcha(url, keyword, size, api_key)

    def test_get_calculate_size(self):
        image_size = {'height': 380, 'width': 380}
        sizes = (450, 450)
        size = {'height': 130, 'width': 130}
        size = RecaptchaHelpers().get_calculate_size(sizes, image_size, size)
        assert size['height'] == 153
        assert size['width'] == 153

if __name__ == '__main__':
    unittest.main()



