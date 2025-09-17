import arcade
import random
import math
# --- Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Pallanguzhi"

ROWS = 2
COLS = 7
PIT_RADIUS = 40
COUNTER_RADIUS = 6
START_COUNTERS = 5

# Colors
PIT_COLOR = arcade.color.LIGHT_BROWN
BOARD_COLOR = arcade.color.DARK_BROWN
COUNTER_COLOR = arcade.color.GOLD


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
        arcade.draw_text(str(self.counters), self.x - 10, self.y - 10, arcade.color.BLACK, 14)


        # Draw counters inside pit
        if self.counters > 0:
            for i in range(self.counters):
                angle = math.radians((360 / self.counters) * i)  # convert to radians
                dx = (PIT_RADIUS - 12) * math.cos(angle)
                dy = (PIT_RADIUS - 12) * math.sin(angle)
                arcade.draw_circle_filled(self.x + dx, self.y + dy, COUNTER_RADIUS, COUNTER_COLOR)

        # Draw number for debugging
        arcade.draw_text(str(self.counters), self.x - 10, self.y - 10, arcade.color.BLACK, 14)

    def __repr__(self):
        return f"Row:{self.row}  Col:{self.col}  Counter:{self.counters}"


class Pallanguzhi(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BOARD_COLOR)

        # Create 2D grid of pits
        self.pits = []
        spacing_x = SCREEN_WIDTH // (COLS + 1)
        spacing_y = SCREEN_HEIGHT // (ROWS + 1)

        for row in range(ROWS):
            row_pits = []
            for col in range(COLS):
                x = (col + 1) * spacing_x
                y = SCREEN_HEIGHT - (row + 1) * spacing_y
                row_pits.append(Pit(row, col, x, y))
                # self.pits.append(Pit(row, col, x, y))
            self.pits.append(row_pits)

        # Track turn
        self.current_player = 0  # 0 = top row, 1 = bottom row
        self.active_counters = 0
        self.active_index = None
        self.distributing = False
        self.distribution_path = []

    def on_draw(self):
        self.clear()

        # Draw pits
        for row in self.pits:
            for pit in row:
                pit.draw()

        # Turn info
        # arcade.draw_text(
        #     f"Player {self.current_player + 1}'s turn",
        #     20, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18
        # )
        #arcade.draw_text("Hello", 50, 50, arcade.color.BLACK, 14)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Detect which circular pit was clicked.
        self.pits is a 2D list: self.pits[row][col] -> Pit object with .x, .y, .counters, .row
        """
        # Ignore clicks while distributing
        if getattr(self, "distributing", False):
            return

        print("Mouse click registered", x, y)

        for row_idx, row_pits in enumerate(self.pits):
            for col_idx, pit in enumerate(row_pits):
                left   = pit.x - PIT_RADIUS
                right  = pit.x + PIT_RADIUS
                bottom = pit.y - PIT_RADIUS
                top    = pit.y + PIT_RADIUS
                if left <= x <= right and bottom <= y <= top:
                    print(f"Clicked pit row:{row_idx}, col:{col_idx}, counters = {pit.counters}")

                    # Optional: only allow clicking your own row
                    # Uncomment if you want that rule
                    # if (self.current_player == 0 and pit.row != 0) or \
                    #    (self.current_player == 1 and pit.row != 1):
                    #     print("Not your pit.")
                    #     return

                    if pit.counters > 0:
                        # start_distribution expects a Pit object in your code
                        self.start_distribution(pit)
                    else:
                        print("This pit is empty!")

                    return  # return immediately after handling the click

        # If you fall here, no pit was clicked
        print("Click not inside any pit.")



    def start_distribution(self, pit):
        """Pick up counters from selected pit and start distribution."""
        print(f"{pit}")
        self.active_counters = pit.counters
        pit.counters = 0
        self.distribution_path = self.get_distribution_path(pit.row, pit.col)
        self.distributing = True
        arcade.schedule(self.distribute_step, 0.3)

    def get_distribution_path(self, row, col):
        """Return the sequence of pits (row, col) to distribute into."""
        path = []
        r, c = row, col
        while True:
            # Move counterclockwise: right on bottom row, left on top row
            if r == 1:  # bottom row, move right
                c += 1
                if c >= COLS:
                    r = 0
                    c = COLS - 1
            else:  # top row, move left
                c -= 1
                if c < 0:
                    r = 1
                    c = 0
            path.append((r, c))
            if len(path) >= 14 * 2:  # safety cap
                break
        return path

    def distribute_step(self, delta_time):
        if self.active_counters <= 0:
            # Stop distributing
            arcade.unschedule(self.distribute_step)
            self.distributing = False
            # Switch player
            self.current_player = 1 - self.current_player
            return

        if not self.distribution_path:
            arcade.unschedule(self.distribute_step)
            self.distributing = False
            return

        # Drop one counter
        r, c = self.distribution_path.pop(0)
        self.pits[r][c].counters += 1
        self.active_counters -= 1


if __name__ == "__main__":
    game = Pallanguzhi()
    arcade.run()
