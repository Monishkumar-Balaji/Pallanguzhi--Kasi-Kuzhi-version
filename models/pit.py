from .constants import *
import arcade
import math

class Pit:
    def __init__(self, row, col, x, y):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.counters = START_COUNTERS
        self.highlight = False  # hover/highlight flag

    def draw(self):
        # Draw pit with simple 3D shading
        # darker rim
        arcade.draw_circle_filled(self.x, self.y, PIT_RADIUS + 2, arcade.color.DARK_BROWN)
        # main pit
        arcade.draw_circle_filled(self.x, self.y, PIT_RADIUS, PIT_COLOR)
        # inner sheen to simulate 3D
        arcade.draw_circle_filled(self.x - PIT_RADIUS*0.25, self.y + PIT_RADIUS*0.25, PIT_RADIUS*0.6, arcade.color.BURLYWOOD)
        # outline
        arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS, arcade.color.BLACK, 3)

        # highlight glow
        if self.highlight:
            arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS+6, BUTTON_HOVER, 4)

        # Draw counters inside pit
        if self.counters > 0:
            for i in range(self.counters):
                angle = math.radians((360 / self.counters) * i)
                dx = (PIT_RADIUS - 12) * math.cos(angle)
                dy = (PIT_RADIUS - 12) * math.sin(angle)
                # simple sheen per bead
                arcade.draw_circle_filled(self.x + dx, self.y + dy, COUNTER_RADIUS + 1, arcade.color.DARK_SLATE_GRAY)
                arcade.draw_circle_filled(self.x + dx - 1, self.y + dy + 1, COUNTER_RADIUS - 1, COUNTER_COLOR)

        # Draw number
        arcade.draw_text(str(self.counters), self.x - 10, self.y - 10, arcade.color.BLACK, 14)

    def __repr__(self):
        return f"Row:{self.row}  Col:{self.col}  Counter:{self.counters}"

