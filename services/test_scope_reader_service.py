import unittest

from models.scope_model import ScopeModel
from services.scope_reader_service import ScopeReaderService


class TestScopeReaderService(unittest.TestCase):

    def test_get_scope(self):
        scope = ScopeReaderService().get_scope('test')
        self.assertEqual(isinstance(scope, ScopeModel), True)
