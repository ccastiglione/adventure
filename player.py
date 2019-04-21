import random
from traits import Traits
from schema import Role
from result import Success, Failure, ProximityFailure, OwnershipFailure
from container import Container
from creature import Creature


class Player(Creature):

    DEFAULT_TRAITS = Traits(evident=False)

    def __init__(self, game, location=None):
        self.traits = Traits.merge(self, None, Player.DEFAULT_TRAITS)
        super(Player, self).__init__(
            game=game, name='me', description='A travel-weary but brave adventurer',
            aliases=None, health=100, strength=75, dexterity=80, location=location)
        self.game = game
        self.vocab = game.vocabulary

    def is_valid_for_role(self, role, attempted_action):
        if role == Role.AGENT:
            return True
        else:
            return super().is_valid_for_role(role, attempted_action)

    def in_current_location(self, target):
        return target.id in self.location.items

    def is_nearby(self, target):
        return self.in_inventory(target) or self.in_current_location(target)

    def nearby_container_having(self, target):
        found_container = None
        nearby_item_ids = self.inventory.items + self.location.items
        nearby_items = [self.game.vocabulary.lookup_noun(i) for i in nearby_item_ids]
        nearby_containers = [c for c in nearby_items if isinstance(c, Container) and not c.traits.closed]
        for c in nearby_containers:
            if target.id in c.items:
                found_container = c
                break
        return found_container

    def nearby_creature_having(self, target):
        found_creature = None
        nearby_item_ids = self.inventory.items + self.location.items
        nearby_items = [self.game.vocabulary.lookup_noun(i) for i in nearby_item_ids]
        nearby_creatures = [c for c in nearby_items if isinstance(c, Creature) and c != self]
        for c in nearby_creatures:
            if target.id in c.inventory.items:
                found_creature = c
                break
        return found_creature

    def go(self, direction):
        if direction.id in self.location.exits:
            self.location.visited = True
            passage = self.location.exits[direction.id]
            r1 = passage.go(self.game, self)
            if r1.success:
                r = self.location.describe(verbose=False)
            else:
                r = r1
        else:
            r = Failure("You can't go {} from here".format(direction.name))
        return r

    def get(self, item):
        if not item.traits.portable:
            r = Failure("You can't carry around the {}!".format(item.full_name()))
        elif self.in_inventory(item):
            r = Failure("You already have the {}!".format(item.full_name()))
        elif not self.is_nearby(item):
            container = self.nearby_container_having(item)
            creature = self.nearby_creature_having(item)
            if container:
                r = self.get_from(item, container)
            elif creature:
                r = self.ask_for(creature, item)
            else:
                r = ProximityFailure(item.full_name())
        else:
            r1 = self.location.remove_item(item)
            if r1.success:
                r2 = self.inventory.add_item(item)
                if r2.success:
                    r = Success("You take the " + item.full_name())
                else:
                    self.location.add_item(item)
                    r = Failure("Your load is too heavy to pick up the {}".format(item.full_name()))
        return r

    def drop(self, item):
        r1 = self.inventory.remove_item(item)
        if r1.success:
            r2 = self.location.add_item(item)
            if r2.success:
                r = Success("You drop the " + item.full_name())
            else:
                r = Failure("You can't drop the " + item.full_name() + "here!")
        else:
            r = OwnershipFailure(item.full_name())
        return r

    def look(self, item=None):
        if item is None:
            item = self.location
            r = item.describe()
        elif self.is_nearby(item):
            r = item.describe()
        else:
            container = self.nearby_container_having(item)
            if container:
                r = item.describe()
            else:
                r = ProximityFailure(item.full_name())
        return r

    def open(self, openable):
        if self.is_nearby(openable):
            if openable.traits.closed:
                if openable.traits.locked:
                    r = Failure("You try to open the {}, but it is firmly locked"
                                .format(openable.full_name()))
                else:
                    openable.traits.closed = False
                    if isinstance(openable, Container):
                        container = openable
                        item_count = container.item_count()
                        if item_count == 0:
                            r = Success("You open the {}, which is empty".format(container.full_name()))
                        elif item_count == 1:
                            r = Success("Opening the {} reveals a {}"
                                        .format(container.full_name(),
                                                self.vocab.lookup_noun(container.items[0]).full_name()))
                        else:
                            r = Success("Opening the {} reveals: ".format(container.full_name()))
                            for item_id in container.items:
                                item = self.vocab.lookup_noun(item_id)
                                r.append("\n\t" + item.description)
                    else:
                        r = Success("You open the {}".format(openable.full_name()))
            else:
                r = Failure("The {} is already open".format(openable.full_name()))
        else:
            r = ProximityFailure(openable.full_name())
        return r

    def close(self, closeable):
        if self.is_nearby(closeable):
            if closeable.traits.closed:
                r = Failure("The {} is already closed".format(closeable.full_name()))
            else:
                closeable.traits.closed = True
                r = Success("You close the {}".format(closeable.full_name()))
        else:
            r = ProximityFailure(closeable.full_name())
        return r

    def lock_with(self, lockable, key):
        if self.is_nearby(lockable):
            if lockable.traits.locked:
                r = Failure("The {} is already locked".format(lockable.full_name()))
            else:
                if key.can_lock(lockable):
                    lockable.traits.locked = True
                    r = Success("The {} is now locked".format(lockable.full_name()))
                else:
                    r = Failure("The {} cannot be locked with the {}!"
                                .format(lockable.full_name(), key.full_name()))
        else:
            r = ProximityFailure(lockable.full_name())
        return r

    def unlock_with(self, lockable, key):
        if self.is_nearby(lockable) or self.nearby_container_having(lockable):
            if not lockable.traits.locked:
                r = Failure("The {} is already unlocked".format(lockable.full_name()))
            else:
                if key.can_lock(lockable):
                    lockable.traits.locked = False
                    r = Success("The {} is now unlocked".format(lockable.full_name()))
                else:
                    r = Failure("The {} cannot be unlocked with the {}!"
                                .format(lockable.full_name(), key.full_name()))
        else:
            r = ProximityFailure(lockable.full_name())
        return r

    def diagnose(self):
        return Success("Health: {}; strength: {}".format(self.health, self.strength))

    def list_inventory(self):
        if len(self.inventory.items) > 0:
            r = Success("You are carrying:")
            for item_id in self.inventory.items:
                item = self.vocab.lookup_noun(item_id)
                r.append("\n\t" + item.description)
        else:
            r = Success("You're not carrying anything")
        return r

    def put_in(self, item, container):
        if not self.is_nearby(container):
            r = ProximityFailure(container.full_name())
        else:
            if not self.is_nearby(item):
                r = ProximityFailure(item.full_name())
            else:
                if container == item:
                    r = Failure("You can't put the {} {} itself!"
                                .format(container.full_name(), container.put_preposition))
                else:
                    if self.in_inventory(item):
                        source = self.inventory
                    else:
                        source = self.location
                    r1 = source.remove_item(item)
                    if r1.success:
                        r2 = container.add_item(item)
                        if r2.success:
                            r = Success("The {} {} now {} the {}"
                                        .format(item.full_name(),
                                                item.existential(),
                                                container.put_preposition, container.full_name()))
                        else:
                            source.add_item(item)
                            r = r2
                    else:
                        r = r1
        return r

    def get_from(self, item, container):
        if isinstance(container, Creature):
            r = self.ask_for(container, item)
        else:
            if not self.is_nearby(container):
                r = ProximityFailure(container.full_name())
            else:
                r1 = container.remove_item(item)
                if r1.success:
                    r2 = self.inventory.add_item(item)
                    if r2.success:
                        r = Success("You take the {} from the {}".format(item.full_name(), container.full_name()))
                    else:
                        container.add_item(item)
                        r = r2
                else:
                    r = r1
        return r

    def consume(self, edible, adjective, verb):
        if not self.is_nearby(edible):
            r = ProximityFailure(edible.full_name())
        else:
            self.health += edible.healing
            if self.in_inventory(edible):
                edible.consume_from(self.inventory)
            else:
                edible.consume_from(self.location)
            r = Success("You {} the {} {}".format(verb, adjective, edible.full_name()))
        return r

    def eat(self, edible): return self.consume(edible, 'delicious', 'eat')

    def drink(self, edible): return self.consume(edible, 'refreshing', 'drink')

    def greet(self, creature):
        if not self.is_nearby(creature):
            r = ProximityFailure(creature.full_name())
        else:
            r = creature.respond_to_greeting()
        return r

    def give_to(self, item, creature):
        if not self.is_nearby(creature):
            r = ProximityFailure(creature.full_name())
        elif not self.in_inventory(item):
            r = OwnershipFailure(item.full_name())
        elif item in creature.wanted_items:
            r1 = self.inventory.remove_item(item)
            if r1.success:
                r2 = creature.inventory.add_item(item)
                if r2.success:
                    creature.become_friendly()
                    r = Success("The {} gratefully accepts the {}".format(creature.full_name(), item.full_name()))
                else:
                    self.inventory.add_item(item)
                    r = r2
            else:
                r = r1
        else:
            r = Failure("The {} politely declines to take the {}".format(creature.full_name(), item.full_name()))
        return r

    def ask_for(self, creature, item):
        if not self.is_nearby(creature):
            r = ProximityFailure(creature.full_name())
        elif not creature.in_inventory(item):
            r = Failure("The {} doesn't have the {}".format(creature.full_name(), item.full_name()))
        elif not creature.traits.friendly or item in creature.wanted_items:
            r = Failure("The {} is unwilling to part with the {}".format(creature.full_name(), item.full_name()))
        else:
            r1 = creature.inventory.remove_item(item)
            if r1.success:
                r2 = self.inventory.add_item(item)
                if r2.success:
                    r = Success("The {} gladly hands over the {} to you"
                                .format(creature.full_name(), item.full_name()))
                else:
                    creature.inventory.add_item(item)
                    r = r2
            else:
                r = r1
        return r

    def hit_with(self, creature, weapon):
        if not self.is_nearby(creature):
            r = ProximityFailure(creature.full_name())
        elif not self.in_inventory(weapon):
            r = OwnershipFailure(weapon.full_name())
        else:
            if not creature.traits.hostile:
                creature.become_hostile()
            attack_difficulty = random.randint(0, 100)
            if weapon.accuracy < attack_difficulty:
                r = Failure("Your attack misses!")
            else:
                creature.health -= weapon.damage
                if creature.is_alive():
                    r = Success("You hit the {}. It reels from your attack!".format(creature.full_name()))
                else:
                    r = Success(("You deal the {} a fatal blow. It falls to the ground dead, "
                                + "and its body dissolves into the hungry earth").format(creature.full_name()))
                    for item_id in creature.inventory.items:
                        item = self.game.vocabulary.lookup_noun(item_id)
                        creature.inventory.remove_item(item)
                        self.location.add_item(item)
                    self.location.remove_item(creature, force=True)
                    creature.location = None
        return r

    def throw(self, throwable, target=None):
        if not self.in_inventory(throwable):
            r = OwnershipFailure(throwable.full_name())
        elif target and not self.is_nearby(target):
            r = ProximityFailure(throwable.full_name())
        else:
            if throwable.size > 30:
                message = "You heave the {} {}; it falls to the ground {}"
                direction = "into the air"
                result = "with a solid thunk"
            elif 10 < throwable.size <= 30:
                message = "You lob the {} {}; it hits the ground {}"
                direction = "across the room"
                result = "and rolls to a stop"
            else:  # throwable.size < 10
                message = "You toss the {} {}; it comes back down {}"
                direction = "into the air"
                result = "with a soft plop"

            if target:
                direction = "at the {}, but miss".format(target.full_name())

            if throwable.traits.fragile:
                result = "and smashes to bits"
                self.inventory.remove_item(throwable)
            else:
                self.drop(throwable)
            r = Failure(message.format(throwable.full_name(), direction, result))

        return r

