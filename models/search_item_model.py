class SearchItemModel:
    def __init__(self, class_name, type, headers, for_item, search_item, current_url,
                 enable_javascript, class_names):
        self.class_name = class_name
        self.type = type
        self.headers = headers
        self.for_item = for_item
        self.search_item = search_item
        self.current_url = current_url
        self.enable_javascript = enable_javascript
        self.class_names = class_names
