import arcade
import math
from .constants import *

# ============ SHARED DRAWING HELPERS ============

def draw_wood_background():
    """Draw a warm wood-textured background with grain lines"""
    # Base dark wood
    arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_COLOR)
    
    # Subtle horizontal wood grain lines
    for i in range(0, SCREEN_HEIGHT, 8):
        shade = 5 if i % 16 == 0 else -3
        color = tuple(max(0, min(255, c + shade)) for c in BOARD_COLOR)
        arcade.draw_line(0, i, SCREEN_WIDTH, i, (*color, 40), 1)
    
    # Subtle vertical variation
    for i in range(0, SCREEN_WIDTH, 60):
        color = tuple(max(0, min(255, c + 8)) for c in BOARD_COLOR)
        arcade.draw_lbwh_rectangle_filled(i, 0, 2, SCREEN_HEIGHT, (*color, 25))


def draw_ornamental_border(x, y, w, h, thickness=3):
    """Draw a carved wood border with corner accents"""
    # Outer border (dark groove)
    arcade.draw_lbwh_rectangle_outline(x, y, w, h, (40, 25, 15), thickness + 1)
    # Inner border (golden inlay)
    arcade.draw_lbwh_rectangle_outline(x + 3, y + 3, w - 6, h - 6, (*KASI_GOLD, 120), 1)
    # Corner diamonds
    for cx, cy in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
        arcade.draw_circle_filled(cx, cy, 4, KASI_GOLD)
        arcade.draw_circle_filled(cx, cy, 2, (40, 25, 15))


def draw_decorative_line(y, width_fraction=0.6):
    """Draw a decorative divider line with center ornament"""
    lw = SCREEN_WIDTH * width_fraction
    lx = (SCREEN_WIDTH - lw) / 2
    # Line
    arcade.draw_line(lx, y, lx + lw, y, (*TEXT_GOLD, 100), 1)
    # Center diamond
    cx = SCREEN_WIDTH / 2
    for d in range(4, 0, -1):
        c = min(255, KASI_GOLD[0] + d * 10), min(255, KASI_GOLD[1] + d * 10), min(255, KASI_GOLD[2] + d * 10)
        points = [(cx, y + d), (cx + d, y), (cx, y - d), (cx - d, y)]
        # Draw diamond shape using lines
        for j in range(4):
            arcade.draw_line(points[j][0], points[j][1], 
                           points[(j+1)%4][0], points[(j+1)%4][1], c, 1)


def draw_board_preview(cx, cy, scale=0.35):
    """Draw a small decorative Pallanguzhi board for visual flair"""
    bw = 7 * 50 * scale
    bh = 2 * 50 * scale
    
    # Board body
    arcade.draw_lbwh_rectangle_filled(cx - bw/2, cy - bh/2, bw, bh, BOARD_INNER)
    arcade.draw_lbwh_rectangle_outline(cx - bw/2, cy - bh/2, bw, bh, (40, 25, 15), 2)
    # Inner border
    arcade.draw_lbwh_rectangle_outline(cx - bw/2 + 2, cy - bh/2 + 2, bw - 4, bh - 4, (*KASI_GOLD, 80), 1)
    
    # Draw mini pits
    pit_r = 10 * scale
    spacing_x = bw / 8
    for row in range(2):
        for col in range(7):
            px = (cx - bw/2) + spacing_x * (col + 1)
            py = cy + (bh/4 if row == 0 else -bh/4)
            
            if col == 3:  # Kasi pit
                arcade.draw_circle_filled(px, py, pit_r + 1, KASI_COLOR)
                arcade.draw_circle_outline(px, py, pit_r + 1, KASI_GOLD, 1)
            else:
                arcade.draw_circle_filled(px, py, pit_r, PIT_COLOR)
                arcade.draw_circle_outline(px, py, pit_r, PIT_SHADOW, 1)
                # Mini seeds
                for s in range(3):
                    angle = math.radians(120 * s + 30)
                    arcade.draw_circle_filled(
                        px + 4 * scale * math.cos(angle),
                        py + 4 * scale * math.sin(angle),
                        2, COUNTER_COLOR
                    )


# ============ WELCOME SCREEN ============

class WelcomeView(arcade.View):
    def __init__(self):
        super().__init__()
        self.rounds = 3
        self.showing_round_input = False
        self.round_input = "3"
        self.selected_ai_difficulty = AI_MEDIUM
        self.time_elapsed = 0  # For subtle animations
        self.start_counters = START_COUNTERS

    def on_show(self):
        arcade.set_background_color(BOARD_COLOR)

    def on_update(self, delta_time):
        self.time_elapsed += delta_time

    def on_draw(self):
        self.clear()
        
        # Wood textured background
        draw_wood_background()
        
        # ---- DECORATIVE BORDER FRAME ----
        draw_ornamental_border(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30)
        
        # ---- TITLE AREA ----
        # Large ornamental title with shadow
        title_y = SCREEN_HEIGHT - 80
        arcade.draw_text("பல்லாங்குழி", SCREEN_WIDTH/2 + 1, title_y + 32 - 1,
                         (30, 18, 8), 18, anchor_x="center")
        arcade.draw_text("பல்லாங்குழி", SCREEN_WIDTH/2, title_y + 32,
                         TEXT_GOLD, 18, anchor_x="center")
        
        # Main title with drop shadow
        arcade.draw_text("PALLANGUZHI", SCREEN_WIDTH/2 + 2, title_y - 2,
                         (20, 12, 5), 36, anchor_x="center", bold=True)
        arcade.draw_text("PALLANGUZHI", SCREEN_WIDTH/2, title_y,
                         TEXT_GOLD, 36, anchor_x="center", bold=True)
        
        # Subtitle
        arcade.draw_text("A Traditional Tamil Board Game", SCREEN_WIDTH/2, title_y - 30,
                         TEXT_DIM, 13, anchor_x="center")
        
        # Decorative line below title
        draw_decorative_line(title_y - 42)
        
        # ---- BOARD PREVIEW ----
        draw_board_preview(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70, 0.5)

        if not self.showing_round_input:
            menu_y = SCREEN_HEIGHT / 2 - 20
            
            # ---- MENU OPTIONS ----
            # Play Multiplayer
            pulse = 0.85 + 0.15 * math.sin(self.time_elapsed * 2)
            arcade.draw_text("[ M ]  Play Multiplayer", SCREEN_WIDTH/2, menu_y + 30,
                             (int(180 * pulse), int(220 * pulse), int(140 * pulse)), 18,
                             anchor_x="center", bold=True)
            
            # Play with AI
            arcade.draw_text("[ A ]  Play with AI", SCREEN_WIDTH/2, menu_y,
                             (int(220 * pulse), int(200 * pulse), int(130 * pulse)), 18,
                             anchor_x="center", bold=True)
            
            # Settings line
            diff_color = {AI_EASY: (120, 200, 120), AI_MEDIUM: (200, 200, 100), AI_HARD: (220, 120, 100)}
            arcade.draw_text(f"[ D ]  Difficulty: {self.selected_ai_difficulty.title()}", 
                             SCREEN_WIDTH/2 - 200, menu_y - 40,
                             diff_color.get(self.selected_ai_difficulty, TEXT_CREAM), 14,
                             anchor_x="center")
            arcade.draw_text(f"[ R ]  Rounds: {self.rounds}", 
                             SCREEN_WIDTH/2, menu_y - 40,
                             TEXT_CREAM, 14, anchor_x="center")
            arcade.draw_text(f"[ S ]  Counters: {self.start_counters}", 
                             SCREEN_WIDTH/2 + 200, menu_y - 40,
                             TEXT_CREAM, 14, anchor_x="center")

            # Decorative line
            draw_decorative_line(menu_y - 65)
            
            # Game Rules - special button style
            rules_y = menu_y - 95
            # Box background
            box_w, box_h = 240, 32
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH/2 - box_w/2, rules_y - 8, box_w, box_h, 
                                                (*BOARD_BORDER, 180))
            arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH/2 - box_w/2, rules_y - 8, box_w, box_h,
                                                 KASI_GOLD, 1)
            arcade.draw_text("[ G ]  Game Rules", SCREEN_WIDTH/2, rules_y,
                             TEXT_GOLD, 16, anchor_x="center", bold=True)
            
            # Footer
            arcade.draw_text("A game of strategy, counting & planning", SCREEN_WIDTH/2, 25,
                             TEXT_DIM, 11, anchor_x="center")

        else:
            # ---- ROUND INPUT MODE ----
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH/2 - 180, SCREEN_HEIGHT/2 - 80, 360, 100,
                                                (*BOARD_BORDER, 200))
            arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH/2 - 180, SCREEN_HEIGHT/2 - 80, 360, 100,
                                                 KASI_GOLD, 1)
            arcade.draw_text("Enter number of rounds (1-10):", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10,
                             TEXT_CREAM, 18, anchor_x="center")
            arcade.draw_text(self.round_input, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 45,
                             TEXT_GOLD, 28, anchor_x="center", bold=True)
            arcade.draw_text("Press ENTER to confirm", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70,
                             TEXT_DIM, 14, anchor_x="center")

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
                if len(self.round_input) < 2:
                    self.round_input += chr(key)
        else:
            if key == arcade.key.M:
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=False, total_rounds=self.rounds, start_counters=self.start_counters)
                self.window.show_view(game_view)
            elif key == arcade.key.A:
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=True, total_rounds=self.rounds, ai_difficulty=self.selected_ai_difficulty, start_counters=self.start_counters)
                self.window.show_view(game_view)
            elif key == arcade.key.R:
                self.showing_round_input = True
                self.round_input = str(self.rounds)
            elif key == arcade.key.S:
                self.start_counters += 1
                if self.start_counters > 6:
                    self.start_counters = 2
            elif key == arcade.key.D:
                difficulties = [AI_EASY, AI_MEDIUM, AI_HARD]
                current_index = difficulties.index(self.selected_ai_difficulty)
                next_index = (current_index + 1) % len(difficulties)
                self.selected_ai_difficulty = difficulties[next_index]
            elif key == arcade.key.G:
                rules_view = GameRulesView()
                self.window.show_view(rules_view)


# ============ GAME RULES VIEW ============

class GameRulesView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scroll_y = 0
        self.max_scroll = 2200
        self.scroll_speed = 30
        
        # All rules text sections: (text, font_size, color, is_heading)
        self.sections = [
            ("PALLANGUZHI - Complete Game Rules", 26, TEXT_GOLD, True),
            ("", 10, TEXT_CREAM, False),
            ("INTRODUCTION", 20, (180, 210, 130), True),
            ("Pallanguzhi is a traditional South Indian board game, commonly played", 14, TEXT_CREAM, False),
            ("in Tamil Nadu. It belongs to the mancala family of games, involving", 14, TEXT_CREAM, False),
            ("strategy, counting, and planning. The game is typically played by two", 14, TEXT_CREAM, False),
            ("players using a wooden board with pits and small seeds.", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("GAME SETUP", 20, (180, 210, 130), True),
            ("  * Board: 2 rows, 7 pits per row (14 pits total)", 14, TEXT_CREAM, False),
            ("  * Each regular pit starts with 6 seeds", 14, TEXT_CREAM, False),
            ("  * Each player controls one row of 7 pits", 14, TEXT_CREAM, False),
            ("  * The center pit (column 4) is the Kasi Kuzhi (storage pit)", 14, TEXT_GOLD, False),
            ("  * Each Kasi Kuzhi starts with 1 seed", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("OBJECTIVE", 20, (180, 210, 130), True),
            ("  Collect the maximum number of seeds.", 14, TEXT_CREAM, False),
            ("  The player with the most seeds at the end wins.", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("BASIC GAMEPLAY RULES", 20, (180, 210, 130), True),
            ("  1. Starting a Turn:", 16, (160, 190, 220), False),
            ("     - Select any pit from your row (not Kasi)", 14, TEXT_CREAM, False),
            ("     - Pick up all seeds from that pit", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("  2. Sowing (Distribution):", 16, (160, 190, 220), False),
            ("     - Seeds are distributed one by one in counterclockwise direction", 14, TEXT_CREAM, False),
            ("     - Includes: Own pits, Opponent's pits, and Kasi Kuzhi", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("  3. Continuation Rule:", 16, (160, 190, 220), False),
            ("     - After placing the last seed, if the next pit has seeds,", 14, TEXT_CREAM, False),
            ("       pick them up and continue sowing", 14, TEXT_CREAM, False),
            ("     - This continues until no continuation is possible", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("CAPTURE RULES", 20, (180, 210, 130), True),
            ("  If the last seed lands in a pit and the next pit is empty:", 14, TEXT_CREAM, False),
            ("  - Capture seeds from the pit after the empty pit", 14, TEXT_CREAM, False),
            ("  - Also capture seeds from the opposite pit", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("  Pasu Capture: If any regular pit reaches exactly 4 seeds,", 14, TEXT_GOLD, False),
            ("  the row's player captures all 4 seeds immediately.", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("KASI KUZHI (Storage Pit) RULES", 20, TEXT_GOLD, True),
            ("  Special Pits:", 16, (160, 190, 220), False),
            ("  - Each player has 1 Kasi Kuzhi (center pit)", 14, TEXT_CREAM, False),
            ("  - Cannot start a turn from Kasi", 14, TEXT_CREAM, False),
            ("  - Seeds ARE dropped into Kasi during sowing", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("  Kasi Eligibility (Reservation):", 16, (160, 190, 220), False),
            ("  A player becomes eligible to reserve Kasi when:", 14, TEXT_CREAM, False),
            ("  Last seed lands in a pit -> next pit is empty ->", 14, TEXT_GOLD, False),
            ("  next pit after that is Kasi Kuzhi", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("  What happens when eligible:", 16, (160, 190, 220), False),
            ("  - Player does NOT collect immediately", 14, (200, 100, 100), False),
            ("  - Kasi Kuzhi is marked as 'reserved'", 14, (140, 200, 140), False),
            ("  - Seeds remain inside the Kasi", 14, TEXT_CREAM, False),
            ("  - Collection is delayed until end of round", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("END OF ROUND - KASI COLLECTION", 20, TEXT_GOLD, True),
            ("  Case 1: Only One Player Reserved Kasi", 16, (140, 200, 140), False),
            ("    - That player takes seeds ONLY from the reserved Kasi", 14, TEXT_CREAM, False),
            ("    - Seeds in the unreserved Kasi carry forward", 14, TEXT_CREAM, False),
            ("  Case 2: Both Players Reserved Kasi", 16, (160, 190, 220), False),
            ("    - Seeds from both Kasi pits are combined", 14, TEXT_CREAM, False),
            ("    - Shared equally between both players", 14, TEXT_CREAM, False),
            ("    - If odd: 1 seed remains in Kasi for next round", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("  Case 3: No Player Reserved Kasi", 16, (200, 100, 100), False),
            ("    - No one collects anything", 14, TEXT_CREAM, False),
            ("    - All seeds in both Kasi Kuzhi carry forward", 14, TEXT_CREAM, False),
            ("    - Makes the next round more competitive!", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("END OF ROUND", 20, (180, 210, 130), True),
            ("  A round ends when one player has no seeds in their pits.", 14, TEXT_CREAM, False),
            ("  The opponent collects all remaining seeds from their side.", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("NEXT ROUND SETUP", 20, (180, 210, 130), True),
            ("  Players refill their pits using collected seeds:", 14, TEXT_CREAM, False),
            ("  - Each pit must have the initial number of seeds (6)", 14, TEXT_CREAM, False),
            ("  - If insufficient seeds: some pits remain empty (rubbish holes)", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("END OF GAME", 20, (180, 210, 130), True),
            ("  The game continues for multiple rounds.", 14, TEXT_CREAM, False),
            ("  Ends when a player cannot refill even 1 pit.", 14, TEXT_CREAM, False),
            ("  Player with maximum collected seeds wins!", 14, TEXT_GOLD, False),
            ("", 10, TEXT_CREAM, False),
            ("STRATEGY TIPS", 20, (180, 210, 130), True),
            ("  - Choose pits that allow long continuations", 14, TEXT_CREAM, False),
            ("  - Plan moves to trigger capture conditions", 14, TEXT_CREAM, False),
            ("  - Plan moves to trigger Kasi eligibility", 14, TEXT_CREAM, False),
            ("  - Monitor Kasi: Leaving it unclaimed may benefit opponent", 14, TEXT_CREAM, False),
            ("  - Try to avoid emptying your row too early", 14, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("", 10, TEXT_CREAM, False),
            ("Press ESC to return to the main menu", 16, TEXT_DIM, False),
        ]
    
    def on_show(self):
        arcade.set_background_color(BOARD_COLOR)
    
    def on_draw(self):
        self.clear()
        draw_wood_background()
        draw_ornamental_border(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30)
        
        # Header bar
        arcade.draw_lbwh_rectangle_filled(20, SCREEN_HEIGHT - 45, SCREEN_WIDTH - 40, 28, (*BOARD_BORDER, 180))
        arcade.draw_text("Game Rules  |  Scroll: UP/DOWN or Mouse Wheel  |  ESC: Back",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 38, TEXT_DIM, 12, anchor_x="center")
        
        # Draw rule sections with scroll offset
        y = SCREEN_HEIGHT - 75 + self.scroll_y
        line_spacing = 22
        
        for text, size, color, is_heading in self.sections:
            if text == "":
                y -= 8
                continue
            
            if is_heading:
                y -= 6
            
            if -20 < y < SCREEN_HEIGHT - 45:
                x = SCREEN_WIDTH / 2 if is_heading else 80
                anchor = "center" if is_heading else "left"
                # Drop shadow for headings
                if is_heading:
                    arcade.draw_text(text, x + 1, y - 1, (20, 12, 5), size, 
                                   anchor_x=anchor, bold=True)
                arcade.draw_text(text, x, y, color, size, 
                               anchor_x=anchor, bold=is_heading)
                if is_heading:
                    line_width = len(text) * size * 0.55
                    arcade.draw_line(x - line_width / 2, y - 4, 
                                   x + line_width / 2, y - 4, 
                                   (*color, 100), 1)
            
            y -= line_spacing
            if is_heading:
                y -= 4
        
        # Scroll indicator
        if self.scroll_y < self.max_scroll:
            arcade.draw_text("\u25bc Scroll down for more \u25bc", SCREEN_WIDTH / 2, 25,
                           TEXT_DIM, 12, anchor_x="center")
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)
        elif key == arcade.key.DOWN:
            self.scroll_y = min(self.scroll_y + self.scroll_speed, self.max_scroll)
        elif key == arcade.key.UP:
            self.scroll_y = max(self.scroll_y - self.scroll_speed, 0)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll_y = max(0, min(self.scroll_y - scroll_y * self.scroll_speed, self.max_scroll))


# ============ GAME OVER VIEW ============

class GameOverView(arcade.View):
    def __init__(self, winner, scores, total_rounds, current_round, final=False,
                 start_counters=6, ai_mode=False, ai_difficulty=AI_MEDIUM):
        super().__init__()
        self.winner = winner
        self.scores = scores
        self.total_rounds = total_rounds
        self.current_round = current_round
        self.final = final
        self.start_counters = start_counters
        self.ai_mode = ai_mode
        self.ai_difficulty = ai_difficulty
        self.next_round_captures = None
        self.kasi_leftover = 0
        self.time_elapsed = 0

    def on_show(self):
        arcade.set_background_color(BOARD_COLOR)

    def on_update(self, delta_time):
        self.time_elapsed += delta_time

    def on_draw(self):
        self.clear()
        draw_wood_background()
        draw_ornamental_border(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30)
        
        # Central panel
        panel_w, panel_h = 500, 300
        px = SCREEN_WIDTH/2 - panel_w/2
        py = SCREEN_HEIGHT/2 - panel_h/2
        arcade.draw_lbwh_rectangle_filled(px, py, panel_w, panel_h, (*BOARD_INNER, 220))
        arcade.draw_lbwh_rectangle_outline(px, py, panel_w, panel_h, KASI_GOLD, 2)
        arcade.draw_lbwh_rectangle_outline(px + 4, py + 4, panel_w - 8, panel_h - 8, (*TEXT_DIM, 60), 1)
        
        if self.final:
            # Pulsing title
            pulse = 0.8 + 0.2 * math.sin(self.time_elapsed * 3)
            title_color = (int(218 * pulse), int(175 * pulse), int(60 * pulse))
            
            arcade.draw_text("GAME OVER!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100,
                             title_color, 32, anchor_x="center", bold=True)
            
            draw_decorative_line(SCREEN_HEIGHT/2 + 85)
            
            arcade.draw_text(f"Final Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                             TEXT_GOLD, 24, anchor_x="center", bold=True)
        else:
            arcade.draw_text(f"Round {self.current_round} Complete!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100,
                             TEXT_GOLD, 28, anchor_x="center", bold=True)
            
            draw_decorative_line(SCREEN_HEIGHT/2 + 85)
            
            arcade.draw_text(f"Round Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                             TEXT_GOLD, 22, anchor_x="center", bold=True)
        
        # Score display with wooden box style  
        score_y = SCREEN_HEIGHT/2 - 5
        # P1 score box
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH/2 - 180, score_y - 15, 160, 50, (*CAPTURE_COLOR, 180))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH/2 - 180, score_y - 15, 160, 50, CAPTURE_BORDER, 1)
        arcade.draw_text(f"Player 1", SCREEN_WIDTH/2 - 100, score_y + 15, TEXT_CREAM, 13, anchor_x="center")
        arcade.draw_text(f"{self.scores[0]} seeds", SCREEN_WIDTH/2 - 100, score_y - 5, TEXT_GOLD, 20, anchor_x="center", bold=True)
        
        # P2 score box
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH/2 + 20, score_y - 15, 160, 50, (*CAPTURE_COLOR, 180))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH/2 + 20, score_y - 15, 160, 50, CAPTURE_BORDER, 1)
        arcade.draw_text(f"Player 2", SCREEN_WIDTH/2 + 100, score_y + 15, TEXT_CREAM, 13, anchor_x="center")
        arcade.draw_text(f"{self.scores[1]} seeds", SCREEN_WIDTH/2 + 100, score_y - 5, TEXT_GOLD, 20, anchor_x="center", bold=True)
        
        if self.final:
            arcade.draw_text(f"Played {self.current_round} of {self.total_rounds} rounds",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60,
                             TEXT_DIM, 14, anchor_x="center")
            arcade.draw_text("Press ENTER to return to Welcome screen",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 110, TEXT_DIM, 14, anchor_x="center")
        else:
            arcade.draw_text(f"Round {self.current_round} of {self.total_rounds}",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60,
                             TEXT_DIM, 14, anchor_x="center")
            arcade.draw_text("Press ENTER to continue to next round",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 110, TEXT_DIM, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)
        elif key == arcade.key.ENTER:
            if self.final:
                welcome_view = WelcomeView()
                self.window.show_view(welcome_view)
            else:
                # Start next round with current captures
                from .pallanguzhi import Pallanguzhi
                game_view = Pallanguzhi(ai_mode=self.ai_mode, total_rounds=self.total_rounds, 
                                      current_round=self.current_round + 1,
                                      previous_captures=self.scores[:],
                                      kasi_leftover=self.kasi_leftover,
                                      start_counters=self.start_counters,
                                      ai_difficulty=self.ai_difficulty)
                self.window.show_view(game_view)
