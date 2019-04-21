import random
from traits import Traits
from item import Item
from result import Result
from container import Container


class Creature(Item):

    DEFAULT_TRAITS = Traits(portable=False, hostile=False, friendly=False, dead=False)

    def __init__(self, game, name, description, aliases=None, traits=None,
                 health=0, strength=0, dexterity=0, speed=50, activity=33, location=None,
                 entry_action=None, present_action=None, exit_action=None):
        self.traits = Traits.merge(self, traits, Creature.DEFAULT_TRAITS)
        super(Creature, self).__init__(game, name, description, aliases)
        self.health = health
        self.location = location
        self.strength = strength
        self.dexterity = dexterity
        self.last_movement = 0
        self.movement_frequency = int(100 / speed)
        self.movement_strategy = self.random_walk
        self.last_activity = 0
        self.activity_frequency = int(100 / activity)
        self.wanted_items = []
        if not entry_action:
            self.entry_action = self.default_entry
        if not exit_action:
            self.exit_action = self.default_exit
        if not present_action:
            self.present_action = self.neutral_action
        if self.location:
            self.location.add_item(self)
        self.inventory = Container(game, name + '-inv', name + "'s items",
                                   traits=Traits(closed=False),
                                   capacity=strength)
        self.add_patient_role('greet')
        self.add_patient_role('wave')
        self.add_patient_role('smile')
        self.add_patient_role('give')
        self.add_patient_role('ask')
        self.add_patient_role('kill')
        self.add_patient_role('take')

    def add_item(self, item):
        self.inventory.add_item(item)

    def remove_item(self, item):
        self.inventory.remove_item(item)

    def add_wanted_item(self, item):
        self.wanted_items.append(item)

    def become_friendly(self):
        self.traits.friendly = True
        self.present_action = self.friendly_action

    def become_hostile(self):
        self.traits.hostile = True
        self.present_action = self.hostile_action

    def default_entry(self, game, player):
        return Result("{} {} has entered the room".format(self.article().capitalize(), self.full_name()))

    def default_exit(self, game, player):
        return Result("The {} has exited the room".format(self.full_name()))

    def neutral_action(self, game, player):
        result = Result("The {} eyes you suspiciously".format(self.name))
        result.add_message("The {} glances at you quickly, then away again".format(self.name))
        result.add_message("The {} coughs nervously".format(self.name))
        result.add_message("The {} whistles tunelessly, avoiding your gaze".format(self.name))
        return result

    def friendly_action(self, game, player):
        result = Result("The {} nods its head at you in friendly greeting".format(self.name))
        result.add_message("The {} smiles warmly at you".format(self.name))
        result.add_message("The {} leans against the wall of the room".format(self.name))
        result.add_message("The {} hums a happy tune, hands in its pockets".format(self.name))
        return result

    def hostile_action(self, game, player):
        result = Result("The {} glares at you ferociously".format(self.name))
        result.add_message("The {} growls under its breath".format(self.name))
        result.add_message("The {} gnashes its teeth in anger".format(self.name))
        result.add_message("The {} clenches its fists with fury".format(self.name))
        return result

    def is_near_player(self):
        player = self.game.player
        return self.location == player.location

    def in_inventory(self, target):
        return target.id in self.inventory.items

    def is_alive(self):
        return self.health > 0

    def respond_to_greeting(self):
        if self.traits.hostile:
            result = Result("The {} snorts derisively at your greeting".format(self.name))
        elif self.traits.friendly:
            result = Result("The {} gives you a friendly wave in return".format(self.name))
        else:
            result = Result("The {} acknowledges your greeting with a curt nod".format(self.name))
        return result

    def attack(self, game, player):
        r = Result("The {} attacks ... ".format(self.name))
        attack_difficulty = random.randint(0, 100)
        if self.dexterity < attack_difficulty:
            r.append("luckily, its blow fails to connect")
        else:
            r.append("and hits you!  You stagger back in pain ... ")
            player.health -= self.strength
        return r

    def should_interact(self, game, player):
        return self.last_activity == 0 \
               or self.activity_frequency <= game.turns - self.last_activity

    def act(self, game, player):
        self.last_activity = game.turns
        r = self.present_action(game, player)
        return r

    def should_move(self, game, player):
        return self.last_movement == 0 \
            or self.movement_frequency <= game.turns - self.last_movement

    def random_walk(self, game, location):
        passages = location.available_exits(game)
        if len(passages) > 0:
            p = random.choice(passages)
            p.go(game, self)
        return self.location

    def move(self, game, player):
        self.last_movement = game.turns
        start_location = self.location
        new_location = self.movement_strategy(game, start_location)
        if start_location != player.location \
                and new_location == player.location:
            r = self.entry_action(game, player)
        elif start_location == player.location \
                and new_location != player.location:
            r = self.exit_action(game, player)
        else:
            r = None
        return r

    def update(self, game, player):
        r = None
        if self.is_near_player():
            if self.traits.hostile:
                r = self.attack(game, player)
            elif self.should_interact(game, player):
                r = self.act(game, player)
            elif self.traits.mobile:
                r = self.move(game, player)
        elif self.traits.mobile:
            r = self.move(game, player)
        return r

    def describe(self):
        r = super(Creature, self).describe()
        item_count = len(self.inventory.items)
        if item_count == 1:
            item = self.vocabulary.lookup_noun(self.inventory.items[0])
            r.append(", carrying {} {}".format(item.article(), item.name))
        elif item_count > 1:
            r.append(", carrying: ")
            for item_id in self.inventory.items:
                item = self.vocabulary.lookup_noun(item_id)
                r.append("\n\t" + item.description)
        return r

