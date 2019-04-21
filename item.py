from thing import Traits, VisibleThing


class Item(VisibleThing):

    MAX_SIZE = 999
    DEFAULT_TRAITS = Traits(portable=True, evident=True)

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0):
        self.traits = Traits.merge(self, traits, Item.DEFAULT_TRAITS)
        super(Item, self).__init__(game, name, description, aliases)
        self.size = size
        self.value = value
        if self.traits.portable:
            self.add_theme_role('throw')
            self.add_theme_role('take')
            self.add_theme_role('drop')
            self.add_theme_role('put')
            self.add_theme_role('get')
            self.add_theme_role('give')
            self.add_theme_role('ask')
