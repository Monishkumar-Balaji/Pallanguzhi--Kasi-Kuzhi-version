from .constants import *
from .pit import Pit
import arcade
import math
import random
import copy


class Pallanguzhi(arcade.View):
    def __init__(self, ai_mode=False, total_rounds=3, current_round=1, previous_captures=None):
        super().__init__()
        arcade.set_background_color(BOARD_COLOR)
        self.ai_mode = ai_mode
        self.total_rounds = total_rounds
        self.current_round = current_round

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
        self.captures = previous_captures if previous_captures else [0, 0]
        self.temporary_message = None
        self.message_timer = 0
        
        # Animation and highlighting
        self.highlighted_pit = None
        self.selected_pit = None
        self.sowing_pit = None
        
        # Rubbish holes
        self.rubbish_holes = [[False] * COLS for _ in range(ROWS)]
        
        # Initialize pits for new round
        self.initialize_round()

    def initialize_round(self):
        """Initialize pits for the current round"""
        if self.current_round == 1:
            # First round - all pits get 5 counters
            for row in range(ROWS):
                for col in range(COLS):
                    self.pits[row][col].counters = START_COUNTERS
                    self.rubbish_holes[row][col] = False
        else:
            # Subsequent rounds
            for row in range(ROWS):
                for col in range(COLS):
                    self.rubbish_holes[row][col] = False
                    self.pits[row][col].counters = 0
            
            # Calculate how many pits each player can fill
            for player in range(2):
                pits_to_fill = self.captures[player] // START_COUNTERS
                pits_to_fill = min(pits_to_fill, COLS)
                
                # Fill the pits for this player
                for col in range(pits_to_fill):
                    self.pits[player][col].counters = START_COUNTERS
                    self.captures[player] -= START_COUNTERS
                
                # Mark remaining pits as rubbish holes
                for col in range(pits_to_fill, COLS):
                    self.rubbish_holes[player][col] = True

    def on_draw(self):
        self.clear()

        # Draw pits
        for row in self.pits:
            for pit in row:
                is_hover = (self.highlighted_pit == (pit.row, pit.col))
                is_selected = (self.selected_pit == (pit.row, pit.col))
                is_sowing = (self.sowing_pit == (pit.row, pit.col))
                
                pit.draw(highlight_type="hover" if is_hover else 
                        "selected" if is_selected else 
                        "sowing" if is_sowing else None,
                        is_rubbish=self.rubbish_holes[pit.row][pit.col])

        # Draw bowls
        arcade.draw_circle_filled(100, SCREEN_HEIGHT - 50, PIT_RADIUS, CAPTURE_COLOR)
        arcade.draw_text(f"P1: {self.captures[0]}", 70, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

        arcade.draw_circle_filled(100, 50, PIT_RADIUS, CAPTURE_COLOR)
        arcade.draw_text(f"P2: {self.captures[1]}", 70, 40, arcade.color.WHITE, 16)

        # Round and turn info
        arcade.draw_text(f"Round {self.current_round}/{self.total_rounds}", 
                        SCREEN_WIDTH - 200, SCREEN_HEIGHT - 60, arcade.color.WHITE, 14)
        
        if self.ai_mode and self.current_player == 1:
            turn_text = "AI's turn"
        else:
            turn_text = f"Player {self.current_player + 1}'s turn"
        arcade.draw_text(turn_text, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18)

        # Draw temporary message if active
        if self.temporary_message and self.message_timer > 0:
            # Determine message position based on which player the message is about
            message_y = SCREEN_HEIGHT - 50  # Default top position for Player 1
            
            # Check if message is about Player 2
            if "Player 2" in self.temporary_message:
                message_y = 50  # Bottom position for Player 2
            
            arcade.draw_text(
                self.temporary_message,
                SCREEN_WIDTH // 2,
                message_y,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )

    def check_termination(self):
        """Check if the round should end - when ANY player has no counters in their pits"""
        # Only check termination when not distributing (after a move is complete)
        if self.distributing:
            return False
            
        # Check if any player has no counters in their non-rubbish pits
        for player in range(2):
            player_has_counters = False
            for col in range(COLS):
                if (not self.rubbish_holes[player][col] and 
                    self.pits[player][col].counters > 0):
                    player_has_counters = True
                    break
            
            # If any player has no counters, round ends immediately
            if not player_has_counters:
                # The player with counters gets all remaining counters
                opponent = 1 - player
                remaining_counters = 0
                
                # Collect all remaining counters from both sides
                for row in range(ROWS):
                    for col in range(COLS):
                        if not self.rubbish_holes[row][col]:
                            remaining_counters += self.pits[row][col].counters
                            self.pits[row][col].counters = 0
                
                # Add remaining counters to opponent's captures
                self.captures[opponent] += remaining_counters
                self.temporary_message = f"Player {player + 1} has no moves! Player {opponent + 1} collects {remaining_counters} counters!"
                self.message_timer = 3.0
                self.end_round()
                return True
        
        return False

    def end_round(self):
        winner = 1 if self.captures[0] > self.captures[1] else 2
        final = (self.current_round >= self.total_rounds)
        
        from .viewScreens import GameOverView
        game_over_view = GameOverView(winner, self.captures, self.total_rounds, self.current_round, final)
        
        if not final:
            game_over_view.next_round_captures = self.captures[:]
        
        self.window.show_view(game_over_view)

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.temporary_message = None

        # Only check termination when not in the middle of a move
        if not self.distributing:
            self.check_termination()

        # AI move - only if game hasn't terminated and not distributing
        if (self.ai_mode and self.current_player == 1 and 
            not self.distributing and not self.check_termination()):
            arcade.schedule(self.ai_move, 1.0)

    def counters_in_pits(self, row_pits):
        return sum(pit.counters for pit in row_pits)

    def ai_move(self, delta_time):
        arcade.unschedule(self.ai_move)
        
        # Check again if game should terminate
        if self.check_termination():
            return
        
        valid_moves = []
        for col in range(COLS):
            if (self.pits[1][col].counters > 0 and 
                not self.rubbish_holes[1][col]):
                valid_moves.append(col)
        
        if not valid_moves:
            self.check_termination()
            return

        best_move = None
        best_score = -1
        
        for col in valid_moves:
            score = self.evaluate_move(col)
            if score > best_score:
                best_score = score
                best_move = col
        
        if best_move is not None:
            pit = self.pits[1][best_move]
            self.selected_pit = (pit.row, pit.col)
            self.start_distribution(pit)

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
                
            if 1 == 4:  # Simplified pasu check
                score += 40
        
        if current_row == 1:
            score += 20
        
        return score

    def on_mouse_motion(self, x, y, dx, dy):
        self.highlighted_pit = None
        
        if self.distributing or (self.ai_mode and self.current_player == 1):
            return
            
        for i, row_pit in enumerate(self.pits):
            for col in range(COLS):
                pit = row_pit[col]
                if self.rubbish_holes[pit.row][pit.col]:
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
        
        # Check if round should end before processing click
        if self.check_termination():
            return
        
        for i, row_pit in enumerate(self.pits):
            for col in range(COLS):
                pit = row_pit[col]
                if self.rubbish_holes[pit.row][pit.col]:
                    continue
                    
                dist = math.sqrt((x - pit.x) ** 2 + (y - pit.y) ** 2)
                if dist <= PIT_RADIUS:
                    if pit.counters > 0 and i == self.current_player:
                        self.selected_pit = (pit.row, pit.col)
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
            
            if not self.rubbish_holes[r][c]:
                path.append((r, c))
                
        return path

    def distribute_step(self, delta_time):
        if self.active_counters > 0:
            if not self.distribution_path:
                self.distribution_path = self.get_distribution_path(self.last_row, self.last_col)

            r, c = self.distribution_path.pop(0)
            pit = self.pits[r][c]
            
            self.sowing_pit = (r, c)
            
            pit.counters += 1
            self.active_counters -= 1
            self.last_row, self.last_col = r, c

            # Pasu capture - any pit reaching exactly 4
            # The capture goes to the player who OWNS the pit, not the distributing player
            if pit.counters == 4:
                capturing_player = pit.row  # The owner of the pit gets the capture
                self.captures[capturing_player] += 4
                pit.counters = 0
                self.temporary_message = f"Player {capturing_player + 1} got Pasu capture! +4 counters from P{capturing_player + 1}'s pit {c+1}"
                self.message_timer = 3.0

        else:
            self.sowing_pit = None
            
            r, c = self.last_row, self.last_col
            next_path = self.get_distribution_path(r, c)
            
            if not next_path:
                self.end_turn()
                return
                
            next_r, next_c = next_path[0]
            next_pit = self.pits[next_r][next_c]

            # Standard capture
            if next_pit.counters == 0 and len(next_path) > 1:
                beyond_index = 1
                while beyond_index < len(next_path):
                    beyond_r, beyond_c = next_path[beyond_index]
                    beyond_pit = self.pits[beyond_r][beyond_c]
                    if not self.rubbish_holes[beyond_r][beyond_c]:
                        break
                    beyond_index += 1
                
                if beyond_index < len(next_path) and beyond_pit.counters > 0:
                    self.captures[self.current_player] += beyond_pit.counters
                    self.temporary_message =f"Player {self.current_player + 1} collected {beyond_pit.counters} counters from P{beyond_pit.row + 1}'s pit {beyond_pit.col + 1}!"
                    self.message_timer = 4.0
                    beyond_pit.counters = 0

            # Check if next two pits are empty
            empty_count = 0
            for i in range(min(2, len(next_path))):
                check_r, check_c = next_path[i]
                if (not self.rubbish_holes[check_r][check_c] and 
                    self.pits[check_r][check_c].counters == 0):
                    empty_count += 1
                else:
                    break
            
            if empty_count >= 2:
                self.end_turn()
                return

            if next_pit.counters > 0:
                self.active_counters = next_pit.counters
                next_pit.counters = 0
                self.last_row, self.last_col = next_r, next_c
                self.distribution_path = self.get_distribution_path(next_r, next_c)
            else:
                self.distribution_path.pop(0)

    def end_turn(self):
        """End the current player's turn and switch to next player"""
        arcade.unschedule(self.distribute_step)
        self.distributing = False
        self.sowing_pit = None
        self.selected_pit = None  # Clear selected pit highlight when turn ends
        self.current_player = 1 - self.current_player
        # Check termination after turn ends
        self.check_termination()