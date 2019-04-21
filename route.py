
class Route:

    def __init__(self, **kwargs):
        if kwargs['prompt']:
            self.prompt = kwargs['prompt']
        else:
            self.prompt = ""

    def set_banner(self, banner):
        pass

    def send_output(self, message):
        pass

    def receive_input(self):
        return ""


class ConsoleRoute(Route):

    def set_banner(self, banner):
        print("\n======== Welcome to " + banner + "! ========")

    def send_output(self, message):
        print(message)

    def receive_input(self):
        return input(self.prompt)
