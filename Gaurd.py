import pygame
import math
import random

# Guard states
STATE_PATROL = "patrol"         # Green vision - normal patrol
STATE_SUSPICIOUS = "suspicious" # Yellow vision - player detected, confirming
STATE_ALERT = "alert"           # Red vision - confirmed, chasing player


class Guard:
    """
    A guard with cone vision (150° sector) that patrols the map.
    
    Vision color changes based on detection state:
      - Green:  patrolling normally
      - Yellow: player stepped into vision, guard is suspicious
      - Red:    player confirmed, guard chases and catches player
    """

    def __init__(self, x, y, patrol_points, vision_radius=120, speed=2, vision_angle=140, wall_manager=None):
        """
        Args:
            x, y: Starting position of the guard.
            patrol_points: List of (x, y) tuples the guard patrols between.
            vision_radius: Radius of the vision cone.
            speed: Movement speed in pixels per frame.
            vision_angle: Total angle of the vision cone in degrees (e.g. 150).
        """
        self.x = float(x)
        self.y = float(y)
        self.patrol_points = patrol_points
        self.current_patrol_index = 0
        self.vision_radius = vision_radius
        self.speed = speed
        self.chase_speed = speed * 2.5  # Faster when chasing

        # Vision cone settings
        self.vision_angle = vision_angle  # Total cone angle in degrees
        self.facing_angle = 0.0          # Angle the guard is facing (radians, 0 = right)

        # Reference to walls for collision and line-of-sight
        self.wall_manager = wall_manager

        # Detection state
        self.state = STATE_PATROL
        self.suspicion_timer = 0.0          # Time spent suspicious (seconds)
        self.suspicion_threshold = 0.2     # Seconds before going alert
        self.player_was_in_vision = False    # Track if player left vision during suspicion

        # Guard visual size
        self.width = 20
        self.height = 20

        # Colors for each state
        self.vision_colors = {
            STATE_PATROL:     (0, 200, 0, 60),      # Green, semi-transparent
            STATE_SUSPICIOUS: (255, 255, 0, 80),     # Yellow, semi-transparent
            STATE_ALERT:      (255, 0, 0, 100),      # Red, semi-transparent
        }
        self.body_colors = {
            STATE_PATROL:     (0, 150, 0),
            STATE_SUSPICIOUS: (200, 200, 0),
            STATE_ALERT:      (200, 0, 0),
        }

    def get_rect(self):
        """Return the guard's bounding rectangle."""
        return pygame.Rect(
            int(self.x - self.width // 2),
            int(self.y - self.height // 2),
            self.width,
            self.height,
        )

    def _distance_to(self, px, py):
        """Euclidean distance from guard center to a point."""
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)

    def _player_in_vision(self, player_rect):
        """Check if the player center is within the vision cone (sector)."""
        # Use player center for angle check
        pcx = player_rect.centerx
        pcy = player_rect.centery

        # Distance check
        dist = self._distance_to(pcx, pcy)
        if dist > self.vision_radius:
            return False

        # Angle check — is the player within the cone?
        angle_to_player = math.atan2(pcy - self.y, pcx - self.x)
        half_cone = math.radians(self.vision_angle / 2)

        # Compute the shortest angular difference
        diff = angle_to_player - self.facing_angle
        # Normalize to [-pi, pi]
        diff = (diff + math.pi) % (2 * math.pi) - math.pi

        return abs(diff) <= half_cone

    def _vision_blocked_by_wall(self, player_rect):
        """Check if a wall blocks line-of-sight to the player."""
        if self.wall_manager is None:
            return False  # No walls to block
        return not self.wall_manager.line_of_sight_clear(
            self.x, self.y, player_rect.centerx, player_rect.centery
        )

    def _move_toward(self, tx, ty, spd):
        """Move the guard toward target (tx, ty) at the given speed."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0.1:
            # Update facing angle to match movement direction
            self.facing_angle = math.atan2(dy, dx)
        if dist < spd:
            self.x = float(tx)
            self.y = float(ty)
            return True  # Arrived
        self.x += (dx / dist) * spd
        self.y += (dy / dist) * spd

        # Wall collision — revert if guard walked into a wall
        if self.wall_manager is not None:
            old_x_saved = self.x - (dx / dist) * spd
            old_y_saved = self.y - (dy / dist) * spd
            self.x, self.y = self.wall_manager.clamp_entity_movement(
                old_x_saved, old_y_saved, self.x, self.y,
                self.width, self.height
            )

        return False

    # ------------------------------------------------------------------
    # Main update — call once per frame
    # ------------------------------------------------------------------
    def update(self, player_rect, dt):
        """
        Update guard logic.

        Args:
            player_rect: pygame.Rect of the player.
            dt: Delta time in seconds since last frame.

        Returns:
            True if the guard has caught the player (game over).
        """
        player_visible = (
            self._player_in_vision(player_rect)
            and not self._vision_blocked_by_wall(player_rect)
        )

        # ---- STATE: PATROL ----
        if self.state == STATE_PATROL:
            # Move along patrol path
            target = self.patrol_points[self.current_patrol_index]
            arrived = self._move_toward(target[0], target[1], self.speed)
            if arrived:
                self.current_patrol_index = (
                    (self.current_patrol_index + 1) % len(self.patrol_points)
                )

            # If player enters vision → become suspicious
            if player_visible:
                self.state = STATE_SUSPICIOUS
                self.suspicion_timer = 0.0
                self.player_was_in_vision = True

        # ---- STATE: SUSPICIOUS ----
        elif self.state == STATE_SUSPICIOUS:
            # Guard stops and watches
            self.suspicion_timer += dt

            if player_visible:
                self.player_was_in_vision = True

            # If player leaves vision, reset after a short grace period
            if not player_visible:
                self.suspicion_timer -= dt * 2  # Drains faster when player not visible
                if self.suspicion_timer <= 0:
                    self.state = STATE_PATROL
                    self.suspicion_timer = 0.0

            # If suspicion reaches threshold → ALERT
            if self.suspicion_timer >= self.suspicion_threshold:
                self.state = STATE_ALERT
                return "ALERT_TRIGGERED"  # Signal to manager to alert all guards

        # ---- STATE: ALERT ----
        elif self.state == STATE_ALERT:
            # Chase the player
            player_cx = player_rect.centerx
            player_cy = player_rect.centery
            self._move_toward(player_cx, player_cy, self.chase_speed)

            # Check if guard caught the player (rects overlap)
            if self.get_rect().colliderect(player_rect):
                return True  # CAUGHT — game over

        return False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, surface):
        """Draw the guard and its vision cone onto the surface."""
        color = self.vision_colors[self.state]
        border_color = (*color[:3], 150)

        # Build the cone as a polygon (pie-slice / sector)
        half_cone = math.radians(self.vision_angle / 2)
        num_segments = 30  # Smoothness of the arc
        start_angle = self.facing_angle - half_cone
        end_angle = self.facing_angle + half_cone

        # Cone polygon points: center → arc → back to center
        points = [(self.x, self.y)]
        for i in range(num_segments + 1):
            a = start_angle + (end_angle - start_angle) * i / num_segments
            px = self.x + math.cos(a) * self.vision_radius
            py = self.y + math.sin(a) * self.vision_radius
            points.append((px, py))
        points.append((self.x, self.y))

        # Draw filled cone (semi-transparent)
        if len(points) >= 3:
            cone_surface = pygame.Surface(
                (self.vision_radius * 2 + 20, self.vision_radius * 2 + 20),
                pygame.SRCALPHA,
            )
            # Offset points so they fit in the surface
            offset_x = self.vision_radius + 10
            offset_y = self.vision_radius + 10
            offset_points = [
                (px - self.x + offset_x, py - self.y + offset_y)
                for (px, py) in points
            ]
            pygame.draw.polygon(cone_surface, color, offset_points)
            pygame.draw.polygon(cone_surface, border_color, offset_points, 2)
            surface.blit(
                cone_surface,
                (int(self.x - offset_x), int(self.y - offset_y)),
            )

        # Draw guard body
        body_color = self.body_colors[self.state]
        guard_rect = self.get_rect()
        pygame.draw.rect(surface, body_color, guard_rect)
        pygame.draw.rect(surface, (255, 255, 255), guard_rect, 2)  # White border

        # Draw a small "eye" indicator showing state
        eye_color = (255, 255, 255)
        pygame.draw.circle(
            surface, eye_color, (int(self.x), int(self.y - 4)), 3
        )
        pupil_color = self.body_colors[self.state]
        pygame.draw.circle(
            surface, pupil_color, (int(self.x), int(self.y - 4)), 1
        )

    def draw_suspicion_bar(self, surface):
        """Draw a small suspicion progress bar above the guard when suspicious."""
        if self.state != STATE_SUSPICIOUS:
            return
        bar_width = 40
        bar_height = 5
        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - self.height // 2 - 12)
        # Background
        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        # Fill
        fill_ratio = min(self.suspicion_timer / self.suspicion_threshold, 1.0)
        fill_color = (
            int(255 * fill_ratio),
            int(255 * (1 - fill_ratio)),
            0,
        )
        pygame.draw.rect(
            surface, fill_color, (bar_x, bar_y, int(bar_width * fill_ratio), bar_height)
        )
        pygame.draw.rect(
            surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1
        )


# ======================================================================
# Guard Manager — manages all guards + game-over overlay
# ======================================================================

class GuardManager:
    """
    Manages a collection of guards and handles the game-over state
    when any guard catches the player.
    """

    def __init__(self, screen_width, screen_height, wall_manager=None):
        self.guards = []
        self.game_over = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wall_manager = wall_manager

        # Restart button rect (will be drawn in the game-over overlay)
        btn_w, btn_h = 200, 50
        self.restart_rect = pygame.Rect(
            screen_width // 2 - btn_w // 2,
            screen_height // 2 + 60,
            btn_w,
            btn_h,
        )

    def add_guard(self, guard):
        """Add a Guard instance to the manager."""
        self.guards.append(guard)

    def create_default_guards(self):
        """
        Create a set of default guards with patrol routes that work
        on an 800×600 screen.
        """
        guard_configs = [
            # Guard 1 — patrols top area horizontally
            {
                "start": (200, 150),
                "patrol": [(200, 150), (600, 150)],
                "radius": 90,
                "speed": 1.5,
            },
            # Guard 2 — patrols right side vertically
            {
                "start": (650, 200),
                "patrol": [(650, 200), (650, 450)],
                "radius": 85,
                "speed": 1.8,
            },
            # Guard 3 — patrols center in a square
            {
                "start": (350, 350),
                "patrol": [(250, 300), (500, 300), (500, 450), (250, 450)],
                "radius": 75,
                "speed": 1.3,
            },
            # Guard 4 — patrols bottom-left area diagonally
            {
                "start": (150, 450),
                "patrol": [(150, 450), (400, 450), (400, 550), (150, 550)],
                "radius": 80,
                "speed": 1.6,
            },
        ]

        for cfg in guard_configs:
            g = Guard(
                cfg["start"][0],
                cfg["start"][1],
                cfg["patrol"],
                vision_radius=cfg["radius"],
                speed=cfg["speed"],
                wall_manager=self.wall_manager,
            )
            self.add_guard(g)

    def create_guards_from_level(self, guard_configs):
        """
        Create guards from a level's predefined guard configs.

        Args:
            guard_configs: List of dicts with keys:
                "start", "patrol", "radius", "speed"
        """
        for cfg in guard_configs:
            g = Guard(
                cfg["start"][0],
                cfg["start"][1],
                cfg["patrol"],
                vision_radius=cfg["radius"],
                speed=cfg["speed"],
                wall_manager=self.wall_manager,
            )
            self.add_guard(g)


    def reset(self):
        """Reset all guards to patrol state and back to start positions."""
        self.game_over = False
        for i, g in enumerate(self.guards):
            g.state = STATE_PATROL
            g.suspicion_timer = 0.0
            g.current_patrol_index = 0
            if g.patrol_points:
                g.x = float(g.patrol_points[0][0])
                g.y = float(g.patrol_points[0][1])

    def _alert_all_guards(self, player_rect):
        """Set ALL guards to alert state so they all chase the player."""
        for g in self.guards:
            if g.state != STATE_ALERT:
                g.state = STATE_ALERT
                g.suspicion_timer = g.suspicion_threshold

    def update(self, player_rect, dt):
        """
        Update all guards.

        When any guard becomes ALERT, all other guards are also
        set to ALERT so they all chase the player together.

        Args:
            player_rect: pygame.Rect of the player.
            dt: Delta time in seconds.

        Returns:
            True if the game is over (player was caught).
        """
        if self.game_over:
            return True

        alert_triggered = False
        for guard in self.guards:
            result = guard.update(player_rect, dt)
            if result == "ALERT_TRIGGERED":
                alert_triggered = True
            elif result is True:
                # Guard caught the player
                self.game_over = True
                return True

        # If any guard just became alert, alert ALL guards
        if alert_triggered:
            self._alert_all_guards(player_rect)

        return False

    def draw(self, surface):
        """Draw all guards and their vision circles."""
        for guard in self.guards:
            guard.draw(surface)
            guard.draw_suspicion_bar(surface)

    def draw_game_over(self, surface):
        """Draw the game-over overlay with a restart button."""
        if not self.game_over:
            return

        # Dark overlay
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # "GAME OVER" text
        try:
            font_large = pygame.font.Font(None, 80)
            font_small = pygame.font.Font(None, 36)
            font_btn = pygame.font.Font(None, 32)
        except Exception:
            font_large = pygame.font.SysFont("arial", 60)
            font_small = pygame.font.SysFont("arial", 28)
            font_btn = pygame.font.SysFont("arial", 24)

        # Main title
        game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        surface.blit(game_over_text, text_rect)

        # Subtitle
        caught_text = font_small.render(
            "You were caught by a guard!", True, (255, 200, 200)
        )
        caught_rect = caught_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 10)
        )
        surface.blit(caught_text, caught_rect)

        # Restart button
        mouse_pos = pygame.mouse.get_pos()
        if self.restart_rect.collidepoint(mouse_pos):
            btn_color = (0, 200, 100)
            text_color = (255, 255, 255)
        else:
            btn_color = (0, 150, 80)
            text_color = (220, 220, 220)

        pygame.draw.rect(surface, btn_color, self.restart_rect, border_radius=10)
        pygame.draw.rect(
            surface, (255, 255, 255), self.restart_rect, 2, border_radius=10
        )

        btn_text = font_btn.render("RESTART", True, text_color)
        btn_text_rect = btn_text.get_rect(center=self.restart_rect.center)
        surface.blit(btn_text, btn_text_rect)

    def handle_event(self, event):
        """
        Handle mouse click on the restart button during game over.

        Returns:
            True if the restart button was clicked.
        """
        if not self.game_over:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_rect.collidepoint(event.pos):
                return True
        return False
