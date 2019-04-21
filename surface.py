from traits import Traits
from container import Container


class Surface(Container):

    MAX_CAPACITY = Container.MAX_CAPACITY
    DEFAULT_TRAITS = Traits(closed=False, portable=False, surface=True)

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, capacity=MAX_CAPACITY):
        self.traits = Traits.merge(self, traits, Surface.DEFAULT_TRAITS)
        super(Surface, self).__init__(game, name, description, aliases, traits,
                                      size=size, value=value, capacity=capacity)
        self.put_preposition = 'on'

    def append_container_description(self, description):
        item_count = len(self.items)
        if item_count == 1:
            item = self.vocab.lookup_noun(self.items[0])
            description.append(", with {} {} on it"
                               .format(item.article(), item.full_name()))
        elif item_count > 1:
            description.append("\nOn the {} are: ".format(self.full_name()))
            for item_id in self.items:
                item = self.vocab.lookup_noun(item_id)
                description.append("\n\t" + item.article().capitalize() + " " + item.full_name())
        return description
