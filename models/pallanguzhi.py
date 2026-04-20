from .constants import *
from .pit import Pit
import arcade
import math
import random
import copy


class Pallanguzhi(arcade.View):
    def __init__(self, ai_mode=False, total_rounds=3, current_round=1,
                 previous_captures=None, ai_difficulty=AI_MEDIUM, kasi_leftover=0,
                 start_counters=6):
        super().__init__()
        arcade.set_background_color(BOARD_COLOR)
        self.ai_mode = ai_mode
        self.total_rounds = total_rounds
        self.current_round = current_round
        self.ai_difficulty = ai_difficulty
        self.start_counters = start_counters
        if isinstance(kasi_leftover, list):
            self.kasi_leftover = kasi_leftover
        else:
            self.kasi_leftover = [kasi_leftover if kasi_leftover else 0, 0]

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
        self.current_player = 0
        self.active_counters = 0
        self.distribution_path = []
        self.last_row, self.last_col = None, None
        self.distributing = False
        self.captures = previous_captures if previous_captures else [0, 0]
        self.temporary_message = None
        self.message_timer = 0
        self.message_player = None  # Which player's message (0=P1, 1=P2, None=general)
        self.round_ending = False
        
        # Animation and highlighting
        self.highlighted_pit = None
        self.selected_pit = None
        self.sowing_pit = None
        self.pickup_pit = None
        self.pickup_pit_timer = 0
        
        # Rubbish holes
        self.rubbish_holes = [[False] * COLS for _ in range(ROWS)]
        
        # Initialize pits for new round
        self.initialize_round()

    def initialize_round(self):
        """Initialize pits for the current round"""
        self.kasi_reserved_by = [None, None]
        if self.current_round == 1:
            for row in range(ROWS):
                for col in range(COLS):
                    self.rubbish_holes[row][col] = False
                    if col == KASI_COL:
                        self.pits[row][col].counters = 1
                    else:
                        self.pits[row][col].counters = self.start_counters
        else:
            # Subsequent rounds - clear all pits
            for row in range(ROWS):
                for col in range(COLS):
                    self.rubbish_holes[row][col] = False
                    self.pits[row][col].counters = 0
            
            # Each player fills their regular pits from captures
            for player in range(2):
                pits_to_fill = self.captures[player] // self.start_counters
                pits_to_fill = min(pits_to_fill, len(REGULAR_COLS))
                
                filled = 0
                for col in REGULAR_COLS:
                    if filled >= pits_to_fill:
                        break
                    self.pits[player][col].counters = self.start_counters
                    self.captures[player] -= self.start_counters
                    filled += 1
                
                # Mark remaining regular pits as rubbish holes
                for col in REGULAR_COLS:
                    if self.pits[player][col].counters == 0:
                        self.rubbish_holes[player][col] = True
                
                # Kasi is never a rubbish hole
                self.rubbish_holes[player][KASI_COL] = False
                self.pits[player][KASI_COL].counters = 0
            
            # Place leftover Kasi seed from previous round
            if self.kasi_leftover[0] > 0:
                self.pits[0][KASI_COL].counters += self.kasi_leftover[0]
            if self.kasi_leftover[1] > 0:
                self.pits[1][KASI_COL].counters += self.kasi_leftover[1]
            self.kasi_leftover = [0, 0]

    def on_draw(self):
        self.clear()
        
        from .viewScreens import draw_wood_background, draw_ornamental_border
        
        # ---- WOOD BACKGROUND ----
        draw_wood_background()
        
        # ---- BOARD AREA (carved wooden board look) ----
        board_margin = 20
        board_top = SCREEN_HEIGHT - 70
        board_bottom = 45
        # Board shadow
        arcade.draw_lbwh_rectangle_filled(board_margin + 3, board_bottom - 3, 
                                            SCREEN_WIDTH - board_margin * 2, board_top - board_bottom, 
                                            (25, 15, 8))
        # Board body
        arcade.draw_lbwh_rectangle_filled(board_margin, board_bottom, 
                                            SCREEN_WIDTH - board_margin * 2, board_top - board_bottom, 
                                            BOARD_INNER)
        # Board border (carved edge)
        arcade.draw_lbwh_rectangle_outline(board_margin, board_bottom, 
                                            SCREEN_WIDTH - board_margin * 2, board_top - board_bottom, 
                                            (40, 25, 15), 3)
        # Inner gold inlay
        arcade.draw_lbwh_rectangle_outline(board_margin + 4, board_bottom + 4, 
                                            SCREEN_WIDTH - board_margin * 2 - 8, board_top - board_bottom - 8, 
                                            (*KASI_GOLD, 60), 1)
        
        # ---- TOP STATUS BAR ----
        # Background panel
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - 65, SCREEN_WIDTH, 65, (*BOARD_BORDER, 200))
        arcade.draw_line(0, SCREEN_HEIGHT - 65, SCREEN_WIDTH, SCREEN_HEIGHT - 65, (40, 25, 15), 2)
        
        # Round info
        arcade.draw_text(f"Round {self.current_round}/{self.total_rounds}", 
                        SCREEN_WIDTH - 180, SCREEN_HEIGHT - 30, TEXT_DIM, 13)
        
        # Turn indicator with colored accent
        if self.ai_mode and self.current_player == 1:
            turn_text = "AI's turn"
            turn_color = (200, 150, 100)
        else:
            turn_text = f"Player {self.current_player + 1}'s turn"
            turn_color = TEXT_GOLD
        arcade.draw_text(turn_text, SCREEN_WIDTH - 180, SCREEN_HEIGHT - 52, 
                        turn_color, 17, bold=True)

        # Kasi status
        kasi_p1 = self.pits[0][KASI_COL].counters
        kasi_p2 = self.pits[1][KASI_COL].counters
        status_top = f"Reserved by P{self.kasi_reserved_by[0] + 1}" if self.kasi_reserved_by[0] is not None else "Unreserved"
        status_bottom = f"Reserved by P{self.kasi_reserved_by[1] + 1}" if self.kasi_reserved_by[1] is not None else "Unreserved"
        
        res_color_1 = (140, 200, 140) if self.kasi_reserved_by[0] is not None else TEXT_DIM
        res_color_2 = (140, 200, 140) if self.kasi_reserved_by[1] is not None else TEXT_DIM
        arcade.draw_text(f"P1 Kasi [{status_top}]: {kasi_p1}", 210, SCREEN_HEIGHT - 30, res_color_1, 12, bold=True)
        arcade.draw_text(f"P2 Kasi [{status_bottom}]: {kasi_p2}", 210, SCREEN_HEIGHT - 50, res_color_2, 12, bold=True)

        # Capture bowls (wooden bowl style)
        for i, (label, score, bx) in enumerate([("P1", self.captures[0], 55), ("P2", self.captures[1], 145)]):
            by = SCREEN_HEIGHT - 35
            # Bowl shadow
            arcade.draw_circle_filled(bx + 1, by - 1, 28, (30, 18, 8))
            # Bowl body
            arcade.draw_circle_filled(bx, by, 27, CAPTURE_COLOR)
            # Bowl rim highlight
            arcade.draw_circle_outline(bx, by, 27, CAPTURE_BORDER, 2)
            # Inner dark
            arcade.draw_circle_filled(bx, by, 18, (90, 45, 22))
            # Score text
            arcade.draw_text(f"{label}", bx, by + 5, TEXT_DIM, 10, anchor_x="center")
            arcade.draw_text(f"{score}", bx, by - 12, TEXT_GOLD, 16, anchor_x="center", bold=True)

        # ---- GAME BOARD - DRAW PITS ----
        for row in self.pits:
            for pit in row:
                is_hover = (self.highlighted_pit == (pit.row, pit.col))
                is_selected = (self.selected_pit == (pit.row, pit.col))
                is_sowing = (self.sowing_pit == (pit.row, pit.col))
                is_pickup = (self.pickup_pit == (pit.row, pit.col) and self.pickup_pit_timer > 0)
                
                if is_pickup:
                    hl = "pickup"
                elif is_hover:
                    hl = "hover"
                elif is_selected:
                    hl = "selected"
                elif is_sowing:
                    hl = "sowing"
                else:
                    hl = None
                
                pit.draw(highlight_type=hl,
                        is_rubbish=self.rubbish_holes[pit.row][pit.col])

        # ---- SEEDS IN HAND ----
        if self.distributing and self.active_counters >= 0:
            # Draw styled panel
            panel_w, panel_h = 180, 35
            px = SCREEN_WIDTH // 2 - panel_w // 2
            py = SCREEN_HEIGHT // 2 - panel_h // 2
            arcade.draw_lbwh_rectangle_filled(px, py, panel_w, panel_h, (*BOARD_BORDER, 200))
            arcade.draw_lbwh_rectangle_outline(px, py, panel_w, panel_h, (*KASI_GOLD, 150), 1)
            arcade.draw_text(f"Seeds in hand: {self.active_counters}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                           TEXT_GOLD, 18, anchor_x="center", anchor_y="center", bold=True)

        # ---- MESSAGE BARS ----
        if self.temporary_message and self.message_timer > 0:
            if self.message_player == 0:
                msg_y = SCREEN_HEIGHT - 95
                arcade.draw_lbwh_rectangle_filled(30, msg_y - 5, SCREEN_WIDTH - 60, 28, MSG_P1_BG)
                arcade.draw_lbwh_rectangle_outline(30, msg_y - 5, SCREEN_WIDTH - 60, 28, (120, 180, 100, 150), 1)
                arcade.draw_text(
                    self.temporary_message, SCREEN_WIDTH // 2, msg_y + 2,
                    (180, 230, 160), 14, anchor_x="center", bold=True
                )
            elif self.message_player == 1:
                msg_y = 52
                arcade.draw_lbwh_rectangle_filled(30, msg_y - 5, SCREEN_WIDTH - 60, 28, MSG_P2_BG)
                arcade.draw_lbwh_rectangle_outline(30, msg_y - 5, SCREEN_WIDTH - 60, 28, (100, 120, 180, 150), 1)
                arcade.draw_text(
                    self.temporary_message, SCREEN_WIDTH // 2, msg_y + 2,
                    (160, 180, 230), 14, anchor_x="center", bold=True
                )
            else:
                arcade.draw_lbwh_rectangle_filled(30, 5, SCREEN_WIDTH - 60, 32, MSG_GENERAL_BG)
                arcade.draw_lbwh_rectangle_outline(30, 5, SCREEN_WIDTH - 60, 32, (*KASI_GOLD, 100), 1)
                arcade.draw_text(
                    self.temporary_message, SCREEN_WIDTH // 2, 13,
                    TEXT_CREAM, 14, anchor_x="center", bold=True
                )

    def check_termination(self):
        """Check if round should end - when ANY player has no counters in regular pits"""
        if self.distributing or getattr(self, 'round_ending', False):
            return False
            
        for player in range(2):
            player_has_counters = False
            for col in REGULAR_COLS:
                if (not self.rubbish_holes[player][col] and 
                    self.pits[player][col].counters > 0):
                    player_has_counters = True
                    break
            
            if not player_has_counters:
                opponent = 1 - player
                remaining_counters = 0
                
                # Opponent collects remaining from their regular pits
                for col in REGULAR_COLS:
                    if not self.rubbish_holes[opponent][col]:
                        remaining_counters += self.pits[opponent][col].counters
                        self.pits[opponent][col].counters = 0
                self.captures[opponent] += remaining_counters
                
                # Handle Kasi Kuzhi end-of-round collection
                kasi_p1 = self.pits[0][KASI_COL].counters
                kasi_p2 = self.pits[1][KASI_COL].counters
                total_kasi = kasi_p1 + kasi_p2
                
                # Find out which Kasi(s) each player reserved
                res_p1 = [i for i in range(2) if self.kasi_reserved_by[i] == 0]
                res_p2 = [i for i in range(2) if self.kasi_reserved_by[i] == 1]
                
                p1_has_res = len(res_p1) > 0
                p2_has_res = len(res_p2) > 0
                
                kasi_leftover_0 = 0
                kasi_leftover_1 = 0
                
                if total_kasi > 0:
                    if p1_has_res and p2_has_res:
                        # Case 2: Both players reserved Kasi
                        # Combine and share equally; odd seed stays for next round
                        each_share = total_kasi // 2
                        leftover = total_kasi % 2
                        self.captures[0] += each_share
                        self.captures[1] += each_share
                        
                        # When both reserve, the odd seed stays in top Kasi
                        kasi_leftover_0 = leftover
                        
                        self.temporary_message = f"Both reserved Kasi! Shared: P1 gets {each_share}, P2 gets {each_share}" + (f" (1 stays)" if leftover else "")
                        self.message_player = None
                        self.message_timer = 5.0
                    elif p1_has_res and not p2_has_res:
                        # Case 1: Only P1 reserved
                        collected = 0
                        if 0 in res_p1: collected += kasi_p1
                        else: kasi_leftover_0 = kasi_p1
                        
                        if 1 in res_p1: collected += kasi_p2
                        else: kasi_leftover_1 = kasi_p2
                        
                        self.captures[0] += collected
                        carry_msg = " (Unreserved stays)" if (kasi_leftover_0 + kasi_leftover_1) > 0 else ""
                        self.temporary_message = f"P1 collects {collected} from reserved Kasi{carry_msg}"
                        self.message_player = 0
                        self.message_timer = 5.0
                    elif p2_has_res and not p1_has_res:
                        # Case 1: Only P2 reserved
                        collected = 0
                        if 0 in res_p2: collected += kasi_p1
                        else: kasi_leftover_0 = kasi_p1
                        
                        if 1 in res_p2: collected += kasi_p2
                        else: kasi_leftover_1 = kasi_p2
                        
                        self.captures[1] += collected
                        carry_msg = " (Unreserved stays)" if (kasi_leftover_0 + kasi_leftover_1) > 0 else ""
                        self.temporary_message = f"P2 collects {collected} from reserved Kasi{carry_msg}"
                        self.message_player = 1
                        self.message_timer = 5.0
                    else:
                        # Case 3: No one reserved Kasi
                        kasi_leftover_0 = kasi_p1
                        kasi_leftover_1 = kasi_p2
                        self.temporary_message = f"No one reserved Kasi! {total_kasi} seeds carry forward"
                        self.message_player = None
                        self.message_timer = 5.0
                
                # Clear Kasi pits (leftover goes via kasi_leftover_to_pass)
                self.pits[0][KASI_COL].counters = 0
                self.pits[1][KASI_COL].counters = 0
                
                if not self.temporary_message:
                    self.temporary_message = f"Round Over! Player {player + 1} has no moves!"
                    self.message_player = None
                    self.message_timer = 4.0
                
                self.round_ending = True
                self.kasi_leftover_to_pass = [kasi_leftover_0, kasi_leftover_1]
                arcade.schedule(self.delayed_end_round, self.message_timer)
                return True
        
        return False
        
    def delayed_end_round(self, delta_time):
        arcade.unschedule(self.delayed_end_round)
        self.end_round(getattr(self, 'kasi_leftover_to_pass', [0, 0]))

    def end_round(self, kasi_leftover=None):
        if kasi_leftover is None:
            kasi_leftover = [0, 0]
        winner = 1 if self.captures[0] > self.captures[1] else 2
        
        # Check if either player can't fill even 1 pit
        can_continue = True
        for player in range(2):
            if self.captures[player] < self.start_counters:
                can_continue = False
                break
        
        final = (self.current_round >= self.total_rounds) or not can_continue
        
        from .viewScreens import GameOverView
        game_over_view = GameOverView(winner, self.captures, self.total_rounds, 
                                       self.current_round, final,
                                       start_counters=self.start_counters,
                                       ai_mode=self.ai_mode,
                                       ai_difficulty=self.ai_difficulty)
        
        if not final:
            game_over_view.next_round_captures = self.captures[:]
            game_over_view.kasi_leftover = kasi_leftover
        
        self.window.show_view(game_over_view)

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.temporary_message = None
                self.message_player = None

        # Fade pickup pit highlight
        if self.pickup_pit_timer > 0:
            self.pickup_pit_timer -= delta_time
            if self.pickup_pit_timer <= 0:
                self.pickup_pit = None

        if not self.distributing:
            self.check_termination()

        if (self.ai_mode and self.current_player == 1 and 
            not self.distributing and not self.check_termination()):
            arcade.schedule(self.ai_move, 1.0)

    def counters_in_pits(self, row_pits):
        return sum(pit.counters for pit in row_pits)

    # ============ DISTRIBUTION LOGIC ============

    def get_distribution_path(self, row, col, for_player=None):
        """Get counterclockwise path, including own Kasi, skipping opponent's Kasi"""
        if for_player is None:
            for_player = self.current_player
            
        path = []
        r, c = row, col
        
        for _ in range(70):
            if r == 1:
                c += 1
                if c >= COLS:
                    r = 0
                    c = COLS - 1
            else:
                c -= 1
                if c < 0:
                    r = 1
                    c = 0
            
            # Skip rubbish holes
            if self.rubbish_holes[r][c]:
                continue
                
            path.append((r, c))
                
        return path

    def start_distribution(self, pit):
        self.active_counters = pit.counters
        pit.counters = 0
        self.distribution_path = self.get_distribution_path(pit.row, pit.col)
        self.last_row, self.last_col = pit.row, pit.col
        self.distributing = True
        # Highlight the pit seeds were picked from
        self.pickup_pit = (pit.row, pit.col)
        self.pickup_pit_timer = 1.5
        arcade.schedule(self.distribute_step, 0.3)

    def distribute_step(self, delta_time):
        if self.active_counters > 0:
            if not self.distribution_path:
                self.distribution_path = self.get_distribution_path(self.last_row, self.last_col)

            r, c = self.distribution_path.pop(0)
            pit = self.pits[r][c]
            
            self.sowing_pit = (r, c)
            
            # Track if pit was empty before dropping
            was_empty = (pit.counters == 0)
            
            pit.counters += 1
            self.active_counters -= 1
            self.last_row, self.last_col = r, c

            # Check if this is the last counter
            if self.active_counters == 0:
                self.last_pit_was_empty = was_empty

            # Pasu capture - any regular pit reaching exactly 4
            # Kasi Kuzhi is excluded from Pasu
            if pit.counters == 4 and not pit.is_kasi:
                capturing_player = self.current_player
                self.captures[capturing_player] += 4
                pit.counters = 0
                self.temporary_message = f"Player {capturing_player + 1} got Pasu! +4 from pit {pit.col + 1}"
                self.message_player = capturing_player
                self.message_timer = 3.0

        else:
            # All counters distributed - check capture or continuation
            self.sowing_pit = None
            
            r, c = self.last_row, self.last_col
            last_pit = self.pits[r][c]
            
            # CAPTURE RULE: next pit is empty (traditional THUDAKKAM)
            next_path = self.get_distribution_path(r, c)
            if not next_path:
                self.end_turn()
                return
            
            next_r, next_c = next_path[0]
            next_pit = self.pits[next_r][next_c]
            
            if next_pit.counters == 0:
                if len(next_path) > 1:
                    beyond_r, beyond_c = next_path[1]
                    beyond_pit = self.pits[beyond_r][beyond_c]
                    
                    captured = 0
                    msg_parts = []
                    
                    if beyond_pit.is_kasi:
                        # KASI RESERVATION RULE
                        self.kasi_reserved_by[beyond_r] = self.current_player
                        self.temporary_message = f"P{self.current_player + 1} reserved Top Kasi!" if beyond_r == 0 else f"P{self.current_player + 1} reserved Bottom Kasi!"
                        self.message_player = self.current_player
                        self.message_timer = 4.0
                    else:
                        if beyond_pit.counters > 0:
                            captured += beyond_pit.counters
                            msg_parts.append(f"{beyond_pit.counters} from P{beyond_r+1} pit {beyond_c+1} (beyond empty)")
                            beyond_pit.counters = 0
                            
                        opp_r = 1 - beyond_r
                        opp_c = beyond_c
                        opp_pit = self.pits[opp_r][opp_c]
                        
                        if not opp_pit.is_kasi and not self.rubbish_holes[opp_r][opp_c] and opp_pit.counters > 0:
                            captured += opp_pit.counters
                            msg_parts.append(f"{opp_pit.counters} from P{opp_r+1} pit {opp_c+1} (opposite)")
                            opp_pit.counters = 0
                        
                        if captured > 0:
                            self.captures[self.current_player] += captured
                            self.temporary_message = f"P{self.current_player + 1} captured: " + " + ".join(msg_parts)
                            self.message_player = self.current_player
                            self.message_timer = 5.0
                
                self.end_turn()
                return
            
            # CONTINUATION RULE: check next non-Kasi pit
            next_idx = 0
            while next_idx < len(next_path):
                nr, nc = next_path[next_idx]
                if self.pits[nr][nc].is_kasi:
                    next_idx += 1
                    continue
                break
            
            if next_idx >= len(next_path):
                self.end_turn()
                return
            
            nr, nc = next_path[next_idx]
            npit = self.pits[nr][nc]
            
            if npit.counters > 0:
                # Continue: pick up from next pit and keep distributing
                self.active_counters = npit.counters
                npit.counters = 0
                self.last_row, self.last_col = nr, nc
                self.distribution_path = self.get_distribution_path(nr, nc)
                # Highlight the continuation pickup pit
                self.pickup_pit = (nr, nc)
                self.pickup_pit_timer = 2.0
                # Brief pause so user can see which pit seeds were taken from
                arcade.unschedule(self.distribute_step)
                arcade.schedule(self.distribute_step, 0.5)
            else:
                self.end_turn()

    def end_turn(self):
        arcade.unschedule(self.distribute_step)
        self.distributing = False
        self.sowing_pit = None
        self.selected_pit = None
        self.pickup_pit = None
        self.pickup_pit_timer = 0
        self.current_player = 1 - self.current_player
        self.check_termination()

    # ============ INPUT HANDLING ============

    def on_mouse_motion(self, x, y, dx, dy):
        self.highlighted_pit = None
        
        if self.distributing or (self.ai_mode and self.current_player == 1):
            return
            
        for i, row_pit in enumerate(self.pits):
            for col in range(COLS):
                pit = row_pit[col]
                if self.rubbish_holes[pit.row][pit.col]:
                    continue
                # Cannot start from Kasi Kuzhi
                if pit.is_kasi:
                    continue
                    
                dist = math.sqrt((x - pit.x) ** 2 + (y - pit.y) ** 2)
                if dist <= PIT_RADIUS and pit.counters > 0 and i == self.current_player:
                    self.highlighted_pit = (pit.row, pit.col)
                    return

    def on_mouse_press(self, x, y, button, modifiers):
        if self.distributing:
            return
        if self.ai_mode and self.current_player == 1:
            return
        if self.check_termination():
            return
        
        for i, row_pit in enumerate(self.pits):
            for col in range(COLS):
                pit = row_pit[col]
                if self.rubbish_holes[pit.row][pit.col]:
                    continue
                # Cannot start from Kasi Kuzhi
                if pit.is_kasi:
                    continue
                    
                dist = math.sqrt((x - pit.x) ** 2 + (y - pit.y) ** 2)
                if dist <= PIT_RADIUS:
                    if pit.counters > 0 and i == self.current_player:
                        self.selected_pit = (pit.row, pit.col)
                        self.start_distribution(pit)
                    return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from .viewScreens import WelcomeView
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)

    # ============ AI LOGIC ============

    def ai_move(self, delta_time):
        arcade.unschedule(self.ai_move)
        
        if self.check_termination():
            return
        
        valid_moves = []
        for col in REGULAR_COLS:
            if (self.pits[1][col].counters > 0 and 
                not self.rubbish_holes[1][col]):
                valid_moves.append(col)
        
        if not valid_moves:
            self.check_termination()
            return

        if self.ai_difficulty == AI_EASY:
            best_move = self.easy_ai(valid_moves)
        elif self.ai_difficulty == AI_MEDIUM:
            best_move = self.medium_ai(valid_moves)
        else:
            best_move = self.hard_ai(valid_moves)
        
        if best_move is not None:
            pit = self.pits[1][best_move]
            self.selected_pit = (pit.row, pit.col)
            self.start_distribution(pit)

    def easy_ai(self, valid_moves):
        moves_with_scores = []
        for col in valid_moves:
            score = self.evaluate_move(col)
            moves_with_scores.append((col, score))
        
        moves_with_scores.sort(key=lambda x: x[1])
        
        if random.random() < 0.7 and len(moves_with_scores) > 1:
            half = len(moves_with_scores) // 2
            return random.choice(moves_with_scores[:half])[0]
        else:
            return random.choice(valid_moves)

    def medium_ai(self, valid_moves):
        best_score = -999
        good_moves = []
        
        for col in valid_moves:
            score = self.evaluate_move(col)
            if score > best_score:
                best_score = score
                good_moves = [col]
            elif score == best_score:
                good_moves.append(col)
        
        if len(good_moves) > 1 and random.random() < 0.2:
            return random.choice(good_moves[1:])
        else:
            return random.choice(good_moves)

    def hard_ai(self, valid_moves):
        best_score = -float('inf')
        best_moves = []
        alpha = -float('inf')
        beta = float('inf')
        
        for col in valid_moves:
            state = self.get_game_state()
            new_state, extra_turn = self.simulate_move_state(state, col, 1)
            
            if extra_turn:
                score = self.minimax(new_state, 2, alpha, beta, True, 1)
            else:
                score = self.minimax(new_state, 2, alpha, beta, False, 1)
            
            if score > best_score:
                best_score = score
                best_moves = [col]
            elif score == best_score:
                best_moves.append(col)
            
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        
        return random.choice(best_moves) if best_moves else valid_moves[0]

    def minimax(self, state, depth, alpha, beta, maximizing_player, current_player):
        pits, captures, rubbish_holes = state
        
        if depth == 0 or self.is_terminal_state(pits, rubbish_holes, current_player):
            return self.evaluate_state(state, 1)
        
        valid_moves = self.get_valid_moves(pits, rubbish_holes, current_player)
        
        if not valid_moves:
            if self.is_terminal_state(pits, rubbish_holes, 1 - current_player):
                return self.evaluate_state(state, 1)
            else:
                return self.minimax(state, depth - 1, alpha, beta, not maximizing_player, 1 - current_player)
        
        if maximizing_player:
            max_eval = -float('inf')
            for col in valid_moves:
                new_state, extra_turn = self.simulate_move_state(state, col, current_player)
                if extra_turn:
                    eval = self.minimax(new_state, depth - 1, alpha, beta, True, current_player)
                else:
                    eval = self.minimax(new_state, depth - 1, alpha, beta, False, 1 - current_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                new_state, extra_turn = self.simulate_move_state(state, col, current_player)
                if extra_turn:
                    eval = self.minimax(new_state, depth - 1, alpha, beta, False, current_player)
                else:
                    eval = self.minimax(new_state, depth - 1, alpha, beta, True, 1 - current_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_game_state(self):
        pits = [[self.pits[row][col].counters for col in range(COLS)] for row in range(ROWS)]
        captures = self.captures.copy()
        rubbish_holes = copy.deepcopy(self.rubbish_holes)
        return (pits, captures, rubbish_holes)

    def simulate_move_state(self, state, col, player):
        """Simulate a complete move with continuation and return new state"""
        pits, captures, rubbish_holes = copy.deepcopy(state)
        row = player
        
        counters = pits[row][col]
        pits[row][col] = 0
        current_row, current_col = row, col
        
        # Full simulation loop (distribution + continuation)
        while True:
            last_was_empty = False
            
            # Distribute counters
            for _ in range(counters):
                # Move to next pit (counterclockwise)
                if current_row == 1:
                    current_col += 1
                    if current_col >= COLS:
                        current_row = 0
                        current_col = COLS - 1
                else:
                    current_col -= 1
                    if current_col < 0:
                        current_row = 1
                        current_col = 0
                
                # Skip rubbish holes
                if rubbish_holes[current_row][current_col]:
                    continue
                    
                # Pasu capture during distribution (not for Kasi)
                if pits[current_row][current_col] == 4 and current_col != KASI_COL:
                    capturing_player = player
                    captures[capturing_player] += 4
                    pits[current_row][current_col] = 0
            
            last_row, last_col = current_row, current_col
            
            # Get next path for simulation
            next_path = self.get_simulation_path(last_row, last_col, rubbish_holes, player)
            if not next_path:
                break
                
            next_r, next_c = next_path[0]
            
            # Check capture: next pit is empty
            if pits[next_r][next_c] == 0:
                if len(next_path) > 1:
                    beyond_r, beyond_c = next_path[1]
                    
                    captured = 0
                    if beyond_c == KASI_COL:
                        pass # AI ignores reserving Kasi Kuzhi for simplicity
                    else:
                        if pits[beyond_r][beyond_c] > 0:
                            captured += pits[beyond_r][beyond_c]
                            pits[beyond_r][beyond_c] = 0
                            
                        opp_r = 1 - beyond_r
                        opp_c = beyond_c
                        if not rubbish_holes[opp_r][opp_c] and pits[opp_r][opp_c] > 0:
                            captured += pits[opp_r][opp_c]
                            pits[opp_r][opp_c] = 0
                        
                        captures[player] += captured
                break  # Turn ends
            
            # Continuation
            next_idx = 0
            while next_idx < len(next_path):
                nr, nc = next_path[next_idx]
                if nc == KASI_COL:
                    next_idx += 1
                    continue
                break
            
            if next_idx >= len(next_path):
                break
            
            nr, nc = next_path[next_idx]
            if pits[nr][nc] == 0:
                break
            
            # Continue: pick up from next pit
            counters = pits[nr][nc]
            pits[nr][nc] = 0
            current_row, current_col = nr, nc
        
        return (pits, captures, rubbish_holes), False

    def get_simulation_path(self, start_row, start_col, rubbish_holes, player):
        path = []
        r, c = start_row, start_col
        
        for _ in range(COLS * 2):
            if r == 1:
                c += 1
                if c >= COLS:
                    r = 0
                    c = COLS - 1
            else:
                c -= 1
                if c < 0:
                    r = 1
                    c = 0
            
            if rubbish_holes[r][c]:
                continue
                
            path.append((r, c))
        
        return path

    def get_valid_moves(self, pits, rubbish_holes, player):
        valid_moves = []
        for col in REGULAR_COLS:
            if pits[player][col] > 0 and not rubbish_holes[player][col]:
                valid_moves.append(col)
        return valid_moves

    def is_terminal_state(self, pits, rubbish_holes, player):
        for col in REGULAR_COLS:
            if not rubbish_holes[player][col] and pits[player][col] > 0:
                return False
        return True

    def evaluate_state(self, state, ai_player):
        pits, captures, rubbish_holes = state
        opponent = 1 - ai_player
        
        score = 0
        score += (captures[ai_player] - captures[opponent]) * 1000
        
        ai_pit_counters = sum(pits[ai_player][c] for c in REGULAR_COLS)
        opponent_pit_counters = sum(pits[opponent][c] for c in REGULAR_COLS)
        score += (ai_pit_counters - opponent_pit_counters) * 10
        
        ai_mobility = sum(1 for col in REGULAR_COLS 
                         if not rubbish_holes[ai_player][col] and pits[ai_player][col] > 0)
        opponent_mobility = sum(1 for col in REGULAR_COLS 
                              if not rubbish_holes[opponent][col] and pits[opponent][col] > 0)
        score += (ai_mobility - opponent_mobility) * 5
        
        # Kasi seeds are shared so worth less
        score += pits[ai_player][KASI_COL] * 3
        
        return score

    def evaluate_move(self, col):
        score = 0
        row = 1
        score += self.pits[row][col].counters * 10
        
        counters = self.pits[row][col].counters
        current_row, current_col = row, col

        for i in range(counters):
            if current_row == 1:
                current_col += 1
                if current_col >= COLS:
                    current_row = 0
                    current_col = COLS - 1
            else:
                current_col -= 1
                if current_col < 0:
                    current_row = 1
                    current_col = 0
            
            if self.rubbish_holes[current_row][current_col]:
                continue
                
            # Traditional Thudakkam Capture Potential
            # Approximate by checking if next pit is empty
            next_r = current_row
            next_c = current_col
            if next_r == 1:
                next_c += 1
                if next_c >= COLS:
                    next_r = 0
                    next_c = COLS - 1
            else:
                next_c -= 1
                if next_c < 0:
                    next_r = 1
                    next_c = 0
                    
            if not self.rubbish_holes[next_r][next_c] and self.pits[next_r][next_c].counters == 0:
                # Capture potential from beyond and opposite
                beyond_r = next_r
                beyond_c = next_c
                if beyond_r == 1:
                    beyond_c += 1
                    if beyond_c >= COLS:
                        beyond_r = 0
                        beyond_c = COLS - 1
                else:
                    beyond_c -= 1
                    if beyond_c < 0:
                        beyond_r = 1
                        beyond_c = 0
                
                if not self.rubbish_holes[beyond_r][beyond_c] and beyond_c != KASI_COL:
                    score += self.pits[beyond_r][beyond_c].counters * 15
                    opp_r = 1 - beyond_r
                    opp_c = beyond_c
                    if not self.rubbish_holes[opp_r][opp_c] and opp_c != KASI_COL:
                        score += self.pits[opp_r][opp_c].counters * 15
        
        return score
