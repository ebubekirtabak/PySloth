import base64
import os
import re

try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover - python 2 fallback
    from urlparse import urlparse

import requests

from helpers.template_helpers import TemplateHelpers
from helpers.variable_helpers import VariableHelpers
from logger import Logger

DISPOSITION_NAME = re.compile(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)\"?", re.IGNORECASE)


class DownloadHelpers:
    """Fetches a file for a scope: either base64 into a variable, or onto disk
    so it can be send_keys'd into an upload input.

    The care here is about not handing the wrong file to an upload form. A
    response that is not 200 writes nothing, an unnamed response writes nothing,
    and the readiness variable only exists when a file is actually on disk — so
    a scope can branch on "did this order have an invoice" without guessing.
    """

    def __init__(self, driver=None):
        self.driver = driver
        self.logger = Logger()

    # -- naming -------------------------------------------------------------

    @staticmethod
    def name_from_response(response):
        disposition = response.headers.get("Content-Disposition", "")
        found = DISPOSITION_NAME.search(disposition)
        if not found:
            return ""
        # Only ever a basename: a server that answers "../../etc/passwd" must
        # not be able to write outside save_dir.
        return os.path.basename(found.group(1).strip())

    @staticmethod
    def apply_name_regex(name, pattern):
        if not pattern:
            return name
        found = re.search(pattern, name or "")
        if not found:
            return ""
        return found.group(1) if found.groups() else found.group(0)

    # -- cookies ------------------------------------------------------------

    def session_cookies(self, url):
        """Browser cookies, but only for the host the page is already on: an
        Amazon session must not be replayed to a different API."""
        if self.driver is None:
            return {}
        try:
            here = urlparse(self.driver.current_url).netloc
        except Exception:
            return {}
        if not here or here != urlparse(url).netloc:
            return {}
        try:
            return dict((c["name"], c["value"]) for c in self.driver.get_cookies())
        except Exception:
            return {}

    # -- the action ---------------------------------------------------------

    def download(self, action):
        url = self.target_url(action)
        if not url:
            self.logger.set_log("download_file: no url, skipping")
            return

        headers = TemplateHelpers.render_all(action.get("headers", {}))
        cookies = self.session_cookies(url)
        if cookies and "Referer" not in headers:
            headers["Referer"] = self.driver.current_url

        save_dir = TemplateHelpers.render(action.get("save_dir", ""))
        pattern = action.get("name_regex")

        # An already-downloaded file is reused rather than re-fetched, but only
        # when its name can be known without the response — which needs a
        # save_path, since save_dir naming comes from the server.
        save_path = TemplateHelpers.render(action.get("save_path", "")) or self.variable(
            action.get("save_path_variable")
        )
        if action.get("skip_if_exists") and save_path and os.path.exists(save_path):
            self.publish(action, save_path, os.path.basename(save_path), 200)
            self.logger.set_log("download_file: reusing " + save_path)
            return

        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=60)
        except Exception as error:
            self.logger.set_error_log("download_file: " + str(error), True)
            self.set(action.get("status_variable"), 0)
            return

        self.set(action.get("status_variable"), response.status_code)
        if response.status_code != 200:
            # Never leave an error body on disk for something to upload.
            self.logger.set_log(
                "download_file: %s answered %s, nothing written" % (url, response.status_code)
            )
            return

        if save_dir:
            name = self.apply_name_regex(self.name_from_response(response), pattern)
            if not name:
                # Falling back to a shared name would let skip_if_exists serve
                # one order's file to every other order.
                self.logger.set_log(
                    "download_file: response had no usable filename, nothing written"
                )
                return
            extension = os.path.splitext(self.name_from_response(response))[1] or ".pdf"
            if not name.endswith(extension):
                name += extension
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            save_path = os.path.join(save_dir, name)

            if action.get("skip_if_exists") and os.path.exists(save_path):
                self.publish(action, save_path, name, response.status_code)
                self.logger.set_log("download_file: reusing " + save_path)
                return

        if save_path:
            with open(save_path, "wb") as handle:
                handle.write(response.content)
            self.publish(action, save_path, os.path.basename(save_path), response.status_code)
            self.logger.set_log("download_file: wrote " + save_path)
            return

        # No destination on disk: hand the bytes back base64 so they travel with
        # the rest of the document.
        self.set(
            action.get("variable_name"),
            base64.b64encode(response.content).decode("utf-8"),
        )

    # -- helpers ------------------------------------------------------------

    def target_url(self, action):
        if action.get("url_variable"):
            return self.variable(action["url_variable"])
        if action.get("url"):
            return TemplateHelpers.render(action["url"])
        if action.get("selector") and self.driver is not None:
            found = self.driver.find_elements_by_xpath(action["selector"])
            if found:
                return found[0].get_attribute(action.get("attribute_name", "href"))
        return ""

    def variable(self, name):
        if not name:
            return ""
        value = VariableHelpers().get_variable(name)
        return "" if value is None else str(value)

    def set(self, name, value):
        if name:
            VariableHelpers().set_variable(name, value)

    def publish(self, action, path, name, status):
        """The variables a scope branches on. ready_variable is set last and
        only here, so "it exists" always means "the file is on disk".

        It holds the path rather than True: if_exists_variable measures a value
        with len(), so a bool raises there and the branch is silently skipped —
        which looked exactly like the upload button never being clicked."""
        base, _ = os.path.splitext(name)
        self.set(action.get("path_variable"), path)
        self.set(action.get("name_variable"), base)
        self.set(action.get("status_variable"), status)
        self.set(action.get("ready_variable"), path)
