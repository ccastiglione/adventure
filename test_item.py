from unittest import TestCase
from item import Item
from result import Result


class TestItem(TestCase):

    def setUp(self):
        self.item = Item('blob', 'a generic blob')

    def test_describe(self):
        self.assertEqual(self.item.describe(), Result('a generic blob', success=True))

