class ImageHelpers:

    def _init_(self):
        pass

    @staticmethod
    def crop_image(image, border):
        return image.crop(border)
