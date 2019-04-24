import json
import os
import errno
import direction
import result
from result import Success, Failure, Result, WON_GAME
from schema import Scope, Role, Schema
from traits import Traits
from item import Item
from door import Door
from container import Container
from surface import Surface
from key import Key
from weapon import Weapon
from location import Location
from player import Player
from action import Action
from creature import Creature
from consumable import Edible, Drinkable
from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class Config:

    def __init__(self, config_path):
        self.setup_config_path(config_path)
        self.config_filename = config_path + '/game_data.config'
        self.game_data = dict()
        self.game_data['objects'] = {}

    @classmethod
    def setup_config_path(cls, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def load_game_data(self):
        with open(self.config_filename, 'r') as config_file:
            self.game_data = json.load(config_file)

    def save_game_data(self):
        with open(self.config_filename, 'w') as config_file:
            json.dump(self.game_data, config_file,
                      indent=4, separators=(',', ': '))

    def setup_directions(self, game):

        direction.north = direction.Direction.create(game, 'north', 'n')
        direction.south = direction.Direction.create(game, 'south', 's')
        direction.east = direction.Direction.create(game, 'east', 'e')
        direction.west = direction.Direction.create(game, 'west', 'w')
        direction.northeast = direction.Direction.create(game, 'northeast', 'ne')
        direction.northwest = direction.Direction.create(game, 'northwest', 'nw')
        direction.southwest = direction.Direction.create(game, 'southwest', 'sw')
        direction.southeast = direction.Direction.create(game, 'southeast', 'se')
        direction.up = direction.Direction.create(game, 'up', 'u')
        direction.down = direction.Direction.create(game, 'down', 'd')

    def setup_actions(self, game):

        Action.create(game, name='history', callback=lambda schema: schema[Role.AGENT].game.history())
        Action.create(game, name='help', callback=lambda schema: schema[Role.AGENT].game.help())
        Action.create(game, name='status',
                      aliases=['score'], callback=lambda schema: schema[Role.AGENT].game.status())
        Action.create(game, name='exit',
                      aliases=['quit', 'end', 'done'],
                      callback=lambda schema: game.exit_game())
        Action.create(game, name='diagnose',
                      callback=lambda schema: schema[Role.AGENT].diagnose())
        Action.create(game, name='wait',
                      callback=lambda schema: Success("Time passes..."))
        Action.create(game, name='inventory',
                      aliases=['i'],
                      callback=lambda schema: schema[Role.AGENT].list_inventory())
        Action.create(game, name='look',
                      aliases=['l'],
                      direct_object_role=Role.THEME,
                      preposition_roles={'at': Role.THEME, 'in': Role.THEME, 'on': Role.THEME},
                      callback=lambda schema: schema[Role.AGENT].look(schema[Role.THEME]))

        def process_get(schema):
            if schema[Role.PATIENT]:
                r = schema[Role.AGENT].get_from(schema[Role.THEME], schema[Role.PATIENT])
            else:
                theme = schema[Role.THEME]
                if isinstance(theme, Creature) and not theme.traits.portable:
                    r = Failure("You are unable to subdue and capture the {}!"
                                .format(theme.full_name()))
                elif not theme.traits.portable:
                    r = Failure("The {} is solidly anchored and cannot be removed"
                                .format(theme.full_name()))
                else:
                    r = schema[Role.AGENT].get(schema[Role.THEME])
            return r

        Action.create(game, name='get',
                      aliases=['take'],
                      required_roles={Role.AGENT},
                      direct_object_role=Role.THEME,
                      preposition_roles={'from': Role.PATIENT},
                      role_scopes={Role.THEME: Scope.EXTERNAL, Role.PATIENT: Scope.EXTERNAL},
                      role_messages={Role.THEME: "Admire the {} all you want, you can't take it with you."},
                      callback=process_get)

        Action.create(game, name='drop',
                      aliases=['leave'],
                      direct_object_role=Role.THEME,
                      required_roles={Role.AGENT, Role.THEME},
                      role_scopes={Role.THEME: Scope.INVENTORY},
                      callback=lambda schema: schema[Role.AGENT].drop(schema[Role.THEME]))

        Action.create(game, name='go',
                      aliases=['walk'],
                      required_roles={Role.AGENT, Role.GOAL},
                      direct_object_role=Role.GOAL,
                      role_messages={Role.GOAL: "That's not a direction!"},
                      callback=lambda schema: schema[Role.AGENT].go(schema[Role.GOAL]))

        Action.create(game, name='open',
                      required_roles={Role.AGENT, Role.PATIENT},
                      direct_object_role=Role.PATIENT,
                      callback=lambda schema: schema[Role.AGENT].open(schema[Role.PATIENT]))

        Action.create(game, name='close',
                      required_roles={Role.AGENT, Role.PATIENT},
                      direct_object_role=Role.PATIENT,
                      callback=lambda schema: schema[Role.AGENT].close(schema[Role.PATIENT]))

        Action.create(game, name='lock',
                      required_roles={Role.AGENT, Role.PATIENT, Role.INSTRUMENT},
                      direct_object_role=Role.PATIENT,
                      preposition_roles={'with': Role.INSTRUMENT},
                      callback=lambda schema: schema[Role.AGENT].lock_with(schema[Role.PATIENT],
                                                                           schema[Role.INSTRUMENT]))

        Action.create(game, name='unlock',
                      required_roles={Role.AGENT, Role.PATIENT, Role.INSTRUMENT},
                      direct_object_role=Role.PATIENT,
                      preposition_roles={'with': Role.INSTRUMENT},
                      callback=lambda schema: schema[Role.AGENT].unlock_with(schema[Role.PATIENT],
                                                                             schema[Role.INSTRUMENT]))
        Action.create(game, name='put',
                      required_roles={Role.AGENT, Role.PATIENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      preposition_roles={'in': Role.PATIENT, 'into': Role.PATIENT, 'on': Role.PATIENT},
                      callback=lambda schema: schema[Role.AGENT].put_in(schema[Role.THEME], schema[Role.PATIENT]))

        Action.create(game, name='eat',
                      required_roles={Role.AGENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      role_messages={Role.THEME: "I don't think the {} would agree with you."},
                      callback=lambda schema: schema[Role.AGENT].eat(schema[Role.THEME]))

        Action.create(game, name='drink',
                      required_roles={Role.AGENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      role_messages={Role.THEME: "I don't think the {} would agree with you."},
                      callback=lambda schema: schema[Role.AGENT].drink(schema[Role.THEME]))

        Action.create(game, name='greet',
                      required_roles={Role.AGENT, Role.PATIENT},
                      direct_object_role=Role.PATIENT,
                      callback=lambda schema: schema[Role.AGENT].greet(schema[Role.PATIENT]))

        Action.create(game, name='smile',
                      required_roles={Role.AGENT, Role.PATIENT},
                      preposition_roles={'at': Role.PATIENT},
                      callback=lambda schema: schema[Role.AGENT].greet(schema[Role.PATIENT]))

        Action.create(game, name='wave',
                      required_roles={Role.AGENT, Role.PATIENT},
                      preposition_roles={'at': Role.PATIENT, 'to': Role.PATIENT},
                      callback=lambda schema: schema[Role.AGENT].greet(schema[Role.PATIENT]))

        Action.create(game, name='give',
                      aliases=['offer'],
                      required_roles={Role.AGENT, Role.PATIENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      indirect_object_role=Role.PATIENT,
                      preposition_roles={'to': Role.PATIENT},
                      callback=lambda schema: schema[Role.AGENT].give_to(schema[Role.THEME], schema[Role.PATIENT]))

        Action.create(game, name='ask',
                      required_roles={Role.AGENT, Role.PATIENT, Role.THEME},
                      direct_object_role=Role.PATIENT,
                      preposition_roles={'for': Role.THEME},
                      callback=lambda schema: schema[Role.AGENT].ask_for(schema[Role.PATIENT], schema[Role.THEME]))

        Action.create(game, name='kill',
                      aliases=['attack', 'fight', 'hit'],
                      required_roles={Role.AGENT, Role.PATIENT, Role.INSTRUMENT},
                      direct_object_role=Role.PATIENT,
                      preposition_roles={'with': Role.INSTRUMENT},
                      role_messages={Role.INSTRUMENT: "The {} proves an ineffective choice of weapon"},
                      callback=lambda schema: schema[Role.AGENT].hit_with(schema[Role.PATIENT], schema[Role.INSTRUMENT]))

        def process_throw(schema):
            if schema[Role.GOAL]:
                r = schema[Role.AGENT].throw(schema[Role.THEME], schema[Role.GOAL])
            else:
                r = schema[Role.AGENT].throw(schema[Role.THEME])
            return r

        Action.create(game, name='throw',
                      aliases=['toss', 'pitch', 'fling', 'lob'],
                      required_roles={Role.AGENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      role_scopes={Role.THEME: Scope.INVENTORY, Role.PATIENT: Scope.EXTERNAL},
                      preposition_roles={'at': Role.GOAL, 'to': Role.GOAL},
                      role_messages={Role.THEME: "The {} is too unwieldy to make an effective missile",
                                     Role.GOAL: "The {} is not intended for target practice!"},
                      callback=lambda schema: process_throw(schema))

        Action.create(game, name='smell',
                      required_roles={Role.AGENT, Role.THEME},
                      direct_object_role=Role.THEME,
                      permissive_roles={Role.THEME},
                      callback=lambda schema: Success("Smells like {} {} to me!".
                                                      format(schema[Role.THEME].article(),
                                                             schema[Role.THEME].full_name())))

        Action.create(game, name='listen',
                      required_roles={Role.AGENT, Role.THEME},
                      permissive_roles={Role.THEME},
                      preposition_roles={'to': Role.THEME},
                      callback=lambda schema: Success("The {} is keeping pretty quiet right now"
                                                      .format(schema[Role.THEME].full_name())))

        Action.create(game, name='admire',
                      aliases=['appreciate'],
                      direct_object_role=Role.THEME,
                      required_roles={Role.AGENT, Role.THEME},
                      permissive_roles={Role.THEME},
                      callback=lambda schema: Success("Breathtaking! You feel enriched by this profound "
                                                      "artistic experience."))

        jump_result = Success("You take a great leap into the air")
        jump_result.add_message("Wheeeeeee!")
        jump_result.add_message("Boing boing boing ...")
        jump_result.add_message("Up, up and away!")

        def process_jump(schema):
            return jump_result

        Action.create(game, name='jump',
                      required_roles={Role.AGENT},
                      callback=process_jump)

    def setup_items(self, game):

        # --------------- Common effects of commands

        def update_score(game, points):
            game.score += points

        def update_health(player, points):
            player.health += points

        def make_creature_hostile(creature):
            creature.become_hostile()

        def instant_death(player):
            player.health = 0

        def lose_item(player, item):
            player.inventory.remove_item(item)

        def end_section(name, game, player, points):
            update_score(game, points)
            result = Result("Congratulations! You have finished {}. ".format(name))
            status = game.status()
            result.append(status.get_message())
            return result

        # ---------------- Create basic locations and objects

        player = game.player

        crumbly_room = Location(game, name='Crumbly Room',
                                description='A small storage room with crumbling plaster walls')
        paneled_room = Location(game, name='Wood Paneled Room',
                                description='A large, warm room with wood-paneled walls')
        north_tower = Location(game, name='North Tower',
                               description='A tower with a high ceiling and red-stained windows')
        balcony = Location(game, name='Balcony',
                           description='A breezy, open balcony with a beautiful view of the landscape below',
                           traits=Traits(precarious=True))
        east_tower = Location(game, name='East Tower',
                              description='The tall tower at the eastern side of the house')
        roof = Location(game, name='Roof',
                        description='You are on the roof of the eastern tower.  '
                                    + 'There is a ladder leading back downwards, and to the west is an open window.',
                        traits=Traits(precarious=True))

        west_tower = Location(game, name='West Tower', description='The tall tower at the western side of the house.')

        master_bedroom = Location(game, 'Master Bedroom',
                                  description='This appears to be a former bedroom, but the bed itself is missing.  '
                                  + 'A window to the east is open.')
        basement = Location(game, 'Basement',
                            description='An empty room, very drafty')
        garden = Location(game, 'garden',
                          description='a lush blooming garden')
        patio = Location(game, 'patio',
                         description='an empty stone patio')
        front_porch = Location(game, 'porch',
                               description='The front porch of the house.  A metal gate prevents you from leaving')
        front_porch.add_modifier('front')

        metal_gate = Surface(game, name='gate',
                             description='An impassable metal gate with two locks: one golden and one bronze, '
                                         + 'blocking your exit!')
        metal_gate.traits.closed = True
        metal_gate.add_modifier('metal')
        front_porch.add_item(metal_gate)

        golden_lock = Door(game, name='lock',
                           description='a golden lock')
        golden_lock.add_modifier('golden')
        metal_gate.add_item(golden_lock, force=True)

        bronze_lock = Door(game, name='lock',
                           description='a bronze lock')
        bronze_lock.add_modifier('bronze')
        metal_gate.add_item(bronze_lock, force=True)

        street = Location(game, 'street',
                          description='an empty street')

        fancy_painting = Item(game, name='painting', description='An ornate painting of the house\'s previous owner',
                              aliases=['portrait', 'picture'], size=15, value=100)
        fancy_painting.add_modifier('fancy')
        west_tower.add_item(fancy_painting)

        east_tower.add_exit(direction.west, paneled_room)
        crumbly_room.add_exit(direction.north, paneled_room)
        paneled_room.add_exit(direction.south, crumbly_room)
        paneled_room.add_exit(direction.north, north_tower)
        paneled_room.add_exit(direction.east, east_tower)
        paneled_room.add_exit(direction.west, west_tower)
        west_tower.add_exit(direction.east, paneled_room)
        roof.add_exit(direction.west, master_bedroom)
        master_bedroom.add_exit(direction.down, basement)
        master_bedroom.add_exit(direction.east, roof)
        basement.add_exit(direction.up, master_bedroom)
        basement.add_exit(direction.west,garden)
        garden.add_exit(direction.east,basement)
        garden.add_exit(direction.south,patio)
        patio.add_exit(direction.north,garden)
        patio.add_exit(direction.south,front_porch)

        front_porch.add_exit(direction.north, patio)
        front_porch.add_exit(direction.south, street,
                             condition=lambda g, p: not metal_gate.traits.closed,
                             after=lambda g, p, l, d: end_section("section one", g, p, 50),
                             fail_result=Failure("The metal gate blocks your way"))

        def too_small_check(g, p):
            return p.inventory.used_capacity() <= 25
        too_small_result = Failure("Your load is too large to fit through the small hole")

        east_tower.add_exit(direction.up, roof,
                            description='A ladder leads up to a hole in the ceiling far above',
                            condition=too_small_check,
                            fail_result=too_small_result)
        roof.add_exit(direction.down, east_tower,
                      description="There is a hole here leading down to the tower below",
                      condition=too_small_check,
                      fail_result=too_small_result)

        sturdy_door = Door(game, name='door', description='A sturdy door leading out to the balcony above the tower')
        sturdy_door.add_modifier('sturdy')

        silver_key = Key(game, name='key', description='A brilliant silver key')
        silver_key.add_modifier('silver')

        steel_key = Key(game, name='key', description='A small steel key')
        steel_key.add_modifier('steel')
        steel_key.set_lockable(sturdy_door)
        roof.add_item(steel_key)

        north_tower.add_item(sturdy_door)
        north_tower.add_exit(direction.south, paneled_room)
        north_tower.add_exit(direction.up, balcony,
                             description="Stairs lead up to a door high above",
                             condition=lambda g, p: not sturdy_door.traits.closed,
                             fail_result=Failure("A sturdy door blocks the way"))
        balcony.add_exit(direction.down, north_tower)

        light_thing = Item(game, name='thing', description='An easily carried thing, light as a feather', size=0)
        light_thing.add_modifier('light')

        fragile_thing = Item(game, name='thing', description='An easily breakable, delicate thing',
                             traits=Traits(fragile=True), size=15)
        fragile_thing.add_modifier('fragile')

        heavy_thing = Item(game, name='thing', description='A heavy block of some unknown material', size=45)
        heavy_thing.add_modifier('heavy')

        trunk = Container(game, name='trunk', description='An old wooden trunk',
                          aliases=['chest', 'box'],
                          size=75, value=5, capacity=90)
        trunk.add_modifier('wooden')
        sword = Weapon(game, name='sword', description='A serviceable iron sword',
                       size=15, value=15, damage=50, defense=10, accuracy=80)
        sword.add_modifier('iron')
        trunk.add_item(sword, force=True)

        diamond = Item(game, name='diamond',
                       aliases=['gem', 'jewel'],
                       size=5, value=100,
                       description='A brilliant diamond')

        apple = Edible(game, name='apple', description='A delicious, juicy red apple',
                       size=15, value=5)
        small_table = Surface(game, name='table', description='A small table', size=20, capacity=15)
        small_table.add_modifier('small')
        small_table.add_item(apple, force=True)

        large_table = Surface(game, name='table', description='A large table', size=75, capacity=100)
        large_table.add_modifier('large')
        large_table.add_item(heavy_thing, force=True)
        large_table.add_item(light_thing, force=True)
        large_table.add_item(fragile_thing, force=True)

        bread = Edible(game, name='bread', description='A loaf of crusty brown bread',
                       size=20, value=5, healing=10)

        puddle = Drinkable(game, name='puddle',
                           aliases=['water'],
                           description='A puddle of refreshing water',
                           size=25, value=5, healing=15)

        mouse = Item(game, name='mouse', description='A small mouse scampers back and forth across the '
                                                     + 'room here, searching for food.  It is carrying something '
                                                       'shiny in its mouth.',
                     traits=Traits(compelling=True), size=0, value=0)
        mouse.add_modifier('brown')
        west_tower.add_item(mouse)

        core = Item(game, name='core', description='The core of an eaten apple', size=5, value=0)
        core.add_modifier('apple')
        apple.add_consumed(core)

        crumbs = Edible(game, name='crumbs', description='A small pile of leftover bread crumbs',
                        aliases=['pile'], traits=Traits(composite=True, plural=True), size=5, value=0, healing=0)
        bread.add_consumed(crumbs)

        mud = Item(game,name='mud', description='A clump of soggy wet mud',
                   traits=Traits(composite=True), size=15, value=1)
        puddle.add_consumed(mud)
        vase = Container(game, name='flowerpot', description='a patterned flowerpot',
                         aliases=['flowerpot', 'pot', 'vase'], traits=Traits(closed=False, fragile=True),
                         size=5, value=10, capacity=3)
        flower = Item(game, name='flower', description='a beautiful, fragrant sunflower', size=3, value=5)
        crumbly_room.add_item(small_table)
        crumbly_room.add_item(large_table)
        paneled_room.add_item(trunk)
        paneled_room.add_item(puddle)

        vase.add_item(flower)
        balcony.add_item(vase)

        villager = Creature(game, name='villager', traits=Traits(mobile=True), aliases=['farmer'],
                            description="A stout but simple villager in farming garb",
                            health=75, strength=25, dexterity=65, location=paneled_room)
        villager.add_wanted_item(apple)
        villager.add_item(diamond)

        golden_key = Key(game, name='key', description='A fashionable golden key')
        golden_key.add_modifier('golden')
        golden_key.set_lockable(golden_lock)

        red_fox = Creature(game, name='fox', traits=Traits(hostile=True, mobile=False),
                           description="a bloodthirsty red fox",
                           health=65, strength=15, dexterity=50, location=front_porch)
        red_fox.add_modifier('red')
        red_fox.add_item(golden_key)

        bronze_key = Key(game, name='key', description='A dull bronze key')
        bronze_key.add_modifier('bronze')
        bronze_key.set_lockable(bronze_lock)

        brown_fox = Creature(game, name='fox', traits=Traits(hostile=True, mobile=False),
                             description="a vicious brown fox",
                             health=65, strength=25, dexterity=50, location=front_porch)
        brown_fox.add_modifier('brown')
        red_fox.add_item(bronze_key)

        townsfolk = Creature(game, name='townsfolk', traits=Traits(mobile=True),
                             description='A short, well-dressed man with a stubbly beard',
                             aliases=['folk', 'man'],
                             health=75, strength=30, dexterity=65, location=north_tower)
        townsfolk.add_wanted_item(diamond)
        townsfolk.add_item(bread)

        def shadow_action(game, player):
            player.health -= 5
            return Result("A dark shadow looms ominously in the corner")

        shadow = Creature(game, name='shadow', traits=Traits(hostile=False, mobile=True, evident=False),
                          description='You attempt to examine the shadow, but your vision blurs as you try to focus '
                                      'on its constantly shifting shape, preventing you from forming '
                                      'any clear impression',
                          health=9001, strength=20, dexterity=90, location=east_tower)
        shadow.add_modifier('dark')
        shadow.entry_action = lambda g, p: Result("A dark shadow enters.  The temperature in the room drops "
                                                  "several degrees, as does your blood")
        shadow.exit_action = lambda g, p: Result("The shadow leaves the room, and you once again find "
                                                 "you can breathe freely")
        shadow.present_action = shadow_action

        # -------- Consequences: game milestones and achievements, and special results
        vocabulary = game.vocabulary

        open = vocabulary.lookup_verb_by_name('open')
        get = vocabulary.lookup_verb_by_name('get')
        ask = vocabulary.lookup_verb_by_name('ask')
        smell = vocabulary.lookup_verb_by_name('smell')
        jump = vocabulary.lookup_verb_by_name('jump')
        drop = vocabulary.lookup_verb_by_name('drop')
        throw = vocabulary.lookup_verb_by_name('throw')
        kill = vocabulary.lookup_verb_by_name('kill')
        unlock = vocabulary.lookup_verb_by_name('unlock')

        # Trying to pick up creatures turns them hostile
        for creature in vocabulary.get_objects_of_class(Creature):
            get.add_consequence(
                schema=Schema(roles={Role.AGENT: player, Role.THEME: creature}),
                necessary_result=result.GENERIC_FAILURE,
                effect=lambda schema: make_creature_hostile(schema[Role.THEME]))

        # Be careful in precarious places!
        for room in vocabulary.get_objects_of_class(Location):
            if room.traits.precarious:
                jump.add_consequence(
                    schema=Schema(roles={Role.AGENT: player}),
                    necessary_result=result.GENERIC_SUCCESS,
                    necessary_location=room,
                    effect=lambda schema: instant_death(player),
                    consequent_result=Success("In your excitement, you slip and fall to the hard ground far below!\n"
                                              + "You should probably be more careful where you do your jumping."))

                # TODO: Some kind of pattern-matching logic here.  This configures for _no_ theme, not _any_ theme ...
                throw.add_consequence(
                    schema=Schema(roles={Role.AGENT: player}),
                    necessary_result=result.GENERIC_FAILURE,
                    necessary_location=room,
                    effect=lambda schema: lose_item(player, schema[Role.THEME]),
                    consequent_result=Failure("You toss it carelessly, and it sails over the edge and out of sight"))

        # The mouse is too fast to catch or kill, but it's hungry
        def fed_mouse(crumbs):
            west_tower.remove_item(mouse)
            west_tower.remove_item(crumbs)
            west_tower.add_item(silver_key)

        get.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: mouse}),
            necessary_result=result.GENERIC_SUCCESS,
            necessary_location=west_tower,
            effect=lambda schema: player.drop(mouse),
            consequent_result=Failure("You try, but the mouse is far too small and fast for you to catch!"))

        drop.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: crumbs}),
            necessary_result=result.GENERIC_SUCCESS,
            necessary_location=west_tower,
            effect=lambda schema: update_score(game, 20))

        drop.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: crumbs}),
            necessary_result=result.GENERIC_SUCCESS,
            necessary_location=west_tower,
            effect=lambda schema: fed_mouse(crumbs),
            consequent_result=Success("The mouse devours the crumbs, dropping something shiny to the floor in the "
                                      "process.  It then returns to its hole, well-fed and content"))

        # Foxes work cooperatively!
        def killed_fox(dead_fox, other_fox, key):
            dead_fox.remove_item(key)
            if other_fox.is_alive:
                other_fox.add_item(key)
                return result.GENERIC_SUCCESS
            else:
                return result.GENERIC_FAILURE

        kill.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: red_fox}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=killed_fox(red_fox, brown_fox, golden_key),
            consequent_result=Success("As the red fox falls dead to the ground, its brother retrieves "
                                      "the golden key from its lifeless form"))

        kill.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: brown_fox}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=killed_fox(brown_fox, red_fox, bronze_key),
            consequent_result=Success("As the brown fox falls dead to the ground, its brother retrieves "
                                      "the bronze key from its lifeless form"))

        # Achievement: unlock and open the sturdy door
        open.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.PATIENT: sturdy_door}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: update_score(game, 10))

        # Achievement: get the diamond from the villager
        ask.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.PATIENT: villager, Role.THEME: diamond}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: update_score(game, 20))

        get.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: diamond}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: update_score(game, 20))

        get.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.PATIENT: villager, Role.THEME: diamond}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: update_score(game, 20))

        # Health bonus: smell the sunflower
        smell.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: flower}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: update_health(player, 10),
            consequent_result=Success("You feel revived by the bloom's invigorating fragrance"))

        def unlock_gate(this_lock, other_lock):
            this_lock.traits.locked = False
            if other_lock.traits.locked:
                return result.GENERIC_FAILURE
            else:
                update_score(game, 50)
                metal_gate.traits.closed = False
                return result.GENERIC_SUCCESS

        unlock.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: golden_lock, Role.INSTRUMENT: golden_key}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: unlock_gate(golden_lock, bronze_lock),
            consequent_result=WON_GAME)

        unlock.add_consequence(
            schema=Schema(roles={Role.AGENT: player, Role.THEME: golden_lock, Role.INSTRUMENT: golden_key}),
            necessary_result=result.GENERIC_SUCCESS,
            effect=lambda schema: unlock_gate(golden_lock, bronze_lock),
            consequent_result=WON_GAME)

        # Start game in crumbly room
        return crumbly_room

    def setup_player(self, game, start_location):
        game.player = Player(game, location=start_location)

    def setup(self, game):

        self.setup_actions(game)
        self.setup_directions(game)
        game.player = Player(game)
        start_location = self.setup_items(game)
        game.player.location = start_location


