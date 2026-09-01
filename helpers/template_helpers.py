import os
import re

try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover - python 2 fallback
    from urlparse import urlparse

from helpers.variable_helpers import VariableHelpers

PLACEHOLDER = re.compile(r"\$\{([^}]+)\}")


class TemplateHelpers:
    """Fills ${...} placeholders in a scope string.

        ${order_id}                     a scope variable
        ${env:SCRAPED_ORDERS_API_KEY}   an environment variable
        ${env_origin:SCRAPED_ORDERS_API_URL}
                                        the scheme+host of a URL setting, so one
                                        setting also addresses sibling endpoints

    Credentials and hosts stay in the environment rather than in the scope JSON,
    which is committed to a repository.
    """

    @staticmethod
    def origin_of(url):
        parts = urlparse(url or "")
        if not parts.scheme or not parts.netloc:
            return url or ""
        return "%s://%s" % (parts.scheme, parts.netloc)

    @staticmethod
    def resolve(name):
        name = name.strip()

        if name.startswith("env_origin:"):
            return TemplateHelpers.origin_of(os.getenv(name[len("env_origin:"):].strip(), ""))
        if name.startswith("env:"):
            return os.getenv(name[len("env:"):].strip(), "")

        value = VariableHelpers().get_variable(name)
        return "" if value is None else str(value)

    @staticmethod
    def render(template):
        if not isinstance(template, str):
            return template
        return PLACEHOLDER.sub(lambda match: TemplateHelpers.resolve(match.group(1)), template)

    @staticmethod
    def render_all(values):
        """Every value of a dict — used for request headers, where the key is
        fixed and only the value carries a secret."""
        if not isinstance(values, dict):
            return {}
        return dict((key, TemplateHelpers.render(value)) for key, value in values.items())
