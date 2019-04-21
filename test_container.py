from unittest import TestCase

from item import Item
from container import Container
from result import Result


class TestContainer(TestCase):

    def setUp(self):
        self.sword = Item(name="sword", description="a sharp, deadly broadsword", size=8, value=5)
        self.lamp = Item(name="lamp", description="a shiny brass lamp", size=5, value=1)
        self.ruby = Item(name="ruby", description="a huge, finely cut ruby", size=3, value=100)
        self.chest = Container(name="chest",
                               description="Treasure chest carved with ancient runes", size=20, value=3, capacity=15)

    def test_add_success(self):
        expected = Result("Okay, the sword is now in the chest", success=True)
        actual = self.chest.add_item(self.sword)
        self.assertEqual(expected, actual)

    def test_add_fail_no_room(self):

        self.chest.add_item(self.sword)
        self.chest.add_item(self.lamp)
        expected = Result("Sorry, the ruby won't fit inside the chest", success=False)
        actual = self.chest.add_item(self.ruby)
        self.assertEqual(expected, actual)

    def test_describe(self):

        self.chest.add_item(self.sword)
        self.chest.add_item(self.lamp)
        self.assertEqual(str(self.chest.describe()),
                         str(Result("Treasure chest carved with ancient runes, containing: "
                                + "\n\ta sharp, deadly broadsword"
                                + "\n\ta shiny brass lamp", success=True)))

    def test_remove_success(self):

        self.chest.add_item(self.sword)
        expected = Result("You remove the sword from the chest", success=True)
        actual = self.chest.remove_item(self.sword)
        self.assertEqual(str(expected), str(actual))

    def test_remove_fail_not_found(self):

        expected = Result("The sword isn't in the chest", success=False)
        actual = self.chest.remove_item(self.sword)
        self.assertEqual(expected, actual)

