class Modifier:

    def __init__(self, game, name, aliases=None):
        self.game = game
        self.name = name
        if aliases is None:
            self.aliases = []
        else:
            self.aliases = aliases

    @classmethod
    def create(cls, game, name, aliases=None):
        m = Modifier(game, name, aliases)
        game.vocabulary.register_adjective(m)
        return m
