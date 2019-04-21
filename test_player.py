from unittest import TestCase
from player import Player
from item import Item
from direction import Direction
from location import Location
from game import Game


class TestPlayer(TestCase):

    def setUp(self):
        self.north = Direction('north')
        self.south = Direction('south')
        self.west = Direction('west')
        self.pool_table = Item('pool table', 'A felt lined pool table', 100, 10)
        self.room1 = Location("Ballroom", "A well furnished ballroom")
        self.room1.add_item(self.pool_table)
        self.tv = Item('TV', 'The family television', 10, 50)
        self.couch = Item('couch', 'A comfy couch', 20, 100)
        self.room2 = Location("Family Room", "A well furnished family room")
        self.room2.add_item(self.couch)
        self.room2.add_item(self.tv)
        self.room1.add_exit(self.north, self.room2)
        self.room2.add_exit(self.south, self.room1)

        self.player = Player(location=self.room1, game=Game())

    def test_go_success(self):
        self.assertEqual(self.player.location, self.room1)
        r = self.player.go(self.north)
        self.assertTrue(r.success)
        self.assertEqual(self.player.location, self.room2)

    def test_go_failure(self):
        self.assertEqual(self.player.location, self.room1)
        r = self.player.go(self.south)
        self.assertFalse(r.success)
        self.assertEqual(self.player.location, self.room1)

    def test_get_success(self):
        self.player.location.add_item(self.tv)
        self.assertFalse(self.tv.id in self.player.inventory.items)
        r = self.player.get(self.tv)
        self.assertTrue(r.success)
        self.assertTrue(self.tv.id in self.player.inventory.items)

    def test_get_failure_item_too_heavy(self):
        self.assertFalse(self.pool_table in self.player.inventory.items)
        self.player.inventory.capacity = self.pool_table.size - 1
        r = self.player.get(self.pool_table)
        self.assertFalse(r.success)
        self.assertFalse(self.pool_table in self.player.inventory.items)

    def test_get_failure_item_not_here(self):
        self.assertFalse(self.tv in self.player.inventory.items)
        r = self.player.get(self.tv)
        self.assertFalse(r.success)
        self.assertFalse(self.tv in self.player.inventory.items)

    def test_drop_success(self):
        self.player.inventory.add_item(self.tv)
        self.player.location.remove_item(self.tv)
        r = self.player.drop(self.tv)
        self.assertTrue(r.success)
        self.assertFalse(self.tv.id in self.player.inventory.items)
        self.assertTrue(self.tv.id in self.player.location.items)

    def test_drop_failure_do_not_have(self):
        r = self.player.drop(self.tv)
        self.assertFalse(r.success)

    def test_look_at_location(self):
        r = self.player.look()
        self.assertEqual(str(r),
                         "\n----Ballroom----\n\n"
                         + "A well furnished ballroom\n\n"
                         + "Exits lead north\n"
                         + "There is a pool table here")

    def test_check_inventory_empty(self):
        r = self.player.list_inventory()
        self.assertEqual(str(r), "You're not carrying anything")

    def test_check_inventory_items(self):
        self.player.inventory.add_item(self.tv)
        r = self.player.list_inventory()
        self.assertEqual(str(r), "You are carrying:\n\tThe family television")

