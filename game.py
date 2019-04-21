from collections import deque
from creature import Creature
from vocabulary import Vocabulary
from result import Success
from config import Config
from command import Command
from route import ConsoleRoute


class Game:

    HISTORY_LENGTH = 10

    def __init__(self, name='the Game', prompt='>> ', route=None):
        self.name = name
        self.prompt = prompt
        self.route = route if route else ConsoleRoute(prompt=self.prompt)
        self.config = Config('/tmp/gameConfig')
        self.player = None
        self.vocabulary = Vocabulary()
        self.command_history = deque(maxlen=Game.HISTORY_LENGTH + 1)
        self.turns = 0
        self.score = 0
        self.setup()

    def setup(self):
        self.config.setup(self)

    def help(self):
        r = Success("Available commands are: \n")
        r.append(', '.join(self.vocabulary.get_valid_verbs()))
        return r

    def exit_game(self):
        self.route.send_output(self.status().message)
        exit(0)

    def history(self):
        r = Success("Recent command history: \n")
        if len(self.command_history) > 0:
            for c in self.command_history:
                r.append("\n|" + self.prompt + c.input_text)
        else:
            r.append("(no commands yet entered)")
        r.append("\n")
        return r

    def move_creature(self, creature, location, destination):
        location.remove_item(creature)
        destination.add_item(creature)
        creature.location = destination

    def is_player(self, creature):
        return creature.id == self.player.id

    def get_living_creatures(self):
        creatures = self.vocabulary.get_objects_of_class(Creature)
        return [c for c in creatures if c.is_alive() and not self.is_player(c)]

    def status(self):
        r = Success("You have a score of {} after {} turns".format(self.score, self.turns))
        return r

    def update_game(self):
        self.turns += 1
        living_creatures = self.get_living_creatures()
        if len(living_creatures) > 0:
            for c in living_creatures:
                r = c.update(self, self.player)
                if r:
                    self.route.send_output(r.message)
                if not self.player.is_alive():
                    self.route.send_output("You have died ... ")
                    self.exit_game()

    def init_game(self):
        self.route.set_banner(self.name)
        self.route.send_output(self.player.look())

    def manage_turn(self):
        player_input = self.route.receive_input()
        if len(player_input) > 0:
            command = Command(self)
            syntax_result = command.parse_input(player_input)
            if syntax_result.success:
                semantic_result = command.assign_roles()
                if semantic_result.success:
                    result = command.execute()
                else:
                    result = semantic_result
            else:
                result = syntax_result
            self.command_history.append(command)
            if len(self.command_history) > Game.HISTORY_LENGTH:
                self.command_history.popleft()
            self.route.send_output(result.message)
            self.update_game()


if __name__ == "__main__":
    game = Game(name="ADVENTURE QUEST")
    game.init_game()
    while True:
        game.manage_turn()
