class LXMLElementHelpers:

    def __init__(self):
        pass

    def get_attribute_from_element(self, element, attr):
        if attr.startswith('style:'):
            return self.get_style_from_element(element, attr.split(':')[1])
        elif attr == 'text':
            return element.text
        elif attr == 'size':
            return element.size
        else:
            return element.attribute[attr]

    @staticmethod
    def get_style_from_element(element, attr):
        return element.value_of_css_property(attr)