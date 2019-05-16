import time

from event_maker import EventMaker
from models.thread_model import ThreadModel


class SeleniumHtmlHelpers:
    def __init__(self, scope):
        self.scope = scope

    def parse_html_with_js(self, doc, script_actions):

        for action in script_actions:
            self.action_router(doc, action)


    def action_router(self, doc, script_actions):
        event_maker = EventMaker(doc)
        switch = {
            "event_loop": self.event_loop,
            "download_loop": self.download_loop,
            "event": event_maker.push_event,
            "function": event_maker.push_event,
            "null": lambda: 0,
        }

        func = switch.get(script_actions['type'], lambda: "nothing")
        return func(doc, script_actions)

    def event_loop(self, doc, action):
        event_maker = EventMaker(doc)
        elements = doc.find_elements_by_xpath(action['selector'])
        for element in elements:
            event_maker.push_event_to_element(element, action['events'])

    def download_loop(self, doc, action):
        elements = doc.find_elements_by_xpath(action['selector'])
        for element in elements:
            url = element.get_attribute(action['download_attribute'])
            thread_model = ThreadModel("thread_" + str(time.time()))
            thread_model.target = 'http_service.download_image'
            thread_model.args = {
                "url": url,
                "folder_name": search_item.download_folder,
                "headers": headers,
                "thread_name": thread_model.name
            }
            thread_model.status = "wait"
            thread_model.type = "download_thread"
            thread_model.start_time = 0
            thread_model.stop_time = 0
            self.scope.thread_controller.add_thread(thread_model)
            pass
