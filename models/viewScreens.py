import arcade
from .constants import *
import random
import time
import math  # used for title animation

# ---------------- Welcome Screen ---------------- #
class WelcomeView(arcade.View):
	def __init__(self):
		super().__init__()
		self.title_angle = 0.0
		# simple buttons: each item is (label, rect)
		self.buttons = []
		self._create_buttons()
		# try to load music; ignore if missing
		try:
			self.music = arcade.load_sound(MUSIC_FILE)
		except Exception:
			self.music = None

	def _create_buttons(self):
		w = 220
		h = 40
		cx = SCREEN_WIDTH // 2
		start_y = SCREEN_HEIGHT//2 + 40
		# Removed "Gameplay Setup" — keep One vs One, One vs AI and How to Play
		labels = [("🎭 One vs One", False), ("🤖 One vs AI", True), ("📖 How to Play", "how")]
		self.buttons = []
		for i, (lbl, val) in enumerate(labels):
			rect = (cx - w//2, start_y - i*(h+12), w, h)
			self.buttons.append((lbl, val, rect))

	def on_show(self):
		arcade.set_background_color(arcade.color.DARK_BLUE)
		# play bg music once
		if self.music:
			arcade.play_sound(self.music, volume=0.3)

	def on_draw(self):
		self.clear()
		# animated title
		self.title_angle += 0.02
		scale = 1.0 + 0.06 * math.sin(TITLE_ANIM_SPEED * self.title_angle)
		arcade.draw_text(GAME_TITLE, SCREEN_WIDTH/2, SCREEN_HEIGHT-80,
						 arcade.color.GOLD, 48*scale, anchor_x="center", bold=True)

		# draw buttons
		mouse_x, mouse_y = self.window.mouse_x if hasattr(self.window, "mouse_x") else 0, self.window.mouse_y if hasattr(self.window, "mouse_y") else 0
		for lbl, val, rect in self.buttons:
			x, y, w, h = rect
			is_hover = x <= mouse_x <= x+w and y <= mouse_y <= y+h
			color = BUTTON_HOVER if is_hover else BUTTON_COLOR
			# arcade.draw_lrbt_rectangle_filled expects (left, right, bottom, top, color)
			arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, color)
			arcade.draw_text(lbl, x + w/2, y + h/2 - 8, arcade.color.BLACK, 16, anchor_x="center")

	def on_mouse_motion(self, x, y, dx, dy):
		# store mouse position for hover checks
		self.window.mouse_x = x
		self.window.mouse_y = y

	def on_mouse_press(self, x, y, button, modifiers):
		for lbl, val, rect in self.buttons:
			xr, yr, w, h = rect
			if xr <= x <= xr + w and yr <= y <= yr + h:
				if val is False:
					# start multiplayer: show bottle spin to pick starting player
					spin = BottleSpinView(ai_mode=False)
					self.window.show_view(spin)
				elif val is True:
					# Route to AI difficulty selection first
					self.window.show_view(AISelectView())
				elif val == "how":
					self.window.show_view(HowToPlayView())
				return

# ---------------- Game Over View ---------------- #
class GameOverView(arcade.View):
	def __init__(self, winner, scores):
		super().__init__()
		self.winner = winner
		self.scores = scores

	def on_show(self):
		arcade.set_background_color(arcade.color.BLACK)

	def on_draw(self):
		self.clear()
		arcade.draw_text("Round Over!", SCREEN_WIDTH/2, SCREEN_HEIGHT-100,
						 arcade.color.WHITE, 30, anchor_x="center")
		arcade.draw_text(f"Winner: Player {self.winner}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30,
						 arcade.color.YELLOW, 24, anchor_x="center")
		arcade.draw_text(f"Scores: P1 = {self.scores[0]} | P2 = {self.scores[1]}",
						 SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10,
						 arcade.color.LIGHT_GREEN, 20, anchor_x="center")
		arcade.draw_text("Press ENTER to return to Welcome screen",
						 SCREEN_WIDTH/2, 50, arcade.color.GRAY, 16, anchor_x="center")

	def on_key_press(self, key, modifiers):
		if key == arcade.key.ENTER:
			self.window.show_view(WelcomeView())

# ---------------- AI Difficulty Selection ---------------- #
class AISelectView(arcade.View):
	def __init__(self):
		super().__init__()
		self.options = [("Easy", AI_EASY), ("Medium", AI_MEDIUM), ("Hard", AI_HARD)]
		self.rects = []
		self._create_ui()

	def _create_ui(self):
		w, h = 200, 40
		cx = SCREEN_WIDTH // 2
		start_y = SCREEN_HEIGHT // 2 + 40
		self.rects = []
		for i, (label, val) in enumerate(self.options):
			rect = (cx - w//2, start_y - i*(h+12), w, h)
			self.rects.append((label, val, rect))

	def on_show(self):
		arcade.set_background_color(arcade.color.DARK_GRAY)

	def on_draw(self):
		self.clear()
		arcade.draw_text("Select AI Difficulty", SCREEN_WIDTH/2, SCREEN_HEIGHT-80, arcade.color.WHITE, 28, anchor_x="center")
		mouse_x = getattr(self.window, "mouse_x", 0)
		mouse_y = getattr(self.window, "mouse_y", 0)
		for label, val, rect in self.rects:
			x, y, w, h = rect
			is_hover = x <= mouse_x <= x+w and y <= mouse_y <= y+h
			color = BUTTON_HOVER if is_hover else BUTTON_COLOR
			arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, color)
			arcade.draw_text(label, x + w/2, y + h/2 - 8, arcade.color.BLACK, 16, anchor_x="center")

	def on_mouse_motion(self, x, y, dx, dy):
		self.window.mouse_x = x
		self.window.mouse_y = y

	def on_mouse_press(self, x, y, button, modifiers):
		for label, val, rect in self.rects:
			xr, yr, w, h = rect
			if xr <= x <= xr + w and yr <= y <= yr + h:
				# proceed to bottle spin passing chosen difficulty
				spin = BottleSpinView(ai_mode=True, ai_level=val)
				self.window.show_view(spin)
				return

#----------------- HowToPlay tutorial ------------------#
class HowToPlayView(arcade.View):
	def __init__(self):
		super().__init__()
		self.step = 0
		self.timer = 0.0

	def on_show(self):
		arcade.set_background_color(arcade.color.BLACK_OLIVE)

	def on_draw(self):
		self.clear()
		arcade.draw_text("How to Play - Tutorial", SCREEN_WIDTH/2, SCREEN_HEIGHT-40, arcade.color.WHITE, 26, anchor_x="center")
		instructions = [
			"Each player controls 7 pits on their side. Each pit starts with 6 beads.",
			"Pick all beads from one of your pits and sow them counterclockwise, one per pit.",
			"If last bead lands in your store, you get another turn.",
			"If last bead lands in an empty pit on your side, you capture that bead and opposite pit's beads.",
			"Round ends when all pits on one side are empty. Most beads in store wins."
		]
		for i, txt in enumerate(instructions):
			arcade.draw_text(f"{i+1}. {txt}", 60, SCREEN_HEIGHT - 90 - i*40, arcade.color.LIGHT_GRAY, 14)

		arcade.draw_text("Press ESC to return", SCREEN_WIDTH/2, 40, arcade.color.GRAY, 14, anchor_x="center")

	def on_key_press(self, key, modifiers):
		if key == arcade.key.ESCAPE:
			self.window.show_view(WelcomeView())

#----------------- Bottle Spin to choose starter ------------------#
class BottleSpinView(arcade.View):
	def __init__(self, ai_mode=False, ai_level=AI_MEDIUM):
		super().__init__()
		self.rotation = 0.0                # angle in degrees
		self.angular_velocity = 0.0        # degrees per second
		self.spinning = False              # true while bottle is spinning
		self.ai_mode = ai_mode
		self.ai_level = ai_level
		self.result = None
		self.wobble_phase = random.random() * 10.0
		# simple particle list for sparkles during spin
		self.particles = []  # list of dicts: {x,y,vx,vy,life}

	def on_show(self):
		arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
		self.spinning = False
		self.angular_velocity = 0.0
		self.result = None
		self.particles.clear()

	def on_draw(self):
		self.clear()
		# Draw a simple bottle (ellipse + stem) and rotate it visually
		cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		# Instruction shown when waiting for user input
		if not self.spinning and self.result is None:
			arcade.draw_text("Click the bottle (or press SPACE) to spin and decide who starts...", SCREEN_WIDTH/2, SCREEN_HEIGHT-50, arcade.color.WHITE, 14, anchor_x="center")
		elif self.spinning:
			arcade.draw_text("Spinning bottle to decide who starts...", SCREEN_WIDTH/2, SCREEN_HEIGHT-50, arcade.color.WHITE, 16, anchor_x="center")
		else:
			arcade.draw_text("Stopping...", SCREEN_WIDTH/2, SCREEN_HEIGHT-50, arcade.color.WHITE, 14, anchor_x="center")

		# compute tilt/wobble depending on speed
		speed_factor = min(1.0, abs(self.angular_velocity) / 1600.0)
		tilt = 8.0 * speed_factor * math.sin(self.wobble_phase + math.radians(self.rotation) * 0.08)
		# visual_angle: degrees used for drawing ellipse (arcade tilt sign)
		visual_angle = self.rotation + tilt
		# math_angle (radians) for polygon/cos/sin calculations (opposite sign to visual_angle)
		math_angle = math.radians(-visual_angle)

		# drop shadow
		shadow_w = 220
		shadow_h = 40
		arcade.draw_ellipse_filled(cx, cy - 18, shadow_w * (0.8 + 0.2*speed_factor), shadow_h, (0,0,0,60))

		# bottle body: layered ellipses for simple gradient + outline
		body_w, body_h = 180, 48
		# draw body with visual_angle
		arcade.draw_ellipse_filled(cx, cy, body_w, body_h, (120, 80, 40), tilt_angle=visual_angle)  # base wood-like tint
		# highlight overlay
		arcade.draw_ellipse_filled(cx - body_w*0.18, cy + body_h*0.2, body_w*0.6, body_h*0.5, (255, 255, 255, int(80*speed_factor)), tilt_angle=visual_angle)

		# draw rotated neck as polygon (neck sits at bottle front based on math_angle)
		neck_len = 56
		neck_w = 22
		nx = cx + math.cos(math_angle) * (body_w*0.5 - 6)
		ny = cy + math.sin(math_angle) * (body_w*0.5 - 6)
		# neck rectangle corners
		hw = neck_w / 2.0
		hh = neck_len / 2.0
		neck_corners = [
			(+hw, +hh),
			(+hw, -hh),
			(-hw, -hh),
			(-hw, +hh),
		]
		neck_poly = []
		for ox, oy in neck_corners:
			rx = nx + ox * math.cos(math_angle) - oy * math.sin(math_angle)
			ry = ny + ox * math.sin(math_angle) + oy * math.cos(math_angle)
			neck_poly.append((rx, ry))
		arcade.draw_polygon_filled(neck_poly, (90, 58, 30))
		# cap
		cap_x = nx + math.cos(math_angle) * (neck_len/2 + 6)
		cap_y = ny + math.sin(math_angle) * (neck_len/2 + 6)
		arcade.draw_circle_filled(cap_x, cap_y, 10, (60, 40, 20))
		arcade.draw_circle_outline(cap_x, cap_y, 10, arcade.color.BLACK, 2)
		# outline body for crispness
		arcade.draw_ellipse_outline(cx, cy, body_w+4, body_h+4, arcade.color.BLACK, 2, tilt_angle=visual_angle)

		# small rotating center marker to show orientation (use math_angle)
		arcade.draw_circle_filled(cx + math.cos(math_angle)*40, cy + math.sin(math_angle)*12, 6, arcade.color.LIGHT_GRAY)

		# draw particles (sparkles)
		for p in list(self.particles):
			alpha = int(255 * max(0.0, p["life"]/p["max_life"]))
			col = (255, 230, 180, alpha)
			arcade.draw_circle_filled(p["x"], p["y"], p["size"], col)
		# result text after stop
		if self.result is not None and not self.spinning:
			arcade.draw_text(f"{'Player' if self.result==0 else ('AI' if self.ai_mode else 'Player 2')} starts!", SCREEN_WIDTH/2, 60, arcade.color.GOLD, 18, anchor_x="center")

	def on_update(self, delta_time):
		# update particles
		for p in list(self.particles):
			p["life"] -= delta_time
			if p["life"] <= 0:
				self.particles.remove(p)
				continue
			p["x"] += p["vx"] * delta_time
			p["y"] += p["vy"] * delta_time
			p["vy"] -= 60 * delta_time  # gravity

		# spinning dynamics
		if not self.spinning:
			return
		# define center locally for use here (prevent NameError)
		cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		# update rotation
		self.rotation = (self.rotation + self.angular_velocity * delta_time) % 360.0
		# recompute tilt and math_angle here for consistency
		speed_factor = min(1.0, abs(self.angular_velocity) / 1600.0)
		tilt = 8.0 * speed_factor * math.sin(self.wobble_phase + math.radians(self.rotation) * 0.08)
		visual_angle = self.rotation + tilt
		math_angle = math.radians(-visual_angle)
		# damping (non-linear): reduce angular velocity each frame
		self.angular_velocity *= max(0.0, 1.0 - 1.6 * delta_time)
		# spawn some particles while fast (use math_angle)
		if abs(self.angular_velocity) > 200 and random.random() < 0.25:
			px = cx + math.cos(math_angle) * 30
			py = cy + math.sin(math_angle) * 10
			self.particles.append({"x": px, "y": py, "vx": random.uniform(-60, 60), "vy": random.uniform(20,120), "life": random.uniform(0.3,0.9), "max_life": 0.9, "size": random.uniform(1.8,3.5)})
		# wobble phase progresses
		self.wobble_phase += delta_time * 8.0
		# stop condition
		if abs(self.angular_velocity) < 18.0:
			# finish spin
			self.spinning = False
			# decide result with slight bias by final visual angle
			self.result = 0 if math.cos(math.radians(visual_angle)) > 0 else 1
			# small delay then launch game
			arcade.schedule(self._launch_game, 0.8)

	# allow clicking or pressing space to begin the spin
	def on_mouse_press(self, x, y, button, modifiers):
		# if already spinning or result decided, ignore
		if self.spinning or (self.result is not None and not self.spinning):
			return
		# detect click within bottle ellipse area (approximate)
		cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		elw = 160  # same ellipse width used in on_draw
		if math.hypot(x - cx, y - cy) <= elw/2 + 26:
			# start spin using angular velocity and slight randomization
			self.rotation = random.uniform(0, 360)
			self.angular_velocity = random.uniform(700.0, 1600.0) * random.choice([1, -1])
			self.spinning = True
			# clear previous result and particles
			self.result = None
			self.particles.clear()

	def on_key_press(self, key, modifiers):
		# allow SPACE to trigger the spin as well
		if key == arcade.key.SPACE and not self.spinning:
			# start spin via keyboard
			self.rotation = random.uniform(0, 360)
			self.angular_velocity = random.uniform(700.0, 1600.0) * random.choice([1, -1])
			self.spinning = True
			self.result = None
			self.particles.clear()

	def _launch_game(self, delta_time):
		arcade.unschedule(self._launch_game)
		# Local import to avoid circular import at module import time
		from .pallanguzhi import Pallanguzhi
		game_view = Pallanguzhi(ai_mode=self.ai_mode, ai_level=self.ai_level)
		# set starting player based on spin result: make top row 0 and bottom row 1
		game_view.current_player = self.result
		self.window.show_view(game_view)