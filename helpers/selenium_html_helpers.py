from event_maker import EventMaker


class SeleniumHtmlHelpers:
    def __init__(self):
        pass

    def parse_html_with_js(self, doc, script_actions):

        for action in script_actions:
            '''namedtuple("ScriptActionModel", scope.keys())(*scope.values())'''
            if action['type'] == 'event*':
                elements = doc.find_elements_with_xpath(action['selector'])
                for element in elements:
                    self.action_router(element, action)
            else:
                self.action_router(doc, action)

        pass

    def action_router(self, doc, script_actions):
        event_maker = EventMaker(doc)
        switch = {
            "event*": event_maker.push_event_to_element(doc, script_actions['event*']),
            "event": event_maker.push_event(doc, script_actions['event']),
            "function": event_maker.push_event(doc, script_actions),
        }

        switch[script_actions['type']]()
