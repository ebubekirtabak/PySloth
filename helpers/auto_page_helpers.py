import time

import globals
from helpers.recaptcha_helpers import RecaptchaHelpers
from services.http_service import HttpServices


class AutoPageHelpers:

    def __init__(self, doc):
        self.doc = doc

    def check_page_elements(self):
        if len(self.doc.find_elements_by_xpath(globals.recaptcha_xpath)) > 0:
            self.solve_recaptcha()

    def solve_recaptcha(self):
        frame = self.doc.find_element_by_xpath(globals.recaptcha_xpath)
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
        time.sleep(1)
        self.doc.switch_to.default_content()
        time.sleep(1)
        self.doc.switch_to.frame(frame)
        time.sleep(2)
        download_button = self.doc.find_element_by_xpath("//a[@class='rc-audiochallenge-tdownload-link']")
        download_args = []
        download_args[0] = download_button.get_attribute("href")
        download_args[1] = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML," +
                              "like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64"
            }
        }
        download_args[2] = "/downloads/audios"
        http_service = HttpServices(None, None)
        audio_file = http_service.download_file(download_args)

        captcha_text = RecaptchaHelpers().solve_with_speech_to_text(audio_file['path'])
        element = self.doc.find_element_by_xpath("//*[@id='audio-response']")
        element.send_keys(captcha_text)

