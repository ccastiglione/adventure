from traits import Traits
from thing import Thing
from result import Success, Failure


class Passage(Thing):

    DEFAULT_TRAITS = None
    DEFAULT_FAIL_RESULT = Failure("You can't go that way")

    def __init__(self, game, name, location, direction, destination, description,
                 condition, fail_result, after=None, traits=None):
        self.traits = Traits.merge(self, traits, Passage.DEFAULT_TRAITS)
        super(Passage, self).__init__(game, name, aliases=None)
        self.vocab = game.vocabulary
        self.location = location.id
        self.direction = direction.id
        self.destination = destination.id
        self.description = description
        self.condition = condition
        self.after = after
        if fail_result:
            self.fail_result = fail_result
        else:
            self.fail_result = Passage.DEFAULT_FAIL_RESULT

    def set_direction(self, direction):
        self.direction = direction.id

    def set_destination(self, destination):
        self.destination = destination.id

    def go(self, game, creature):
        if self.condition(game, creature):
            location = self.vocab.lookup_noun(self.location)
            destination = self.vocab.lookup_noun(self.destination)
            game.move_creature(creature, location, destination)
            r = Success("Creature moved from {} to {}".format(location.name, destination.name))
            if self.after:
                r = self.after(game, creature, location, destination)
        else:
            r = self.fail_result
        return r

