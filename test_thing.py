from unittest import TestCase
from action import Action
from thing import Thing
from schema import Role


class TestThing(TestCase):

    def setUp(self):
        self.thing = Thing(name='thing')
        self.action1 = Action.create(name='action1')
        self.action2 = Action.create(name='action2')
        self.thing.add_agent_role(verb='action1')

    def test_add_role(self):
        self.thing.add_agent_role(verb='action2')
        self.assertTrue(self.thing.is_valid_agent(self.action2))

    def test_is_valid_for_role(self):
        self.thing.add_role(Role.THEME, 'action2')
        self.assertTrue(self.thing.is_valid_for_role(Role.THEME, self.action2))


