DETERMINERS = {'the', 'a', 'an', 'some'}
PREPOSITIONS = {'on', 'at', 'to', 'with', 'in', 'into', 'from', 'for', 'of'}


class PartOfSpeech:

    NOUN = 0
    VERB = 1
    ADJECTIVE = 2

    values = {NOUN, VERB, ADJECTIVE}


class Vocabulary:

    def __init__(self):
        self.id_counter = 0
        self.catalogs = dict()
        self.reset()

    def reset(self):
        for pos in PartOfSpeech.values:
            self.catalogs[pos] = {}

    def next_id(self):
        self.id_counter += 1
        return "{:0>6d}".format(self.id_counter)

    def register(self, part_of_speech, entry):
        catalog_id = self.next_id()
        self.catalogs[part_of_speech][catalog_id] = entry
        return catalog_id

    def lookup_by_id(self, part_of_speech, catalog_id):
        return self.catalogs[part_of_speech][catalog_id]

    def lookup_by_name(self, part_of_speech, name):
        matches = []
        for entry in self.catalogs[part_of_speech].values():
            if name == entry.name or name in entry.aliases:
                matches.append(entry)
        return matches

    def is_valid_part_of_speech(self, part_of_speech, lookup_term):
        return len(self.lookup_by_name(part_of_speech, lookup_term)) > 0

    def get_objects(self):
        noun_catalog = self.catalogs[PartOfSpeech.NOUN]
        return [self.lookup_by_id(PartOfSpeech.NOUN, catalog_id) for catalog_id in noun_catalog.keys()]

    def get_objects_of_class(self, klass):
        return [x for x in self.get_objects() if isinstance(x, klass)]

    def get_valid_verbs(self):
        verb_catalog = self.catalogs[PartOfSpeech.VERB]
        return [verb_catalog[v].name for v in verb_catalog.keys()]

    def is_preposition(self, word):
        return word in PREPOSITIONS

    def is_determiner(self, word):
        return word in DETERMINERS

    def register_noun(self, thing):
        return self.register(PartOfSpeech.NOUN, thing)

    def is_noun(self, lookup_term):
        return self.is_valid_part_of_speech(PartOfSpeech.NOUN, lookup_term)

    def lookup_noun(self, lookup_term):
        return self.lookup_by_id(PartOfSpeech.NOUN, lookup_term)

    def lookup_noun_by_name(self, lookup_term):
        return self.lookup_by_name(PartOfSpeech.NOUN, lookup_term)

    def register_verb(self, action):
        return self.register(PartOfSpeech.VERB, action)

    def is_verb(self, lookup_term):
        return self.is_valid_part_of_speech(PartOfSpeech.VERB, lookup_term)

    def lookup_verb_by_name(self, lookup_term):
        return self.lookup_by_name(PartOfSpeech.VERB, lookup_term)[0]

    def register_adjective(self, modifier):
        return self.register(PartOfSpeech.ADJECTIVE, modifier)

    def is_adjective(self, lookup_term):
        return self.is_valid_part_of_speech(PartOfSpeech.ADJECTIVE, lookup_term)

    def lookup_adjective(self, lookup_term):
        return self.lookup_by_id(PartOfSpeech.ADJECTIVE, lookup_term)
