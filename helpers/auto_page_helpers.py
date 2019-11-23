import time

import globals


class AutoPageHelpers:

    def __init__(self, doc):
        self.doc = doc

    def check_page_elements(self):

        if len(self.doc.find_elements_by_xpath(globals.recaptcha_xpath)) > 0:
            self.solve_recaptcha()

    def solve_recaptcha(self):
        frame = self.doc.find_element_by_xpath("//div[@class='g-recaptcha']/div/div/iframe")
        self.doc.switch_to.frame(frame)

        anchor = self.doc.find_element_by_xpath("//*[@id='recaptcha-anchor']")
        anchor.click()
        time.sleep(2)
        self.doc.switch_to.default_content()

        frame = self.doc.find_element_by_xpath("//*[@title='recaptcha challenge']")
        self.doc.switch_to.frame(frame)
        time.sleep(2)
        audio_button = self.doc.find_element_by_xpath("//button[@id='recaptcha-audio-button']")
        audio_button.click()

        self.doc.switch_to.default_content()
        self.doc.switch_to.frame(frame)

