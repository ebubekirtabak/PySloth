class ElementHelpers:

    def __init__(self):
        pass

    @staticmethod
    def get_attribute_from_element(element, attr):
        if attr == 'text':
            return element.text
        elif attr == 'size':
            return element.size
        else:
            return element.get_attribute(attr)

