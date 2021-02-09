import base64
from io import BytesIO

from helpers.http_helpers import HttpHelpers


class ImageHelpers:

    def _init_(self):
        pass

    @staticmethod
    def crop_image(image, border):
        return image.crop(border)

    @staticmethod
    def encode_base64_from_url(image_url):
        request_data = {
            "url": image_url,
            "method": "get",
            "headers": {
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                "Content-Type": "application/json"
            },
            "params": ""
        }

        image_content = HttpHelpers().get_request_content(request_data)
        if hasattr(image_content, "content") is False or image_content.status_code != 200:
            return image_url

        buffered = BytesIO(image_content.content)
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return 'data:image/png;base64,{}'.format(image_base64)

