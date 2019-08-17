import unittest
from helpers.variable_helpers import VariableHelpers


class TestVariableHelpers(unittest.TestCase):

    def test_load_scope_variable(self):
        VariableHelpers().load_scope_variables()

    def test_set_variable(self):
        VariableHelpers().set_variable('test', 'test_value')

    def test_get_variables(self):
        self.test_load_scope_variable()
        self.test_set_variable()
        assert VariableHelpers().get_variable('test') == 'test_value'


if __name__ == '__main__':
    unittest.main()
