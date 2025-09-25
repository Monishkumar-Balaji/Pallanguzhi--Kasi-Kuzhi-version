from .pallanguzhi import Pallanguzhi
import arcade
from .constants import *

# ---------------- Welcome Screen ---------------- #
class WelcomeView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Welcome to Pallanguzhi", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
                         arcade.color.WHITE, 28, anchor_x="center")

        arcade.draw_text("Press M to Play Multiplayer", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20,
                         arcade.color.LIGHT_GREEN, 20, anchor_x="center")
        arcade.draw_text("Press A to Play with AI", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20,
                         arcade.color.LIGHT_YELLOW, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.M:
            game_view = Pallanguzhi(ai_mode=False)
            self.window.show_view(game_view)
        elif key == arcade.key.A:
            game_view = Pallanguzhi(ai_mode=True)
            self.window.show_view(game_view)

#----------------- Game over view ------------------#

class GameOverView(arcade.View):
    def __init__(self, winner, scores):
        super().__init__()
        self.winner = winner
        self.scores = scores

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Round Over!", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
                         arcade.color.WHITE, 30, anchor_x="center")
        arcade.draw_text(f"Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30,
                         arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text(f"Scores: P1 = {self.scores[0]} | P2 = {self.scores[1]}",
                         SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10,
                         arcade.color.LIGHT_GREEN, 20, anchor_x="center")
        arcade.draw_text("Press ENTER to return to Welcome screen",
                         SCREEN_WIDTH/2, 50, arcade.color.GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            from_main_menu = WelcomeView()
            self.window.show_view(from_main_menu)