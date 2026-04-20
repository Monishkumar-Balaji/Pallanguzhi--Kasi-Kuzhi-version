from .constants import *
import math

class Pit:
    def __init__(self, row, col, x, y):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.is_kasi = (col == KASI_COL)
        self.counters = 0 if self.is_kasi else START_COUNTERS

    def draw(self, highlight_type=None, is_rubbish=False):
        import arcade
        
        # ---- DETERMINE PIT APPEARANCE ----
        if is_rubbish:
            base_color = (100, 85, 70)
            rim_color = (120, 100, 80)
            shadow_color = (70, 55, 40)
        elif self.is_kasi:
            if highlight_type == "sowing":
                base_color = HIGHLIGHT_SOWING
            elif highlight_type == "pickup":
                base_color = HIGHLIGHT_PICKUP
            else:
                base_color = KASI_COLOR
            rim_color = KASI_GOLD
            shadow_color = KASI_INNER
        elif highlight_type == "selected":
            base_color = HIGHLIGHT_SELECTED
            rim_color = (180, 210, 230)
            shadow_color = (100, 140, 170)
        elif highlight_type == "sowing":
            base_color = HIGHLIGHT_SOWING
            rim_color = (170, 210, 150)
            shadow_color = (90, 140, 75)
        elif highlight_type == "pickup":
            base_color = HIGHLIGHT_PICKUP
            rim_color = (100, 230, 240)
            shadow_color = (30, 150, 170)
        elif highlight_type == "hover":
            base_color = HIGHLIGHT_HOVER
            rim_color = (220, 190, 130)
            shadow_color = (140, 110, 65)
        else:
            base_color = PIT_COLOR
            rim_color = PIT_RIM
            shadow_color = PIT_SHADOW

        # ---- DRAW CARVED PIT (multi-layer depth effect) ----
        
        # Outer shadow (carved groove)
        arcade.draw_circle_filled(self.x, self.y - 1, PIT_RADIUS + 3, shadow_color)
        
        # Main pit rim (lit edge)
        arcade.draw_circle_filled(self.x, self.y + 1, PIT_RADIUS + 1, rim_color)
        
        # Pit fill (the carved interior)
        arcade.draw_circle_filled(self.x, self.y, PIT_RADIUS, base_color)
        
        # Dark outline
        arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS, (40, 25, 15), 2)
        
        # ---- KASI DECORATIONS ----
        if self.is_kasi:
            # Double gold ring
            arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS - 3, KASI_GOLD, 2)
            arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS + 2, KASI_GOLD, 1)
            # Inner ornamental ring
            arcade.draw_circle_outline(self.x, self.y, PIT_RADIUS - 8, (180, 140, 50), 1)

        # ---- DRAW SEEDS (tamarind-seed style) ----
        if self.counters > 0:
            max_visual = min(self.counters, 20)
            for i in range(max_visual):
                angle = math.radians((360 / max_visual) * i + 15)  # Slight offset
                radius_offset = 14 if not self.is_kasi else 16
                orbit_r = PIT_RADIUS - radius_offset
                dx = orbit_r * math.cos(angle)
                dy = orbit_r * math.sin(angle)
                sx, sy = self.x + dx, self.y + dy
                
                # Seed shadow
                arcade.draw_circle_filled(sx + 1, sy - 1, COUNTER_RADIUS + 1, COUNTER_SHADOW)
                # Seed body
                arcade.draw_circle_filled(sx, sy, COUNTER_RADIUS, COUNTER_COLOR)
                # Seed highlight (tiny bright spot)
                arcade.draw_circle_filled(sx - 1, sy + 1, 2, COUNTER_HIGHLIGHT)

        # ---- DRAW COUNT ----
        text_color = TEXT_CREAM if self.is_kasi else TEXT_CREAM
        # Draw count with shadow for readability
        arcade.draw_text(str(self.counters), self.x - 10 + 1, self.y - 10 - 1, 
                        (30, 20, 10), 15, bold=True)
        arcade.draw_text(str(self.counters), self.x - 10, self.y - 10, 
                        text_color, 15, bold=True)
        
        # ---- KASI LABEL ----
        if self.is_kasi:
            label_y = self.y + PIT_RADIUS + 8 if self.row == 0 else self.y - PIT_RADIUS - 18
            # Shadow
            arcade.draw_text("KASI", self.x + 1, label_y - 1,
                           (40, 25, 10), 11, anchor_x="center", bold=True)
            arcade.draw_text("KASI", self.x, label_y,
                           KASI_GOLD, 11, anchor_x="center", bold=True)
        
        # ---- RUBBISH HOLE MARKER ----
        if is_rubbish:
            # Draw crossed planks instead of ugly X
            r = PIT_RADIUS - 10
            arcade.draw_line(self.x - r, self.y - r, self.x + r, self.y + r, (80, 50, 30), 3)
            arcade.draw_line(self.x - r, self.y + r, self.x + r, self.y - r, (80, 50, 30), 3)

    def __repr__(self):
        kasi_str = " [KASI]" if self.is_kasi else ""
        return f"Row:{self.row}  Col:{self.col}  Counter:{self.counters}{kasi_str}"
