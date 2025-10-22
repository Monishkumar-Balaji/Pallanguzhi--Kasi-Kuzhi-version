import arcade
from .constants import *

# ---------------- Welcome Screen ---------------- #
class WelcomeView(arcade.View):
    def __init__(self):
        super().__init__()
        self.rounds = 3  # Default number of rounds
        self.showing_round_input = False
        self.round_input = "3"

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Welcome to Pallanguzhi", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
                         arcade.color.WHITE, 28, anchor_x="center")

        if not self.showing_round_input:
            arcade.draw_text("Press M to Play Multiplayer", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40,
                             arcade.color.LIGHT_GREEN, 20, anchor_x="center")
            arcade.draw_text("Press A to Play with AI", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                             arcade.color.LIGHT_YELLOW, 20, anchor_x="center")
            arcade.draw_text(f"Rounds: {self.rounds} (Press R to change)", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40,
                             arcade.color.LIGHT_BLUE, 16, anchor_x="center")
        else:
            arcade.draw_text("Enter number of rounds (1-10):", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20,
                             arcade.color.WHITE, 20, anchor_x="center")
            arcade.draw_text(self.round_input, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20,
                             arcade.color.YELLOW, 24, anchor_x="center")
            arcade.draw_text("Press ENTER to confirm", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60,
                             arcade.color.GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if self.showing_round_input:
            if key == arcade.key.ENTER:
                try:
                    self.rounds = max(1, min(10, int(self.round_input)))
                    self.showing_round_input = False
                except ValueError:
                    self.round_input = "3"
            elif key == arcade.key.BACKSPACE:
                self.round_input = self.round_input[:-1]
            elif key in (arcade.key.KEY_0, arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, 
                        arcade.key.KEY_4, arcade.key.KEY_5, arcade.key.KEY_6, arcade.key.KEY_7, 
                        arcade.key.KEY_8, arcade.key.KEY_9):
                if len(self.round_input) < 2:  # Limit to 2 digits
                    self.round_input += chr(key)
        else:
            if key == arcade.key.M:
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=False, total_rounds=self.rounds)
                self.window.show_view(game_view)
            elif key == arcade.key.A:
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=True, total_rounds=self.rounds)
                self.window.show_view(game_view)
            elif key == arcade.key.R:
                self.showing_round_input = True
                self.round_input = str(self.rounds)

#----------------- Game over view ------------------#

class GameOverView(arcade.View):
    def __init__(self, winner, scores, total_rounds, current_round, final=False):
        super().__init__()
        self.winner = winner
        self.scores = scores
        self.total_rounds = total_rounds
        self.current_round = current_round
        self.final = final
        self.next_round_captures = None  # To pass captures to next round

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        if self.final:
            arcade.draw_text("GAME OVER!", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
                             arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text(f"Final Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30,
                             arcade.color.YELLOW, 24, anchor_x="center")
        else:
            arcade.draw_text(f"Round {self.current_round} Over!", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
                             arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text(f"Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30,
                             arcade.color.YELLOW, 24, anchor_x="center")
        
        arcade.draw_text(f"Scores: P1 = {self.scores[0]} | P2 = {self.scores[1]}",
                         SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10,
                         arcade.color.LIGHT_GREEN, 20, anchor_x="center")
        
        if self.final:
            arcade.draw_text(f"Played {self.current_round} of {self.total_rounds} rounds",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50,
                             arcade.color.LIGHT_BLUE, 16, anchor_x="center")
            arcade.draw_text("Press ENTER to return to Welcome screen",
                             SCREEN_WIDTH/2, 50, arcade.color.GRAY, 16, anchor_x="center")
        else:
            arcade.draw_text(f"Round {self.current_round} of {self.total_rounds}",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50,
                             arcade.color.LIGHT_BLUE, 16, anchor_x="center")
            arcade.draw_text("Press ENTER to continue to next round",
                             SCREEN_WIDTH/2, 50, arcade.color.GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            if self.final:
                welcome_view = WelcomeView()
                self.window.show_view(welcome_view)
            else:
                # Start next round with current captures
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=True, total_rounds=self.total_rounds, 
                                      current_round=self.current_round + 1,
                                      previous_captures=self.scores[:])
                self.window.show_view(game_view)