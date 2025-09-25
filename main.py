import arcade
from models.constants import *
from models.pit import Pit
#from models.gameOverView import GameOverView
from models.pallanguzhi import Pallanguzhi
from models.viewScreens import *


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    welcome = WelcomeView()
    window.show_view(welcome)
    arcade.run()

