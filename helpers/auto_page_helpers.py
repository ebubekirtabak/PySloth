import globals


class AutoPageHelpers:

    def __init__(self, doc):
        self.doc = doc

    def check_page_elements(self):

        if len(self.doc.find_elements_by_xpath(globals.recaptcha_xpath)) > 0:
            print("ere")