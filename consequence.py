
class Consequence:

    def __init__(self, result, callback):
        self.result = result
        self.callback = callback

    def do_consequence(self, schema):
        self.callback(schema)
        return self.result

