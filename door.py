from traits import Traits
from item import Item


class Door(Item):

    DEFAULT_TRAITS = Traits(portable=False, evident=False, closed=True, locked=True)

    def __init__(self, game, name, description, aliases=None, traits=None):
        self.traits = Traits.merge(self, traits, Door.DEFAULT_TRAITS)
        super(Door, self).__init__(game, name, description, aliases)
        self.add_patient_role('open')
        self.add_patient_role('close')
        self.add_patient_role('lock')
        self.add_patient_role('unlock')

