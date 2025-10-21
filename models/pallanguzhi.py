from .constants import *
from .pit import Pit
import arcade
import random
import copy
import math


class Pallanguzhi(arcade.View):
    def __init__(self, ai_mode=False, ai_level=AI_MEDIUM):
        super().__init__()
        arcade.set_background_color(BOARD_COLOR)
        self.ai_mode = ai_mode
        self.ai_level = ai_level

        # Create 2D grid of pits
        self.pits = []
        spacing_x = (SCREEN_WIDTH - 220) // (COLS + 1)
        spacing_y = (SCREEN_HEIGHT - 80) // (ROWS + 1)

        for row in range(ROWS):
            row_pits = []
            for col in range(COLS):
                x = 200 + (col + 1) * spacing_x
                y = SCREEN_HEIGHT - 60 - (row + 1) * spacing_y
                row_pits.append(Pit(row, col, x, y))
            self.pits.append(row_pits)

        # stores for each player
        self.captures = [0, 0]

        # Turn and distribution state
        self.current_player = 0  # 0 = top row, 1 = bottom row
        self.distributing = False
        # animation distribution state
        self.active_beads = 0
        self.distribution_idx = None
        self.distribution_last_pos = None
        self.message = None
        self.message_timer = 0.0
        self.hovered = None
        self.hand_animation = None  # placeholder timer for hand animation

        # Precompute circle order: top row left->right, store0 (owner 0), bottom row right->left, store1 (owner1)
        self.circle = []
        for c in range(COLS):
            self.circle.append(('pit', 0, c))
        self.circle.append(('store', 0, None))
        for c in reversed(range(COLS)):
            self.circle.append(('pit', 1, c))
        self.circle.append(('store', 1, None))

    def on_draw(self):
        self.clear()
        # Draw pits
        for row in self.pits:
            for pit in row:
                pit.draw()

        # Draw stores (bowls)
        arcade.draw_circle_filled(100, SCREEN_HEIGHT - 50, PIT_RADIUS + 10, CAPTURE_COLOR)
        arcade.draw_text(f"P1: {self.captures[0]}", 70, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
        arcade.draw_circle_filled(100, 50, PIT_RADIUS + 10, CAPTURE_COLOR)
        arcade.draw_text(f"P2: {self.captures[1]}", 70, 40, arcade.color.WHITE, 16)

        # Turn info
        turn_text = "Your Turn" if (not self.ai_mode and self.current_player == 1) else f"Player {self.current_player + 1}'s turn"
        if self.ai_mode:
            turn_text = "Your Turn" if self.current_player == 0 else "AI's Turn"
        arcade.draw_text(turn_text, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18)

        # message
        if self.message and self.message_timer > 0:
            arcade.draw_text(self.message, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16, anchor_x="center")

    def set_message(self, txt, duration=2.5):
        self.message = txt
        self.message_timer = duration

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = None

        # run AI move if needed
        if self.ai_mode and self.current_player == 1 and not self.distributing:
            # schedule AI think delay then perform move
            arcade.schedule(self._ai_make_move, AI_THINK_DELAY)
            self.distributing = True  # block user input until scheduled

    def counters_in_pits(self, row_pits):
        return sum(p.counters for p in row_pits)

    def on_mouse_motion(self, x, y, dx, dy):
        # highlight valid pits for hovering
        for row in self.pits:
            for pit in row:
                pit.highlight = False
        for pit in self.pits[self.current_player]:
            dist = math.hypot(x - pit.x, y - pit.y)
            if dist <= PIT_RADIUS and pit.counters > 0 and (not (self.ai_mode and self.current_player == 1)):
                pit.highlight = True

    def on_mouse_press(self, x, y, button, modifiers):
        if self.distributing:
            return
        # check click on pits for current player
        for pit in self.pits[self.current_player]:
            dist = math.hypot(x - pit.x, y - pit.y)
            if dist <= PIT_RADIUS and pit.counters > 0:
                self._player_move(pit.row, pit.col)
                return

    def _index_of(self, pos):
        # pos is ('pit',row,col) or ('store',owner,None)
        for i, p in enumerate(self.circle):
            if p == pos:
                return i
        return None

    def _player_move(self, row, col):
        # start sowing from selected pit
        if self.pits[row][col].counters == 0:
            return
        # Begin animated distribution: schedule per-bead drops
        beads = self.pits[row][col].counters
        self.pits[row][col].counters = 0
        self.active_beads = beads
        start_pos = ('pit', row, col)
        self.distribution_idx = self._index_of(start_pos)
        self.distribution_last_pos = None
        self.distributing = True
        arcade.schedule(self._distribute_step, 0.12)

    def _distribute_step(self, delta_time):
        # drop one bead per scheduled tick
        if self.active_beads > 0:
            # advance index to next valid position
            while True:
                self.distribution_idx = (self.distribution_idx + 1) % len(self.circle)
                p = self.circle[self.distribution_idx]
                # skip opponent's store
                if p[0] == 'store' and p[1] != self.current_player:
                    continue
                break

            # apply bead to pit or store
            if p[0] == 'pit':
                self.pits[p[1]][p[2]].counters += 1
            else:
                self.captures[p[1]] += 1

            self.distribution_last_pos = p
            self.active_beads -= 1
            return

        # active_beads == 0 -> finalize distribution
        arcade.unschedule(self._distribute_step)
        last_pos = self.distribution_last_pos
        # If last landed in own store -> extra turn (do not switch)
        if last_pos and last_pos[0] == 'store' and last_pos[1] == self.current_player:
            self.set_message("Extra turn!", 1.8)
            self.distributing = False
            self._check_end_condition()
            return

        # If last landed in own empty pit -> capture own + opposite
        if last_pos and last_pos[0] == 'pit':
            r, c = last_pos[1], last_pos[2]
            pit = self.pits[r][c]
            if r == self.current_player and pit.counters == 1:
                opp = self.pits[1 - r][COLS - 1 - c]
                if opp.counters > 0:
                    captured = opp.counters + pit.counters
                    opp.counters = 0
                    pit.counters = 0
                    self.captures[self.current_player] += captured
                    self.set_message(f"Captured {captured} beads!", 2.5)
                    self.distributing = False
                    # switch turn after capture
                    self.current_player = 1 - self.current_player
                    self._check_end_condition()
                    return

        # otherwise switch turn
        self.distributing = False
        self.current_player = 1 - self.current_player
        self._check_end_condition()

    def _check_end_condition(self):
        top_sum = self.counters_in_pits(self.pits[0])
        bot_sum = self.counters_in_pits(self.pits[1])
        if top_sum == 0 or bot_sum == 0:
            # collect remaining into respective store
            self.captures[0] += top_sum
            self.captures[1] += bot_sum
            for pit in self.pits[0]:
                pit.counters = 0
            for pit in self.pits[1]:
                pit.counters = 0
            # determine winner
            winner = 1 if self.captures[0] > self.captures[1] else 2
            from .viewScreens import GameOverView
            game_over = GameOverView(winner, self.captures)
            self.window.show_view(game_over)

    # ---------------- AI ----------------
    def _ai_make_move(self, delta_time):
        arcade.unschedule(self._ai_make_move)
        self.distributing = False
        # pick move based on difficulty (use medium heuristic for now)
        valid_moves = [c for c in range(COLS) if self.pits[1][c].counters > 0]
        if not valid_moves:
            self._check_end_condition()
            return

        # choose based on ai_level
        if self.ai_level == AI_EASY:
            choice = random.choice(valid_moves)
        elif self.ai_level == AI_MEDIUM:
            best_score = -999
            choice = random.choice(valid_moves)
            for col in valid_moves:
                score = self._simulate_move_score(1, col)
                if score > best_score:
                    best_score = score
                    choice = col
        else:  # AI_HARD: use minimax with alpha-beta
            # prepare compact board representation: pits as 2xCOLS ints and stores
            board_pits = [[self.pits[r][c].counters for c in range(COLS)] for r in range(ROWS)]
            stores = [self.captures[0], self.captures[1]]
            ai_player = 1
            depth = 6  # adjust for strength/performance
            best_score = -10**9
            choice = random.choice(valid_moves)
            alpha = -10**9
            beta = 10**9
            for col in valid_moves:
                new_pits, new_stores, next_player = self._simulate_move_state(board_pits, stores, ai_player, col)
                # if terminal, evaluate directly
                score = self._minimax(new_pits, new_stores, next_player, depth - 1, alpha, beta, ai_player)
                if score > best_score:
                    best_score = score
                    choice = col
                    alpha = max(alpha, best_score)

        # perform AI move
        self._player_move(1, choice)

    def _simulate_move_state(self, pits, stores, player, col):
        """Simulate move on simple arrays. Return (new_pits, new_stores, next_player)."""
        # copy state
        new_pits = [row[:] for row in pits]
        new_stores = stores[:]
        beads = new_pits[player][col]
        new_pits[player][col] = 0
        # build circle positions same as self.circle
        circle = []
        for c in range(COLS):
            circle.append(('pit', 0, c))
        circle.append(('store', 0, None))
        for c in reversed(range(COLS)):
            circle.append(('pit', 1, c))
        circle.append(('store', 1, None))
        # find start idx
        start = ('pit', player, col)
        idx = 0
        for i,p in enumerate(circle):
            if p == start:
                idx = i
                break
        last = None
        while beads > 0:
            idx = (idx + 1) % len(circle)
            p = circle[idx]
            # skip opponent's store
            if p[0] == 'store' and p[1] != player:
                continue
            if p[0] == 'pit':
                new_pits[p[1]][p[2]] += 1
            else:
                new_stores[p[1]] += 1
            last = p
            beads -= 1

        # check terminal
        top_sum = sum(new_pits[0])
        bot_sum = sum(new_pits[1])
        if top_sum == 0 or bot_sum == 0:
            # collect remainders
            new_stores[0] += top_sum
            new_stores[1] += bot_sum
            for r in range(ROWS):
                for c in range(COLS):
                    new_pits[r][c] = 0
            # no next player matter; return next_player as -1 to indicate terminal
            return new_pits, new_stores, -1

        # resolve capture / extra turn
        if last and last[0] == 'store' and last[1] == player:
            next_player = player  # extra turn
        else:
            next_player = 1 - player
            # capture rule: last landed in own empty pit (now has 1) and opposite has >0
            if last and last[0] == 'pit':
                r, c = last[1], last[2]
                if r == player and new_pits[r][c] == 1:
                    opp = new_pits[1 - r][COLS - 1 - c]
                    if opp > 0:
                        captured = opp + new_pits[r][c]
                        new_stores[player] += captured
                        new_pits[1 - r][COLS - 1 - c] = 0
                        new_pits[r][c] = 0
        return new_pits, new_stores, next_player

    def _evaluate_state(self, pits, stores, ai_player):
        """Heuristic evaluation from ai_player perspective (higher = better for AI)."""
        opp = 1 - ai_player
        score = 0
        # primary: store difference
        score += (stores[ai_player] - stores[opp]) * 1000
        # secondary: mobility (non-empty pits)
        score += (sum(1 for x in pits[ai_player] if x>0) - sum(1 for x in pits[opp] if x>0)) * 30
        # potential captures: if a move would land in empty own pit with opposite beads
        potential = 0
        for col in range(COLS):
            b = pits[ai_player][col]
            if b == 0:
                continue
            # simulate landing index quickly
            # compute landing position by walking circle length b skipping opponent store
            circle_len = 2*COLS + 2
            idx = 0
            # start pos index
            # build circle once locally to compute landing
        # approximate board_balance: favor more beads on AI side
        score += (sum(pits[ai_player]) - sum(pits[opp])) * 5
        return score

    def _minimax(self, pits, stores, player, depth, alpha, beta, ai_player):
        """Alpha-beta minimax. Returns score from ai_player perspective."""
        # terminal check or depth limit
        if player == -1:
            # terminal: evaluate directly
            return self._evaluate_state(pits, stores, ai_player)
        if depth <= 0:
            return self._evaluate_state(pits, stores, ai_player)

        valid_moves = [c for c in range(COLS) if pits[player][c] > 0]
        if not valid_moves:
            # no moves => terminal-like
            return self._evaluate_state(pits, stores, ai_player)

        if player == ai_player:
            value = -10**9
            for col in valid_moves:
                new_pits, new_stores, next_player = self._simulate_move_state(pits, stores, player, col)
                val = self._minimax(new_pits, new_stores, next_player, depth - 1, alpha, beta, ai_player)
                if val > value:
                    value = val
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            # opponent minimizes AI score
            value = 10**9
            for col in valid_moves:
                new_pits, new_stores, next_player = self._simulate_move_state(pits, stores, player, col)
                val = self._minimax(new_pits, new_stores, next_player, depth - 1, alpha, beta, ai_player)
                if val < value:
                    value = val
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

