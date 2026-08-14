import os

from logger import Logger


class PathHelpers:
    """Scopes reference custom scripts and imported action files with paths that
    are relative to the project they live in ("custom_scripts/parse_date.py"),
    but PySloth is started from its own directory, so those paths do not resolve
    on their own. PYSLOTH_PROJECT_ROOT tells PySloth where that project is."""

    CONFIG_DIRECTORY = 'configs'

    @staticmethod
    def project_root():
        return os.getenv('PYSLOTH_PROJECT_ROOT', '')

    @staticmethod
    def resolve(path):
        if not path or os.path.isabs(path) or os.path.exists(path):
            return path

        root = PathHelpers.project_root()
        if not root:
            return path

        candidates = [
            os.path.join(root, path),
            os.path.join(root, PathHelpers.CONFIG_DIRECTORY, path)
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        Logger().set_log('PathHelpers: ' + path + ' not found under ' + root)
        return path

    @staticmethod
    def interpreter(script_type):
        """The scraper runs in its own virtualenv, PYSLOTH_SCRIPT_PYTHON lets it
        run the custom scripts with the same python instead of whatever python3
        happens to be first on PATH."""
        if script_type in ('python', 'python3'):
            return os.getenv('PYSLOTH_SCRIPT_PYTHON', script_type)
        return script_type
