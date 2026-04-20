#constants.py
import math
import arcade

# --- Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 520
SCREEN_TITLE = "Pallanguzhi"

ROWS = 2
COLS = 7
PIT_RADIUS = 40
COUNTER_RADIUS = 6
START_COUNTERS = 6
KASI_COL = 3  # Center column is the Kasi Kuzhi

# Regular columns (non-Kasi)
REGULAR_COLS = [0, 1, 2, 4, 5, 6]

# ============ TRADITIONAL WOOD COLOR PALETTE ============

# Board & Background - Rich Rosewood / Teak
BOARD_COLOR = (62, 39, 25)           # Deep rosewood
BOARD_BORDER = (90, 55, 30)          # Lighter wood edge
BOARD_INNER = (78, 48, 28)           # Inner board grain

# Pits - Carved wood look
PIT_COLOR = (140, 95, 55)            # Warm teak pit
PIT_SHADOW = (85, 55, 30)            # Pit shadow ring (depth)
PIT_RIM = (170, 120, 70)             # Lit rim of carved pit

# Kasi Kuzhi - Special carved pit
KASI_COLOR = (110, 70, 45)           # Darker carved Kasi
KASI_GOLD = (218, 165, 32)           # Gold accent ring
KASI_INNER = (90, 58, 35)            # Deep Kasi interior

# Seeds / Counters - Tamarind seed look
COUNTER_COLOR = (200, 160, 80)       # Golden tamarind seed
COUNTER_SHADOW = (160, 120, 50)      # Seed shadow
COUNTER_HIGHLIGHT = (240, 210, 140)  # Seed highlight

# Capture bowls
CAPTURE_COLOR = (120, 65, 35)        # Wooden bowl
CAPTURE_BORDER = (180, 130, 70)      # Bowl rim

# UI Colors
TEXT_GOLD = (218, 175, 60)           # Warm gold text
TEXT_CREAM = (245, 235, 210)         # Cream white
TEXT_DIM = (160, 140, 110)           # Subtle text

# Highlight Colors
HIGHLIGHT_HOVER = (190, 160, 100)    # Warm hover glow
HIGHLIGHT_SELECTED = (140, 180, 200) # Cool blue selected
HIGHLIGHT_SOWING = (130, 180, 110)   # Soft green sowing
HIGHLIGHT_PICKUP = (60, 200, 220)    # Bright cyan pickup

# Message Bars
MSG_P1_BG = (20, 160, 40, 240)      # Vibrant green
MSG_P2_BG = (20, 100, 220, 240)     # Vibrant blue  
MSG_GENERAL_BG = (180, 40, 180, 240) # Vibrant purple

# AI Difficulties
AI_EASY = "easy"
AI_MEDIUM = "medium" 
AI_HARD = "hard"
