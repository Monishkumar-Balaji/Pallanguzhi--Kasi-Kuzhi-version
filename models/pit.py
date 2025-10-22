from .constants import *
import math

class Pit:
    def __init__(self, row, col, x, y):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.counters = START_COUNTERS

    def draw(self, highlight_type=None, is_rubbish=False):
        # Determine pit color based on highlight type
        if is_rubbish:
            pit_color = arcade.color.GRAY
        elif highlight_type == "selected":
            pit_color = arcade.color.LIGHT_BLUE  # Blue for selected pit
        elif highlight_type == "sowing":
            pit_color = arcade.color.LIGHT_GREEN  # Green for sowing pit
        elif highlight_type == "hover":
            pit_color = arcade.color.LIGHT_YELLOW  # Yellow for hover
        else:
            pit_color = PIT_COLOR  # Normal color
            
        arcade.draw_circle_filled(self.x, self.y, PIT_RADIUS, pit_color)
        arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS, arcade.color.BLACK, 3)

        # Draw counters inside pit
        if self.counters > 0:
            for i in range(self.counters):
                angle = math.radians((360 / self.counters) * i)
                dx = (PIT_RADIUS - 12) * math.cos(angle)
                dy = (PIT_RADIUS - 12) * math.sin(angle)
                arcade.draw_circle_filled(self.x + dx, self.y + dy, COUNTER_RADIUS, COUNTER_COLOR)

        # Draw number
        arcade.draw_text(str(self.counters), self.x - 10, self.y - 10, arcade.color.BLACK, 14)
        
        # Draw X for rubbish holes
        if is_rubbish:
            arcade.draw_text("X", self.x, self.y, arcade.color.RED, 20, 
                           anchor_x="center", anchor_y="center", bold=True)

    def __repr__(self):
        return f"Row:{self.row}  Col:{self.col}  Counter:{self.counters}"