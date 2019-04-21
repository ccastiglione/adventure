from traits import Traits
from result import Result
from passage import Passage
from container import Container


class Location(Container):

    DEFAULT_TRAITS = Traits(closed=False)

    def __init__(self, game, name, description, aliases=None, traits=None, size=0, value=0):
        traits = Traits.merge(self, traits, Location.DEFAULT_TRAITS)
        super(Location, self).__init__(game, name, description, aliases=aliases, traits=traits,
                                       size=size, value=value, capacity=Container.MAX_CAPACITY)
        self.vocab = game.vocabulary
        self.exits = dict()
        self.visited = False

    def to_json(self):
        return vars(self)

    @staticmethod
    def free_passage(game, player):
        return True

    def add_exit(self, direction, destination, description=None, condition=None, fail_result=None, after=None):
        if not condition:
            condition = Location.free_passage
        passage = Passage(self.game, self.name + '-' + direction.name,
                          self, direction, destination, description, condition, fail_result, after)
        self.exits[direction.id] = passage

    def available_exits(self, game):
        return [self.exits[d] for d in self.exits if self.exits[d].condition(game, game.player)]

    def list_nondescript_exits(self):
        return ', '.join([self.vocab.lookup_noun(x).name for x in self.exits.keys() if not self.exits[x].description])

    def append_exit_description(self, description):
        special_exits = [x for x in self.exits.keys() if self.exits[x].description]
        nondescript_exits = [x for x in self.exits.keys() if not self.exits[x].description]
        description.append("\n")
        for x in special_exits:
            description.append("\n" + self.exits[x].description)
        if len(special_exits) > 0:
            if len(nondescript_exits) == 1:
                description.append("\nAnother exit leads " + self.list_nondescript_exits())
            elif len(nondescript_exits) > 1:
                description.append("\nOther exits lead " + self.list_nondescript_exits())
        else:
            if len(nondescript_exits) == 1:
                description.append("\nAn exit leads " + self.list_nondescript_exits())
            elif len(nondescript_exits) > 1:
                description.append("\nExits lead " + self.list_nondescript_exits())

    def append_compelling_items(self, description):
        for item_id in self.items:
            item = self.vocab.lookup_noun(item_id)
            if item.traits.compelling:
                description.append("\n" + item.description)

    def append_evident_items(self, description):
        for item_id in self.items:
            item = self.vocab.lookup_noun(item_id)
            if item.traits.evident and not item.traits.compelling:
                description.append("\nThere {} {} {} here"
                                   .format(item.existential(), item.article(), item.full_name()))
                if isinstance(item, Container) and not item.traits.closed:
                    item.append_container_description(description)

    def describe(self, verbose=True):
        description = Result("\n------ " + self.name + " ------", success=True)
        if verbose or not self.visited:
            description.append("\n\n" + self.description)
        self.append_compelling_items(description)
        self.append_evident_items(description)
        self.append_exit_description(description)
        return description
