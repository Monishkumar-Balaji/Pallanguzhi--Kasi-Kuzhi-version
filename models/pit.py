from .constants import *
class Pit:
    def __init__(self, row, col, x, y):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.counters = START_COUNTERS

    def draw(self):
        # Draw pit
        arcade.draw_circle_filled(self.x, self.y, PIT_RADIUS, PIT_COLOR)
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

    def __repr__(self):
        return f"Row:{self.row}  Col:{self.col}  Counter:{self.counters}"

