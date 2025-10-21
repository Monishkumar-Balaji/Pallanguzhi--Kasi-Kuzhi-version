import math
import arcade

# --- Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Pallanguzhi"

ROWS = 2
COLS = 7
PIT_RADIUS = 40
COUNTER_RADIUS = 6
START_COUNTERS = 6  # each pit starts with 6 beads as per rules

# Colors
PIT_COLOR = arcade.color.LIGHT_BROWN
BOARD_COLOR = arcade.color.DARK_BROWN
COUNTER_COLOR = arcade.color.GOLD
CAPTURE_COLOR = arcade.color.RED

# UI / Audio / Animation
GAME_TITLE = "PALLANGULI"
MUSIC_FILE = "assets/ambient.mp3"  # placeholder — add your audio file to assets/
TITLE_ANIM_SPEED = 2.0
BUTTON_COLOR = arcade.color.ALMOND
BUTTON_HOVER = arcade.color.LIGHT_YELLOW
SPIN_DURATION = 2.0
AI_THINK_DELAY = 0.8

# AI difficulty
AI_EASY = "easy"
AI_MEDIUM = "medium"
AI_HARD = "hard"
