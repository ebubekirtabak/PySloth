import unittest
import nose
from helpers.image_helpers import ImageHelpers


class TestImageHelpers(unittest.TestCase):

    def test_encode_base64_from_url(self):
        fine_image_url = "https://images.unsplash.com/photo-1612839943360-ec0a9b9f6666?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=2425&q=80"
        result = ImageHelpers().encode_base64_from_url(fine_image_url)
        assert result.find("data:image/png;base64") > -1
        bad_image_url = "https://images.unsplash.com/photo-1612839943360-ec0a9b9f6666.jj?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=2425&q=80"
        bad_result = ImageHelpers().encode_base64_from_url(bad_image_url)
        assert bad_result == bad_image_url


if __name__ == '__main__':
    unittest.main()
