from schema import Scope, Role, Schema
from result import *


class ProximityException(Exception):

    def __init__(self, item_name):
        self.item_name = item_name


class OwnershipException(Exception):

    def __init__(self, item_name, article='the'):
        self.article = article
        self.item_name = item_name


class AmbiguousNounException(Exception):

    def __init__(self, matches):
        self.matches = matches


class PrepPhrase:

    def __init__(self, noun_phrase, preposition):
        self.noun_phrase = noun_phrase
        self.preposition = preposition


class NounPhrase:

    def __init__(self, noun, modifiers):
        self.noun = noun
        self.modifiers = modifiers

    def text(self):
        if len(self.modifiers) > 0:
            full_name = ' '.join(list(self.modifiers)) + ' ' + self.noun
        else:
            full_name = self.noun
        return full_name


class Command:

    def __init__(self, game):

        self.game = game
        self.vocabulary = game.vocabulary
        self.input_text = None
        self.action = None
        self.schema = Schema()

        self.verb = None
        self.direct_object = None
        self.indirect_object = None
        self.prep_phrases = []

    def set_role_from_noun_in_context(self, action, schema, phrase, role):
        scope = action.role_scopes[role]
        thing = self.lookup_noun_in_context(phrase, scope)
        schema.set_role(role, thing)

    def lookup_noun_in_context(self, phrase, scope):

        unambiguous_match = None
        player = self.game.player
        noun = phrase.noun
        matches = self.vocabulary.lookup_noun_by_name(noun)
        if len(matches) == 1:
            unambiguous_match = matches[0]

        if not unambiguous_match:
            modifiers = phrase.modifiers
            if len(modifiers) > 0:
                matches_by_modifier = \
                    [m for m in matches if set(modifiers) <=
                     set([self.vocabulary.lookup_adjective(a).name for a in m.modifiers])]
                if len(matches_by_modifier) == 1:
                    unambiguous_match = matches_by_modifier[0]
                elif len(matches_by_modifier) > 1:
                    matches = matches_by_modifier

        matches_in_inventory = [m for m in matches if player.in_inventory(m)]
        matches_in_location = [m for m in matches if player.in_current_location(m)]
        proximate_matches = matches_in_inventory + matches_in_location
        container_matches = [m for m in matches if player.nearby_container_having(m)]
        creature_matches = [m for m in matches if player.nearby_creature_having(m)]
        nearby_matches = proximate_matches + container_matches + creature_matches
        if scope == Scope.INVENTORY:
            available_matches = matches_in_inventory
        elif scope == Scope.PROXIMITY:
            available_matches = proximate_matches
        elif scope == Scope.EXTERNAL:
            available_matches = matches_in_location + container_matches + creature_matches
        else:  # Scope.NEARBY
            available_matches = nearby_matches

        if unambiguous_match and unambiguous_match in available_matches:
            return unambiguous_match
        elif unambiguous_match and not unambiguous_match.traits.ubiquitous \
                and unambiguous_match not in available_matches:
            if unambiguous_match in nearby_matches:
                article = 'the'
            elif unambiguous_match.traits.composite:
                article = 'any'
            else:
                article = unambiguous_match.article()
            if scope == Scope.INVENTORY:
                raise OwnershipException(phrase.text(), article)
            else:
                raise ProximityException(phrase.text())
        elif not unambiguous_match and len(available_matches) == 0:
            if scope == Scope.INVENTORY:
                raise OwnershipException(phrase.text(), article='a')
            else:
                raise ProximityException(phrase.text())
        elif not unambiguous_match:
            if len(available_matches) == 1:
                unambiguous_match = available_matches[0]
            elif len(available_matches) > 1:
                raise AmbiguousNounException(available_matches)

        return unambiguous_match

    def assign_roles(self):

        self.schema.set_agent(self.game.player)

        try:
            for prep_phrase in self.prep_phrases:
                try:
                    prep_role = self.action.get_role_for_preposition(prep_phrase.preposition)
                except (KeyError, AttributeError):
                    return NotUnderstoodFailure()
                self.set_role_from_noun_in_context(self.action, self.schema, prep_phrase.noun_phrase, prep_role)

            direct_object_role = self.action.get_direct_object_role()
            indirect_object_role = self.action.get_indirect_object_role()

            if self.indirect_object:
                if indirect_object_role:
                    self.set_role_from_noun_in_context(self.action, self.schema,
                                                       self.indirect_object, indirect_object_role)
            if self.direct_object:
                if direct_object_role:
                    self.set_role_from_noun_in_context(self.action, self.schema,
                                                       self.direct_object, direct_object_role)

        except AmbiguousNounException as ane:
            return AmbiguousNounFailure(ane.matches)
        except ProximityException as pe:
            return ProximityFailure(pe.item_name)
        except OwnershipException as oe:
            return OwnershipFailure(oe.item_name, oe.article)

        return Success("Roles assigned successfully")

    def parse_input(self, input_text):

        vocabulary = self.vocabulary
        words = input_text.split()
        self.input_text = input_text

        self.verb = words[0]
        try:
            self.action = vocabulary.lookup_verb_by_name(self.verb)
        except (KeyError, IndexError):
            return Failure("I don't know how to {}!".format(self.verb))

        preposition = None
        determiner = None
        modifiers = set()
        for word in words[1:]:
            if vocabulary.is_determiner(word):
                if determiner:
                    return NotUnderstoodFailure()
                else:
                    determiner = word
                    continue
            if vocabulary.is_preposition(word):
                if preposition:
                    return NotUnderstoodFailure()
                else:
                    preposition = word
                    continue
            if vocabulary.is_noun(word):
                determiner = None
                if preposition:
                    prep_phrase = PrepPhrase(NounPhrase(word, modifiers), preposition)
                    self.prep_phrases.append(prep_phrase)
                    preposition = None
                elif self.direct_object:
                    # Two nouns in a row: is first noun an indirect object?
                    if self.action.get_indirect_object_role():
                        self.indirect_object = self.direct_object
                        self.direct_object = NounPhrase(word, modifiers)
                    # ... if this verb doesn't accept indirect objects, the first 'noun'
                    # might be acting as an adjective-like specifier (e.g., "apple core")
                    else:
                        previous_noun = self.direct_object.noun
                        if vocabulary.is_adjective(previous_noun):
                            modifiers = self.direct_object.modifiers
                            modifiers.add(previous_noun)
                            self.direct_object = NounPhrase(word, modifiers)
                else:
                    self.direct_object = NounPhrase(word, modifiers)
                modifiers = set()
                continue
            if vocabulary.is_adjective(word):
                modifiers.add(word)
                continue

            return NotUnderstoodFailure(word)
        return Success("Syntax check: passed")

    def execute(self):
        return self.action.attempt_action(self.schema)

