from item import Traits, Item


class Consumable(Item):

    DEFAULT_TRAITS = None

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, healing=0):
        self.traits = Traits.merge(self, traits, Consumable.DEFAULT_TRAITS)
        super(Consumable, self).__init__(game, name, description, aliases, size=size, value=value)
        self.consumed = None
        self.healing = healing

    def add_consumed(self, consumed_item):
        self.consumed = consumed_item

    def consume_from(self, location):
        r = location.remove_item(self)
        if r.success and self.consumed is not None:
            location.add_item(self.consumed)
        return r


class Edible(Consumable):

    DEFAULT_TRAITS = None

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, healing=0):
        self.traits = Traits.merge(self, traits, Edible.DEFAULT_TRAITS)
        super(Edible, self).__init__(game, name, description, aliases, size=size, value=value,
                                     healing=healing)
        self.add_theme_role('eat')


class Drinkable(Consumable):

    DEFAULT_TRAITS = Traits(portable=False)

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, healing=0):
        self.traits = Traits.merge(self, traits, Drinkable.DEFAULT_TRAITS)
        super(Drinkable, self).__init__(game, name, description, aliases, size=size, value=value,
                                        healing=healing)
        self.add_theme_role('drink')
