from traits import Traits
from item import Item


class Key(Item):

    DEFAULT_TRAITS = Traits()

    def __init__(self, game, name, description, aliases=None, traits=None):
        self.traits = Traits.merge(self, traits, Key.DEFAULT_TRAITS)
        super(Key, self).__init__(game, name, description, aliases)
        self.add_instrument_role('lock')
        self.add_instrument_role('unlock')
        self.key_for = set()

    def set_lockable(self, lockable):
        self.key_for.add(lockable.id)

    def can_lock(self, lockable):
        return lockable.id in self.key_for
