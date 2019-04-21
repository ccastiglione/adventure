from traits import Traits
from item import Item
from result import Success, Failure


class Container(Item):

    MAX_CAPACITY = 999
    DEFAULT_TRAITS = Traits(closed=True)

    def __init__(self, game, name, description,
                 aliases=None, traits=None, size=0, value=0, capacity=0):
        self.traits = Traits.merge(self, traits, Container.DEFAULT_TRAITS)
        super(Container, self).__init__(game, name, description, aliases, size=size, value=value)
        self.vocab = game.vocabulary
        self.put_preposition = 'in'
        self.capacity = capacity
        self.items = []
        self.add_patient_role('put')
        self.add_patient_role('get')
        if not self.traits.surface:
            self.add_patient_role('open')
            self.add_patient_role('close')
            self.add_patient_role('lock')
            self.add_patient_role('unlock')

    def item_count(self):
        return len(self.items)

    def used_capacity(self):
        used_capacity = 0
        for item_id in self.items:
            item = self.vocab.lookup_noun(item_id)
            used_capacity += item.size
        return used_capacity

    def remaining_capacity(self):
        return self.capacity - self.used_capacity()

    def add_item(self, item, force=False):
        if not force and self.traits.closed:
            result = Failure("The " + self.full_name() + " is closed")
        else:
            if item.id in self.items:
                result = Failure("The {} {} already {} the {}"
                                 .format(item.full_name(),
                                         item.existential(),
                                         self.put_preposition,
                                         self.full_name()))
            elif item.size > self.remaining_capacity():
                result = Failure("Sorry, the {} won't fit {} the {}"
                                 .format(item.full_name(), self.put_preposition, self.full_name()))
            else:
                self.items.append(item.id)
                result = Success("Okay, the {} {} now {} the {}"
                                 .format(item.full_name(),
                                         item.existential(),
                                         self.put_preposition, self.full_name()))
        return result

    def remove_item(self, item, force=False):
        if not force and self.traits.closed:
            result = Failure("The " + self.full_name() + " is closed")
        else:
            if item.id in self.items:
                self.items.remove(item.id)
                result = Success("You remove the " + item.name + " from the " + self.full_name())
            else:
                result = Failure("The {} {}n't {} the {}!"
                                 .format(item.full_name(),
                                         item.existential(),
                                         self.put_preposition,
                                         self.full_name()))
        return result

    def append_container_description(self, description):
        item_count = len(self.items)
        if item_count == 0:
            description.append(", containing nothing")
        elif len(self.items) == 1:
            item = self.vocab.lookup_noun(self.items[0])
            description.append(", containing {} {}"
                               .format(item.article(), item.name))
        else:
            description.append(", containing: ")
            for item_id in self.items:
                item = self.vocab.lookup_noun(item_id)
                description.append("\n\t" + item.article() + " " + item.full_name())

    def describe(self):
        r = super(Container, self).describe()
        if self.traits.closed:
            r.append(", which is currently closed")
        else:
            self.append_container_description(r)
        return r
