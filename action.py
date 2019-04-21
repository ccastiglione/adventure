from copy import copy
from schema import Role, Scope
from result import Success, Failure, NotUnderstoodFailure


class InvalidRoleConfiguration(Exception):
    def __init__(self, name, required_unassigned):
        self.name = name
        self.required_unassigned = required_unassigned


class Consequence:
    def __init__(self, effect, result):
        self.effect = effect
        self.result = result


class Action:

    DEFAULT_ROLE_SCOPES = {
        Role.PATIENT: Scope.NEARBY,
        Role.GOAL: Scope.NEARBY,
        Role.THEME: Scope.NEARBY,
        Role.INSTRUMENT: Scope.INVENTORY
    }

    # Default error messages when a thing was given to fill a role that doesn't make sense semantically
    DEFAULT_ROLE_MESSAGES = {
        Role.AGENT: "How disappointing! Behavior of that sort is hardly appropriate " \
                    + "for a noble adventurer such as yourself!",
        Role.PATIENT: "You can't do that to the {}",
        Role.THEME: "That is not the kind of thing you do with a {}",
        Role.GOAL: "You can't {} there",
        Role.INSTRUMENT: "The {} is not well-designed for that task"
    }

    def __init__(self, game, name, callback,
                 preposition_roles, direct_object_role, indirect_object_role,
                 required_roles, permissive_roles,
                 aliases=None, role_scopes=None, role_messages=None):

        self.game = game
        self.name = name
        self.callback = callback
        self.preposition_roles = preposition_roles
        self.required_roles = required_roles
        self.permissive_roles = permissive_roles
        self.unassigned_roles = copy(Role.values)

        self.unassigned_roles.remove(Role.AGENT)

        if direct_object_role:
            self.direct_object_role = direct_object_role
            self.unassigned_roles.remove(direct_object_role)
        else:
            self.direct_object_role = None

        if indirect_object_role:
            self.indirect_object_role = indirect_object_role
            self.unassigned_roles.remove(indirect_object_role)
        else:
            self.indirect_object_role = None

        if preposition_roles:
            for p in preposition_roles:
                if preposition_roles[p] in self.unassigned_roles:
                    self.unassigned_roles.remove(preposition_roles[p])

        required_unassigned = set(self.unassigned_roles).intersection(self.required_roles)
        if len(required_unassigned) > 0:
            raise InvalidRoleConfiguration(self.name, required_unassigned)

        if aliases is None:
            self.aliases = []
        else:
            self.aliases = aliases

        self.role_scopes = copy(Action.DEFAULT_ROLE_SCOPES)
        if role_scopes:
            for role in role_scopes.keys():
                self.role_scopes[role] = role_scopes[role]

        self.role_messages = copy(Action.DEFAULT_ROLE_MESSAGES)
        if role_messages is not None:
            for role in role_messages.keys():
                self.role_messages[role] = role_messages[role]

        self.consequences = dict()

    @classmethod
    def create(cls, game, name,
               callback=lambda schema: Success("Done"),
               preposition_roles=None,
               direct_object_role=None,
               indirect_object_role=None,
               required_roles=None,
               permissive_roles=None,
               aliases=None,
               role_scopes=None,
               role_messages=None):
        if not preposition_roles:
            preposition_roles = {}
        if not required_roles:
            required_roles = {Role.AGENT}
        if not permissive_roles:
            permissive_roles = {}
        a = Action(game, name, callback, preposition_roles, direct_object_role, indirect_object_role,
                   required_roles, permissive_roles,
                   aliases, role_scopes, role_messages)
        game.vocabulary.register_verb(a)
        return a

    def add_alias(self, alias):
        self.aliases.append(alias)

    def schema_lookup(self, schema, necessary_result, necessary_location):
        if necessary_result:
            is_success = necessary_result.success
        else:
            is_success = None
        if necessary_location:
            location_name = necessary_location.name
        else:
            location_name = None
        lookup_key = (schema[Role.AGENT], schema[Role.PATIENT], schema[Role.THEME],
                      schema[Role.GOAL], schema[Role.INSTRUMENT],
                      location_name, is_success)
        return lookup_key

    def add_consequence(self, schema, necessary_result=None, necessary_location=None,
                        effect=None, consequent_result=None):
        key = self.schema_lookup(schema, necessary_result, necessary_location)
        if key not in self.consequences:
            self.consequences[key] = []
        entry = Consequence(effect, consequent_result)
        self.consequences[key].append(entry)

    def handle_consequences(self, schema, action_result, player_location):
        result = None
        consequences = None
        key = self.schema_lookup(schema, action_result, player_location)
        try:
            consequences = self.consequences[key]
        except KeyError:
            try:
                key = self.schema_lookup(schema, action_result, None)
                consequences = self.consequences[key]
            except KeyError:
                pass
        if consequences:
            for c in consequences:
                if c.effect:
                    default_result = c.effect(schema)
                    if c.result:
                        result = c.result
                    else:
                        result = default_result
                else:
                    result = c.result
        return result

    def get_direct_object_role(self):
        return self.direct_object_role

    def get_indirect_object_role(self):
        return self.indirect_object_role

    def get_role_for_preposition(self, preposition):
        role = self.preposition_roles[preposition]
        return role

    def do_action(self, schema):
        player = schema[Role.AGENT]
        result = self.callback(schema)
        special_result = self.handle_consequences(schema, result, player.location)
        if special_result:
            result = special_result
        return result

    def is_valid_schema(self, schema):
        r = None
        missing_roles = set()
        for role in Role.values:
            if role in self.unassigned_roles and schema.get_role(role):
                r = NotUnderstoodFailure()
                break
            elif role in self.required_roles:
                if schema.get_role(role) is None:
                    missing_roles.add(role)
                else:
                    role_value = schema.get_role(role)
                    if not (role in self.permissive_roles or role_value.is_valid_for_role(role, self)):
                        r = Failure(self.role_messages[role].format(role_value.full_name()))
                        break
        if r is None:
            # TODO: Add heuristic to guess identity of missing words, if possible
            if len(missing_roles) > 0:
                preposition = None
                for k, v in self.preposition_roles.items():
                    if v in missing_roles:
                        preposition = k
                if Role.PATIENT in missing_roles:
                    if preposition:
                        r = Failure("What do you want to {} {}?".format(self.name, preposition))
                    else:
                        r = Failure("What do you want to {}?".format(self.name))
                elif Role.THEME in missing_roles or Role.INSTRUMENT in missing_roles:
                    if preposition:
                        r = Failure("What do you want to {} the {} {}?"
                                    .format(self.name, schema[Role.PATIENT].full_name(), preposition))
                    else:
                        r = Failure("What do you want to {} the {}?"
                                    .format(self.name, schema[Role.PATIENT].full_name()))
                else:
                    r = NotUnderstoodFailure()
            else:
                r = Success("Success")
        return r

    def attempt_action(self, schema):
        r = self.is_valid_schema(schema)
        if r.success:
            r = self.do_action(schema)
        return r
