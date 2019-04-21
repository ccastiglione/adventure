from copy import copy
from collections.abc import Sequence


class Scope:

    INVENTORY = 0
    EXTERNAL = 1
    PROXIMITY = 2
    NEARBY = 3

    values = {INVENTORY, EXTERNAL, PROXIMITY, NEARBY}


class Role:

    AGENT = 0
    PATIENT = 1
    THEME = 2
    GOAL = 3
    INSTRUMENT = 4

    values = {AGENT, PATIENT, THEME, GOAL, INSTRUMENT}


class Schema(Sequence):

    EMPTY_SCHEMA = {Role.AGENT: None,
                    Role.PATIENT: None,
                    Role.THEME: None,
                    Role.INSTRUMENT: None}

    def __init__(self, roles=None):
        self.roles = copy(Schema.EMPTY_SCHEMA)
        if roles:
            for r in roles:
                self.roles[r] = roles[r]

    def __getitem__(self, i):
        try:
            value = self.roles[i]
        except KeyError:
            value = None
        return value

    def __len__(self):
        return len(self.roles)

    def set_role(self, role, value):
        self.roles[role] = value

    def get_role(self, role):
        try:
            value = self.roles[role]
        except KeyError:
            value = None
        return value

    def set_agent(self, agent):
        self.set_role(Role.AGENT, agent)

    def set_patient(self, patient):
        self.set_role(Role.PATIENT, patient)

    def set_topic(self, topic):
        self.set_role(Role.THEME, topic)

    def set_instrument(self, instrument):
        self.set_role(Role.INSTRUMENT, instrument)

