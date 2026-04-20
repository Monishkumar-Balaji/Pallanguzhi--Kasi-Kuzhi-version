import arcade
from models.viewScreens import WelcomeView

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 520
SCREEN_TITLE = "Pallanguzhi"

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    welcome = WelcomeView()
    window.show_view(welcome)
    arcade.run()