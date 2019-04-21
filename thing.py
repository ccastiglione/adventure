from traits import Traits
from modifier import Modifier
from schema import Role
from result import Success


class Thing:

    DEFAULT_TRAITS = None

    def __init__(self, game, name, aliases=None, traits=None):

        self.game = game
        self.vocabulary = game.vocabulary
        self.id = self.vocabulary.register_noun(self)
        self.name = name
        if aliases:
            self.aliases = aliases
        else:
            self.aliases = []
        self.traits = Traits.merge(self, traits, Thing.DEFAULT_TRAITS)
        self.modifiers = set()
        self.valid_roles = {
            Role.AGENT: [],
            Role.PATIENT: [],
            Role.THEME: [],
            Role.GOAL: [],
            Role.INSTRUMENT: []
        }

    def full_name(self):
        if len(self.modifiers) > 0:
            full_name = ' '.join([self.vocabulary.lookup_adjective(m).name for m in list(self.modifiers)]) \
                        + ' ' + self.name
        else:
            full_name = self.name
        return full_name

    def add_modifier(self, adjective):
        modifier_id = self.vocabulary.register_adjective(Modifier(self.game, name=adjective))
        self.modifiers.add(modifier_id)

    def article(self):
        if self.traits.composite:
            article = 'some'
        else:
            first_word = self.name
            if len(self.modifiers) > 0:
                first_word = list(self.modifiers)[0]
            if first_word[0] in ['a', 'e', 'i', 'o', 'u']:
                article = 'an'
            else:
                article = 'a'
        return article

    def existential(self):
        if self.traits.plural:
            existential = 'are'
        else:
            existential = 'is'
        return existential

    def to_json(self):
        return vars(self)

    def add_alias(self, alias):
        self.aliases.append(alias)

    def add_role(self, role, verb):
        self.valid_roles[role].append(self.vocabulary.lookup_verb_by_name(verb))

    def remove_role(self, role, verb):
        self.valid_roles[role].remove(self.vocabulary.lookup_verb_by_name(verb))

    def is_valid_for_role(self, role, attempted_action):
        valid_roles = self.valid_roles[role]
        is_valid = attempted_action in valid_roles
        return is_valid

    def add_agent_role(self, verb):
        self.add_role(Role.AGENT, verb)

    def is_valid_agent(self, attempted_action):
        return self.is_valid_for_role(Role.AGENT, attempted_action)

    def add_patient_role(self, verb):
        self.add_role(Role.PATIENT, verb)

    def is_valid_patient(self, attempted_action):
        return self.is_valid_for_role(Role.PATIENT, attempted_action)

    def add_theme_role(self, verb):
        self.add_role(Role.THEME, verb)

    def is_valid_theme(self, attempted_action):
        return self.is_valid_for_role(Role.THEME, attempted_action)

    def add_goal_role(self, verb):
        self.add_role(Role.GOAL, verb)

    def is_valid_goal(self, attempted_action):
        return self.is_valid_for_role(Role.GOAL, attempted_action)

    def add_instrument_role(self, verb):
        self.add_role(Role.INSTRUMENT, verb)

    def is_valid_instrument(self, attempted_action):
        return self.is_valid_for_role(Role.INSTRUMENT, attempted_action)


class VisibleThing(Thing):

    DEFAULT_TRAITS = Traits(visible=True)

    def __init__(self, game, name, description, aliases=None, traits=None):
        self.traits = Traits.merge(self, traits, VisibleThing.DEFAULT_TRAITS)
        super(VisibleThing, self).__init__(game, name, aliases)
        self.description = description
        self.add_patient_role('look')
        self.add_theme_role('throw')

    def describe(self):
        return Success(self.description)
