from traits import Traits
from item import Item


class Weapon(Item):

    DEFAULT_TRAITS = None

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, damage=10, defense=10, accuracy=50):
        self.traits = Traits.merge(self, traits, Weapon.DEFAULT_TRAITS)
        super(Weapon, self).__init__(game, name, description, aliases, size=size, value=value)
        self.add_instrument_role('hit')
        self.damage = damage
        self.defense = defense
        self.accuracy = accuracy
