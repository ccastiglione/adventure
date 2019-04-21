from unittest import TestCase
from location import Location
from consumable import Consumable


class TestConsumable(TestCase):

    def setUp(self):
        self.consumable = Consumable('thing', 'Thing', size=0, value=0)
        self.room1 = Location('room1', 'A Room')
        self.room2 = Location('room2', 'A Room')
        self.room1.add_item(self.consumable)

    def test_consume_from_current_location(self):
        self.assertIsNotNone(self.consumable)
        self.assertTrue(self.consumable.id in self.room1.items)
        r = self.consumable.consume_from(self.room1)
        self.assertTrue(r.success)
        self.assertFalse(self.consumable.id in self.room1.items)

    def test_consume_from_other_location(self):
        self.assertIsNotNone(self.consumable)
        self.assertTrue(self.consumable.id in self.room1.items)
        r = self.consumable.consume_from(self.room2)
        self.assertFalse(r.success)
        self.assertTrue(self.consumable.id in self.room1.items)
