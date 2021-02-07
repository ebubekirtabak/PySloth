class LXMLElementHelpers:

    def __init__(self):
        pass

    def get_attribute_from_element(self, element, action_object):
        attr = action_object["attribute_name"]
        if attr.startswith('style:'):
            return self.get_style_from_element(element, attr.split(':')[1])
        elif attr == 'text':
            return element.text
        elif attr == 'size':
            return element.size
        elif attr == 'src':
            return self.get_src_from_element(element, action_object)
        else:
            return element.attrib[attr]

    @staticmethod
    def encode_image(image_url, action_object):
        convert_type = action_object["as"]
        if convert_type == "base64":
            return ImageHelpers().encode_base64_from_url(image_url)

    def get_src_from_element(self, element, action_object):
        attr = action_object['attribute_name']
        src = element.get_attribute(attr)
        if "as" in action_object:
            return self.encode_image(src, action_object)
        else:
            return src

    @staticmethod
    def get_style_from_element(element, attr):
        return element.value_of_css_property(attr)