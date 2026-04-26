import pygame
import math
import random





class Wall:
    """A single rectangular wall with visual styling."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Slightly randomized dark color for each wall (visual variety)
        base = random.randint(40, 70)
        self.color = (base, base + 10, base + 30)
        self.border_color = (100, 120, 160)

    def draw(self, surface):
        """Draw the wall with a subtle 3D-ish look."""
        # Main fill
        pygame.draw.rect(surface, self.color, self.rect)
        # Highlight on top/left edges
        pygame.draw.line(
            surface,
            (self.color[0] + 40, self.color[1] + 40, self.color[2] + 40),
            self.rect.topleft,
            self.rect.topright,
            2,
        )
        pygame.draw.line(
            surface,
            (self.color[0] + 30, self.color[1] + 30, self.color[2] + 30),
            self.rect.topleft,
            self.rect.bottomleft,
            2,
        )
        # Shadow on bottom/right edges
        pygame.draw.line(
            surface,
            (max(self.color[0] - 20, 0), max(self.color[1] - 10, 0), max(self.color[2] - 10, 0)),
            self.rect.bottomleft,
            self.rect.bottomright,
            2,
        )
        pygame.draw.line(
            surface,
            (max(self.color[0] - 20, 0), max(self.color[1] - 10, 0), max(self.color[2] - 10, 0)),
            self.rect.topright,
            self.rect.bottomright,
            2,
        )
        # Outer border
        pygame.draw.rect(surface, self.border_color, self.rect, 1)



LEVELS = {


    1: {
        "name": "Training Ground",
        "player_spawn": (60, 540),
        "objective": (740, 40),
        "walls": [
            # ---- Top horizontal barrier ----
            (160, 100, 300, 20),
            # ---- Top-right horizontal barrier ----
            (560, 100, 200, 20),
            # ---- Center vertical divider ----
            (400, 120, 20, 180),
            # ---- Left room wall (vertical) ----
            (160, 100, 20, 180),
            # ---- Left room bottom wall ----
            (160, 280, 160, 20),
            # ---- Center horizontal corridor wall ----
            (280, 360, 240, 20),
            # ---- Right vertical wall ----
            (620, 120, 20, 200),
            # ---- Bottom-right L-shape ----
            (500, 460, 20, 120),
            (500, 460, 200, 20),
            # ---- Bottom-left barrier ----
            (160, 460, 180, 20),
            # ---- Small cover block center-bottom ----
            (340, 500, 60, 20),
        ],
        "guards": [
            # Guard 1 — patrols the top corridor left-right
            {
                "start": (280, 60),
                "patrol": [(200, 60), (540, 60)],
                "radius": 85,
                "speed": 1.5,
            },
            # Guard 2 — patrols right side up-down
            {
                "start": (700, 200),
                "patrol": [(700, 150), (700, 430)],
                "radius": 80,
                "speed": 1.4,
            },
            # Guard 3 — patrols below the center corridor wall
            {
                "start": (300, 420),
                "patrol": [(220, 400), (270, 400), (270, 440), (220, 440)],
                "radius": 75,
                "speed": 1.3,
            },
        ],
    },

  
    2: {
        "name": "The Compound",
        "player_spawn": (60, 540),
        "objective": (740, 40),
        "walls": [
            # ---- Top-left room ----
            (120, 80, 20, 180),      # left wall
            (120, 80, 200, 20),      # top wall
            (320, 80, 20, 120),      # right wall (with gap at bottom)
            # ---- Top-right room ----
            (460, 80, 20, 180),      # left wall (with gap)
            (460, 80, 280, 20),      # top wall
            (740, 80, 20, 180),      # right wall
            # ---- Center maze section ----
            (200, 260, 20, 160),     # vertical divider left
            (200, 260, 180, 20),     # horizontal connector
            (380, 200, 20, 160),     # vertical divider center
            (480, 260, 180, 20),     # horizontal right
            (560, 260, 20, 140),     # vertical divider right
            # ---- Bottom corridor walls ----
            (120, 460, 240, 20),     # bottom-left barrier
            (460, 460, 20, 120),     # bottom vertical
            (560, 460, 200, 20),     # bottom-right barrier
            # ---- Cover blocks ----
            (660, 340, 60, 20),      # small cover right
            (300, 380, 20, 80),      # small vertical cover center
        ],
        "guards": [
            # Guard 1 — patrols inside top-left room
            {
                "start": (220, 160),
                "patrol": [(160, 120), (300, 120), (300, 220), (160, 220)],
                "radius": 80,
                "speed": 1.6,
            },
            # Guard 2 — patrols inside top-right room
            {
                "start": (600, 160),
                "patrol": [(500, 120), (700, 120), (700, 220), (500, 220)],
                "radius": 85,
                "speed": 1.5,
            },
            # Guard 3 — patrols center-bottom corridor (avoids center dividers)
            {
                "start": (440, 420),
                "patrol": [(240, 420), (440, 420), (440, 440), (240, 440)],
                "radius": 75,
                "speed": 1.8,
            },
            # Guard 4 — patrols bottom area
            {
                "start": (650, 520),
                "patrol": [(600, 500), (750, 500), (750, 560), (600, 560)],
                "radius": 80,
                "speed": 1.7,
            },
        ],
    },

  
    3: {
        "name": "High Security",
        "player_spawn": (40, 560),
        "objective": (750, 30),
        "walls": [
            # ---- Outer inner walls (creates a border corridor) ----
            (80, 60, 640, 20),       # top inner wall
            (80, 60, 20, 200),       # left inner wall top
            (80, 340, 20, 200),      # left inner wall bottom
            (720, 60, 20, 240),      # right inner wall top
            (720, 380, 20, 160),     # right inner wall bottom
            (80, 540, 300, 20),      # bottom inner wall left
            (480, 540, 260, 20),     # bottom inner wall right
            # ---- Interior room dividers ----
            (200, 140, 20, 200),     # room divider 1
            (200, 140, 160, 20),     # room top 1
            (360, 80, 20, 160),      # room divider 2
            (460, 140, 160, 20),     # room top 2
            (460, 140, 20, 200),     # room divider 3
            (620, 200, 100, 20),     # room connector right
            # ---- Center cross ----
            (340, 320, 120, 20),     # horizontal center
            (400, 260, 20, 140),     # vertical center
            # ---- Bottom rooms ----
            (180, 420, 20, 120),     # bottom-left divider
            (180, 420, 140, 20),     # bottom-left top wall
            (520, 400, 20, 140),     # bottom-right divider
            (520, 400, 200, 20),     # bottom-right top wall
            # ---- Scattered cover ----
            (280, 460, 60, 20),      # cover 1
            (600, 480, 20, 60),      # cover 2
            (660, 300, 60, 20),      # cover 3
        ],
        "guards": [
            # Guard 1 — patrols top corridor
            {
                "start": (500, 40),
                "patrol": [(120, 40), (700, 40)],
                "radius": 90,
                "speed": 2.0,
            },
            # Guard 2 — patrols left interior room
            {
                "start": (140, 240),
                "patrol": [(120, 100), (120, 300)],
                "radius": 85,
                "speed": 1.8,
            },
            # Guard 3 — patrols right interior room (avoids room connector)
            {
                "start": (600, 170),
                "patrol": [(500, 170), (600, 170), (600, 190), (500, 190)],
                "radius": 80,
                "speed": 2.0,
            },
            # Guard 4 — patrols center area
            {
                "start": (340, 400),
                "patrol": [(240, 360), (380, 360), (380, 500), (240, 500)],
                "radius": 85,
                "speed": 1.9,
            },
            # Guard 5 — patrols bottom-right
            {
                "start": (650, 480),
                "patrol": [(560, 440), (700, 440), (700, 520), (560, 520)],
                "radius": 90,
                "speed": 2.2,
            },
        ],
    },
}

# Total number of levels available
TOTAL_LEVELS = len(LEVELS)




class WallManager:
    """
    Manages walls loaded from predefined level layouts.

    Key features:
      - Level-based wall loading with predefined layouts
      - Line-of-sight checking (for guard vision blocking)
      - Collision detection for player and guard movement
      - Smooth axis-sliding so entities don't get stuck on corners
    """

    # Grid cell size in pixels (used for line-of-sight grid)
    CELL_SIZE = 20

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.walls = []
        self.current_level = 0
        self.level_name = ""
        self.player_spawn = (100, 500)

        # Grid dimensions (for fast line-of-sight)
        self.grid_cols = screen_width // self.CELL_SIZE
        self.grid_rows = screen_height // self.CELL_SIZE
        self.grid = [[False] * self.grid_cols for _ in range(self.grid_rows)]

    # ------------------------------------------------------------------
    # Level loading
    # ------------------------------------------------------------------
    def load_level(self, level_number):
        """
        Load a predefined level by number.

        Args:
            level_number: Level to load (1, 2, 3, ...).

        Returns:
            The guard configs for this level (list of dicts).
        """
        if level_number not in LEVELS:
            level_number = 1  # Fallback to level 1

        level_data = LEVELS[level_number]
        self.current_level = level_number
        self.level_name = level_data["name"]
        self.player_spawn = level_data["player_spawn"]
        self.objective_pos = level_data.get("objective", (740, 40))

        # Clear old walls
        self.walls.clear()
        self.grid = [[False] * self.grid_cols for _ in range(self.grid_rows)]

        # Create wall objects and populate the grid
        for wx, wy, ww, wh in level_data["walls"]:
            self.walls.append(Wall(wx, wy, ww, wh))
            # Mark grid cells covered by this wall
            self._mark_grid(wx, wy, ww, wh)

        return level_data["guards"]

    def _mark_grid(self, x, y, w, h):
        """Mark grid cells occupied by a wall rectangle."""
        c_start = max(0, x // self.CELL_SIZE)
        c_end = min(self.grid_cols, (x + w + self.CELL_SIZE - 1) // self.CELL_SIZE)
        r_start = max(0, y // self.CELL_SIZE)
        r_end = min(self.grid_rows, (y + h + self.CELL_SIZE - 1) // self.CELL_SIZE)
        for r in range(r_start, r_end):
            for c in range(c_start, c_end):
                self.grid[r][c] = True

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------
    def collides(self, rect):
        """Check if a pygame.Rect collides with any wall."""
        for wall in self.walls:
            if rect.colliderect(wall.rect):
                return True
        return False

    def clamp_player_movement(self, old_x, old_y, new_x, new_y, size):
        """
        Try to move from (old_x, old_y) to (new_x, new_y).
        If the new position collides with a wall, allow sliding along axes
        independently so the player doesn't get 'stuck' on corners.

        Returns:
            (final_x, final_y) — the corrected position.
        """
        # Try horizontal move only
        test_rect_x = pygame.Rect(int(new_x), int(old_y), size, size)
        if self.collides(test_rect_x):
            new_x = old_x

        # Try vertical move only
        test_rect_y = pygame.Rect(int(new_x), int(new_y), size, size)
        if self.collides(test_rect_y):
            new_y = old_y

        return new_x, new_y

    def clamp_entity_movement(self, old_x, old_y, new_x, new_y, width, height):
        """
        Generic version for any entity (guards, etc).
        Returns (final_x, final_y).
        """
        half_w = width // 2
        half_h = height // 2

        # Try horizontal
        test_rect = pygame.Rect(int(new_x - half_w), int(old_y - half_h), width, height)
        if self.collides(test_rect):
            new_x = old_x

        # Try vertical
        test_rect = pygame.Rect(int(new_x - half_w), int(new_y - half_h), width, height)
        if self.collides(test_rect):
            new_y = old_y

        return new_x, new_y

  
    def line_of_sight_clear(self, x1, y1, x2, y2):
        """
        Check if a straight line from (x1,y1) to (x2,y2) is clear of walls.
        Uses ray-marching along the line in small steps.

        Returns:
            True if the line is NOT blocked by any wall.
        """
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            return True

        # Step size — half the cell size for accuracy
        step = self.CELL_SIZE / 2
        steps = int(dist / step) + 1

        for i in range(steps + 1):
            t = i / steps
            px = x1 + dx * t
            py = y1 + dy * t
            # Check which grid cell this point falls in
            gc = int(px // self.CELL_SIZE)
            gr = int(py // self.CELL_SIZE)
            if 0 <= gr < self.grid_rows and 0 <= gc < self.grid_cols:
                if self.grid[gr][gc]:
                    return False  # Blocked by wall
        return True

    def draw(self, surface):
        """Draw all walls onto the surface."""
        for wall in self.walls:
            wall.draw(surface)

    def draw_level_name(self, surface):
        """Draw the current level name in the top-left corner."""
        try:
            font = pygame.font.Font(None, 28)
        except Exception:
            font = pygame.font.SysFont("arial", 20)
        text = font.render(
            f"Level {self.current_level}: {self.level_name}",
            True,
            (180, 200, 220),
        )
        surface.blit(text, (10, 8))
