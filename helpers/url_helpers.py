# -*- coding: utf-8 -*-

import urllib
import urllib.request
import urllib.parse
from logger import Logger
from lxml.html import fromstring


class UrlHelpers:

    def __init__(self):
        pass

    def get_page_html_content(self, url, data=None, headers={}):
        try:
            req = urllib.request.Request(
                url=url,
                data=data,
                headers=headers
            )
            f = urllib.request.urlopen(req)
            content = f.read()
            doc = fromstring(content)
            doc.make_links_absolute(url)
            return doc
        except ConnectionResetError as e:
            Logger().set_error_log(str(e))
        except Exception as e:
            Logger().set_error_log(str(e))

