from urllib.request import urlopen

import urllib3
from PIL import Image
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import requests
from io import BytesIO

from helpers.image_helpers import ImageHelpers
from helpers.speech_to_text_helpers import SpeechToTextHelpers


class RecaptchaHelpers:
    object_maps = {
        'bridges': [
            'bridges',
            'bridge'
        ],
        'bicycles': [
            'bicycles',
            'bike',
            'cycles',
            'cycle'
        ],
        'vehicles': [
            'vehicles',
            'vehicle',
            'car',
            'cars'
        ],
        'cars': [
            'vehicles',
            'vehicle',
            'car',
            'cars'
        ],
        'car': [
            'vehicles',
            'vehicle',
            'car',
            'cars'
        ],
        'palm trees': [
            'palm trees',
            'palm tree',
            'tree',
            'tropical'
        ],
        'traffic lights': [
            'light',
            'traffic lights',
            'traffic light'
        ],
        'crosswalks': [
            'crosswalks',
            'crossing'
        ]
    }

    def __init__(self):
        pass

    def __load_image(self):
        pass

    def solve_captcha(self, image_url, keyword, size, api_key, image_size):
        image_result = []
        cropped_images = []
        response = requests.get(image_url)
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        size = self.get_calculate_size(image.size, image_size, size)
        w_level = int(image.size[0] / size['width'])
        h_level = int(image.size[0] / size['height'])
        for h in range(h_level):
            for i in range(w_level):
                left = (i * size['width'])
                top = (h * size['height'])
                right = (i * size['width']) + size['width']
                bottom = (h * size['height']) + size['height']
                border = (left, top, right, bottom)
                cropped_image = ImageHelpers().crop_image(image, border)
                image_name = str(left) + "_" + str(top) + "_" + str(right) + "_" + str(bottom) + ".jpeg"
                cropped_images.append(image_name)
                cropped_image.save('./' + image_name)
                result = self.get_objects_from_image('./' + image_name, api_key)
                print(border)
                if result['code'] != 400:
                    is_exists = self.find_object_in_concepts(keyword,result['concepts'])
                    image_result.append({'w': i, 'h': h, 'is_exists': is_exists})
                else:
                    image_result.append({'w': i, 'h': h, 'is_exists': False})

        return image_result

    def get_objects_from_image(self, image, api_key):
        app = ClarifaiApp(api_key=api_key)
        model = app.public_models.general_model
        model.model_version = 'aa7f35c01e0642fda5cf400f543e7c40'
        image = ClImage(filename=image)
        response = model.predict([image])
        if response['status']['code'] == 10000:
            return {'code': 10000, 'concepts': self.parse_response_data(response['outputs'])}
        else:
            return {'code': 400}

    @staticmethod
    def parse_response_data(outputs):
        output = outputs[0]
        data = output['data']
        concepts = data['concepts']
        return concepts

    @staticmethod
    def get_calculate_size(image, image_size, size):
        image_width = image[0]
        image_height = image[1]
        if image_width > image_size['width']:
            diff = image_width - image_size['width']
            width_rate = int((diff / image_size['width']) * 100)
            size['width'] = int(size['width'] + ((size['width'] / 100) * width_rate))
        else:
            diff = image_size['width'] - image_width
            width_rate = int((diff / image_width) * 100)
            size['width'] = int(size['width'] - ((size['width'] / 100) * width_rate))

        if image_height > image_size['height']:
            diff = image_height - image_size['height']
            height_rate = int((diff / image_size['height']) * 100)
            size['height'] = int(size['height'] + ((size['height'] / 100) * height_rate))
        else:
            diff = image_size['height'] - image_height
            height_rate = int((diff / image_height) * 100)
            size['height'] = int(size['height'] - ((size['height'] / 100) * height_rate))

        return size

    def find_object_in_concepts(self, keyword, concepts):
        if keyword in self.object_maps.keys():
            keyword_list = self.object_maps[keyword]
            for item in concepts:
                try:
                    index = keyword_list.index(item['name'])
                    print('****' + keyword + ' == ' + item['name'])
                    return True
                except:
                    print(keyword + ' -> ' + item['name'])
        else:
            for item in concepts:
                print(keyword + ' -> ' + item['name'])
                if keyword == item['name']:
                    return True

        return False

    ''' Solve With Speech to Text'''
    @staticmethod
    def solve_with_speech_to_text(file_name):
        return SpeechToTextHelpers().convert_to_text(file_name)

