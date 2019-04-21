from unittest import TestCase
from direction import Direction
from location import Location


class TestLocation(TestCase):

    def setUp(self):
        self.north = Direction('north')
        self.west = Direction('west')
        self.room1 = Location("Ballroom", "A well furnished ballroom")
        self.room2 = Location("Family Room", "A well furnished family room")
        self.room3 = Location("Bathroom", "A small and dingy bathroom")

    def test_add_exit(self):
        self.room1.add_exit(self.north, self.room2)
        self.assertEqual(1, len(self.room1.exits))
        self.assertEqual(self.room2.id, self.room1.exits[self.north.id])

    def test_list_exits(self):
        self.room1.add_exit(self.north, self.room2)
        self.room1.add_exit(self.west, self.room3)
        self.assertEqual("north, west", str(self.room1.list_exits()))

    def test_describe_verbose(self):
        self.assertEqual(str(self.room1.describe(verbose=True)),
                         "\n----Ballroom----\n\n"
                         + "A well furnished ballroom")

