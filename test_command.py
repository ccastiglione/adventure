from unittest import TestCase

import vocabulary
from schema import Role
from item import Item
from location import Location
from player import Player
from command import Command
from game import Game


class TestCommand(TestCase):

    def setUp(self):
        vocabulary.reset_nouns()
        nothing = Item('nothing', 'Nothing')
        nowhere = Location('nowhere', 'Nowhere')
        r = nowhere.add_item(nothing)
        self.assertTrue(r.success)
        self.game = Game()
        self.player = Player(location=nowhere, game=self.game)

    def test_success(self):
        command = Command('get nothing')
        self.assertIsNotNone(command)
        self.assertEqual(command.action, vocabulary.lookup_verb('get'))
        self.assertTrue(vocabulary.lookup_noun_by_name('nothing') in command.schema[Role.PATIENT])
        r = command.execute(self.player)
        self.assertTrue(r.success)
        self.assertEqual(r.message, "You take the nothing")

    def test_failure(self):
        command = Command('bloop floop')
        self.assertIsNotNone(command)
        self.assertIsNone(command.action)
        self.assertIsNone(command.schema[Role.PATIENT])
        r = command.execute(self.player)
        self.assertFalse(r.success)
        self.assertEqual(r.message, "Sorry, I don't know how to bloop the floop")

    def test_too_many_words(self):
        command = Command('flip flop flap')
        self.assertIsNotNone(command)
        r = command.execute(self.player)
        self.assertFalse(r.success)
        self.assertEqual(r.message, "Sorry, I don't know how to flip the flap")

    def test_only_one_word(self):
        command = Command('look')
        self.assertIsNotNone(command)
        r = command.execute(self.player)
        print(r.message)
        self.assertTrue(r.success)





