import unittest

from transactions.mongo_transactions import MongoTransactions


class TestMongoTransactions(unittest.TestCase):

    def test_is_usable_value(self):
        assert MongoTransactions.is_usable_value('Ali Veli') is True
        assert MongoTransactions.is_usable_value('**********') is False
        assert MongoTransactions.is_usable_value('+** ************') is False
        assert MongoTransactions.is_usable_value('') is False
        assert MongoTransactions.is_usable_value('-') is False
        assert MongoTransactions.is_usable_value(None) is False
        assert MongoTransactions.is_usable_value(False) is True
        assert MongoTransactions.is_usable_value(['Cumhuriyet mah.', 'Türkiye']) is True
        assert MongoTransactions.is_usable_value(['42080 ********, *****', 'Türkiye']) is False
        assert MongoTransactions.is_usable_value([]) is False

    def test_split_preserved_values_keeps_masked_fields(self):
        value = {
            'order_id': 'PO-203-1',
            'buyer_name': '**********',
            'buyer_phone': '',
            'courier': 'ARAS Standard',
            'did_invoice_uploaded': False
        }
        values, set_on_insert = MongoTransactions(None, value).split_preserved_values(
            ['buyer_name', 'buyer_phone']
        )

        assert values == {
            'order_id': 'PO-203-1',
            'courier': 'ARAS Standard',
            'did_invoice_uploaded': False
        }
        assert set_on_insert == {'buyer_name': '**********', 'buyer_phone': ''}

    def test_split_preserved_values_updates_readable_fields(self):
        value = {'order_id': 'PO-203-1', 'buyer_name': 'Ali Veli'}
        values, set_on_insert = MongoTransactions(None, value).split_preserved_values(['buyer_name'])

        assert values == value
        assert set_on_insert == {}

    def test_split_preserved_values_without_preserve_fields(self):
        value = {'order_id': 'PO-203-1', 'buyer_name': '**********'}
        values, set_on_insert = MongoTransactions(None, value).split_preserved_values([])

        assert values == value
        assert set_on_insert == {}


if __name__ == '__main__':
    unittest.main()
