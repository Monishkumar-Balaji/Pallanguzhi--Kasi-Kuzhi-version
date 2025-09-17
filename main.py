import arcade
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
CAPTURE_COLOR = arcade.color.RED


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
            self.pits.append(row_pits)

        # Track turn and captures
        self.current_player = 0  # 0 = top row, 1 = bottom row
        self.active_counters = 0
        self.distribution_path = []
        self.last_row, self.last_col = None, None
        self.distributing = False
        self.captures = [0, 0]  # bowls for each player
        self.temporary_message = None
        self.message_timer = 0

    def on_draw(self):
        self.clear()

        # Draw pits
        for row in self.pits:
            for pit in row:
                pit.draw()

        # Draw bowls (player collections)
        # Player 1 bowl (top row)
        arcade.draw_circle_filled(100, SCREEN_HEIGHT - 50, PIT_RADIUS, CAPTURE_COLOR)
        arcade.draw_text(f"P1: {self.captures[0]}", 70, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

        # Player 2 bowl (bottom row)
        arcade.draw_circle_filled(100, 50, PIT_RADIUS, CAPTURE_COLOR)
        arcade.draw_text(f"P2: {self.captures[1]}", 70, 40, arcade.color.WHITE, 16)

        # Turn info
        arcade.draw_text(
            f"Player {self.current_player + 1}'s turn",
            SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 18
        )
        # Draw temporary message if active
        if self.temporary_message and self.message_timer > 0:
            arcade.draw_text(
                self.temporary_message,
                SCREEN_WIDTH // 2,  # Center horizontally
                SCREEN_HEIGHT - 50,  # Near top
                arcade.color.WHITE,
                18,
                anchor_x="center"  # Center the text
            )

    def on_update(self, delta_time):
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.temporary_message = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.distributing:
            return  # ignore clicks while sowing

        for i, row_pit in enumerate(self.pits):
            for col in range(COLS):
                pit = row_pit[col]
                dist = math.sqrt((x - pit.x) ** 2 + (y - pit.y) ** 2)
                if dist <= PIT_RADIUS:  # clicked inside pit
                    if pit.counters > 0 and i == self.current_player:
                        self.start_distribution(pit)
                    return

    def start_distribution(self, pit):
        self.active_counters = pit.counters
        pit.counters = 0
        self.distribution_path = self.get_distribution_path(pit.row, pit.col)
        self.last_row, self.last_col = pit.row, pit.col
        self.distributing = True
        arcade.schedule(self.distribute_step, 0.3)

    def get_distribution_path(self, row, col):
        """Generator-style path."""
        path = []
        r, c = row, col
        while True:
            if r == 1:  # bottom row → right
                c += 1
                if c >= COLS:
                    r = 0
                    c = COLS - 1
            else:  # top row → left
                c -= 1
                if c < 0:
                    r = 1
                    c = 0
            path.append((r, c))
            if len(path) >= 50:  # safety
                break
        return path

    def distribute_step(self, delta_time):
        if self.active_counters > 0:
            if not self.distribution_path:
                self.distribution_path = self.get_distribution_path(self.last_row, self.last_col)

            r, c = self.distribution_path.pop(0)
            pit = self.pits[r][c]
            pit.counters += 1
            self.active_counters -= 1
            self.last_row, self.last_col = r, c

            # Check for pasu capture (exactly 4 counters)
            if pit.row == self.current_player and pit.counters == 4:
                self.captures[self.current_player] += 4
                pit.counters = 0

        else:
            # Hand is empty → check captures and continuation
            r, c = self.last_row, self.last_col
            next_path = self.get_distribution_path(r, c)
            next_r, next_c = next_path[0]
            next_pit = self.pits[next_r][next_c]

            # Standard capture
            if next_pit.counters == 0 and len(next_path) > 1:
                beyond_r, beyond_c = next_path[1]
                beyond_pit = self.pits[beyond_r][beyond_c]
                if beyond_pit.counters > 0:
                    self.captures[self.current_player] += beyond_pit.counters
                    self.temporary_message = f"Player {self.current_player + 1} collected {beyond_pit.counters} counters from Player {beyond_pit.row + 1}'s {beyond_pit.col}'th pit!"
                    self.message_timer = 3.0  # 3 seconds
                    beyond_pit.counters = 0
                    return 
                    # continue with next non-empty
                    # self.active_counters = 0
                    # self.last_row, self.last_col = beyond_r, beyond_c
                    # self.distribution_path = self.get_distribution_path(beyond_r, beyond_c)
                    # return

            # Check if next two pits are empty → stop
            if next_pit.counters == 0 and len(next_path) > 1:
                r2, c2 = next_path[1]
                if self.pits[r2][c2].counters == 0:
                    arcade.unschedule(self.distribute_step)
                    self.distributing = False
                    self.current_player = 1 - self.current_player
                    return

            # Otherwise, pick up counters from next pit if non-empty
            if next_pit.counters > 0:
                self.active_counters = next_pit.counters
                next_pit.counters = 0
                self.last_row, self.last_col = next_r, next_c
                self.distribution_path = self.get_distribution_path(next_r, next_c)
            else:
                # If just one empty → skip it
                self.distribution_path.pop(0)


if __name__ == "__main__":
    game = Pallanguzhi()
    arcade.run()
