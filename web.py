from flask import render_template
from flask import Flask
from route import Route
from game import Game


class WebRoute(Route):

    def __init__(self):
        super(Route, self).__init__()
        self.banner = None
        self.input = None
        self.output = None

    def set_banner(self, banner):
        self.banner = banner

    def send_output(self, output):
        self.output = output

    def receive_input(self):
        return self.input


app = Flask(__name__)


@app.route("/")
@app.route("/game")
def game_controller():
    route = WebRoute()
    game = Game(name='Adventure Quest', route=route)
    game.init_game()
    return render_template('game.html', banner=route.banner, hello='Hello')


if __name__ == "__main__":
    app.run()
