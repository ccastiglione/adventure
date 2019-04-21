from traits import Traits
from schema import Role
from action import Action
from thing import VisibleThing


class Direction(VisibleThing):

    DEFAULT_TRAITS = Traits(ubiquitous=True)

    @classmethod
    def create(cls, game, name, alias):
        d = Direction(game, name)
        Action.create(game=game, name=name, aliases=[alias],
                      callback=lambda schema: schema[Role.AGENT].go(d))
        return d

    def __init__(self, game, name, description=None, aliases=None):
        if description is None:
            description = 'An exit leading ' + name
        self.traits = Traits.merge(self, None, Direction.DEFAULT_TRAITS)
        super(Direction, self).__init__(game, name, description, aliases)
        self.add_goal_role('go')

