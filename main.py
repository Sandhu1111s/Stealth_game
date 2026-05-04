from tkinter import font
import math
import os

import pygame
from Gaurd import GuardManager, Guard
from Walls import WallManager, TOTAL_LEVELS

pygame.init()
pygame.mixer.init()
WIDTH , HEIGHT = 800, 600
bg = pygame.image.load("newbg/new.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
pygame.mixer.music.load("assests/mu.mp3")
pygame.mixer.music.play(-1)



screen = pygame.display.set_mode((WIDTH , HEIGHT))
pygame.display.set_caption("Stealth Game")
MENU = 0
GAME = 1
state = MENU

# Current level
current_level = 1

# Player setup
player_x, player_y = 0, 0
player_speed = 4
player_size = 30

# Objective state
OBJ_WAITING = 0      # Objective is sitting at its location, waiting to be picked up
OBJ_PICKED = 1        # Player picked it up, must return to spawn
OBJ_COMPLETE = 2      # Player returned to spawn — level complete!
objective_state = OBJ_WAITING
objective_size = 20
objective_pulse = 0.0  # For glowing animation

# Level complete buttons
btn_w, btn_h = 180, 45
btn_gap = 20
btn_restart_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50, btn_w, btn_h)
btn_next_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50 + btn_h + btn_gap, btn_w, btn_h)
btn_menu_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50 + 2 * (btn_h + btn_gap), btn_w, btn_h)

# Wall & guard system
wall_manager = WallManager(WIDTH, HEIGHT)
guard_manager = GuardManager(WIDTH, HEIGHT, wall_manager=wall_manager)

# --- Load textures ---
TEXTURE_DIR = "textures"
if os.path.isdir(TEXTURE_DIR):
    wall_tex = os.path.join(TEXTURE_DIR, "wall.png")
    guard_tex = os.path.join(TEXTURE_DIR, "guard.png")
    player_tex_path = os.path.join(TEXTURE_DIR, "player.png")
    if os.path.isfile(wall_tex):
        wall_manager.set_wall_texture(wall_tex)
    if os.path.isfile(guard_tex):
        Guard.set_texture(guard_tex)
    if os.path.isfile(player_tex_path):
        player_texture = pygame.image.load(player_tex_path).convert_alpha()
    else:
        player_texture = None
else:
    player_texture = None

# Player facing direction (for texture rotation)
player_facing_angle = 0.0


def load_level(level_num):
    """Load a level — sets up walls, guards, player spawn, and objective."""
    global player_x, player_y, guard_manager, objective_state

    guard_configs = wall_manager.load_level(level_num)
    player_x, player_y = wall_manager.player_spawn
    objective_state = OBJ_WAITING

    guard_manager = GuardManager(WIDTH, HEIGHT, wall_manager=wall_manager)
    guard_manager.create_guards_from_level(guard_configs)


# Load level 1 at start
load_level(current_level)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = GAME
                    current_level = 1
                    load_level(current_level)
                if event.key == pygame.K_ESCAPE:
                    running = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_rect.collidepoint(event.pos):
                    state = GAME
                    current_level = 1
                    load_level(current_level)
                if quit_rect.collidepoint(event.pos):
                    running = False

        if state == GAME:
            # Game over restart
            if guard_manager.handle_event(event):
                load_level(current_level)

            # Level complete buttons
            if objective_state == OBJ_COMPLETE and event.type == pygame.MOUSEBUTTONDOWN:
                if btn_restart_rect.collidepoint(event.pos):
                    load_level(current_level)
                elif btn_next_rect.collidepoint(event.pos):
                    if current_level < TOTAL_LEVELS:
                        current_level += 1
                    load_level(current_level)
                elif btn_menu_rect.collidepoint(event.pos):
                    state = MENU
                    current_level = 1


    screen.fill((1,3,45))
    if state == MENU:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        screen.blit(bg, (0, 0))

        menu_font = pygame.font.Font("title/my2.otf", 40)  
        title_font = pygame.font.Font("assests/my.ttf", 60)
        title_text = title_font.render("Stealth Game", True, (0 ,255 ,255))

        mouse_pos = pygame.mouse.get_pos()

        new_game_text = menu_font.render("New Game", True, (0 ,255 ,255))
        new_game_rect = new_game_text.get_rect(center=(WIDTH//2, HEIGHT//2))

        quit_text = menu_font.render("Quit", True, (0 ,255 ,255))
        quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))

        text = menu_font.render("Press ENTER to Start", True, (0 ,255 ,255))
        if new_game_rect.collidepoint(mouse_pos):
            new_game_text = menu_font.render("New Game", True, (255, 215, 0))
        else:
            new_game_text = menu_font.render("New Game", True, (0 ,255 ,255))

        if quit_rect.collidepoint(mouse_pos):
            quit_text = menu_font.render("Quit", True, (255, 215, 0))
        else:
            quit_text = menu_font.render("Quit", True, (0 ,255 ,255))

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(new_game_text, new_game_rect)
        screen.blit(quit_text, quit_rect)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 + 150))
       
    elif state == GAME:
        pygame.mixer.music.stop()
        dt = clock.get_time() / 1000.0  # Delta time in seconds
        objective_pulse += dt * 3  # Animate the objective glow

        # --- Player movement (WASD or arrow keys) ---
        if not guard_manager.game_over and objective_state != OBJ_COMPLETE:
            keys = pygame.key.get_pressed()
            old_px, old_py = player_x, player_y  # Save for wall collision
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= player_speed
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += player_speed
                dy += 1

            # Update player facing angle when moving
            if dx != 0 or dy != 0:
                player_facing_angle = math.atan2(dy, dx)

            # Keep player on screen
            player_x = max(0, min(player_x, WIDTH - player_size))
            player_y = max(0, min(player_y, HEIGHT - player_size))

            # Wall collision — slide along walls instead of stopping
            player_x, player_y = wall_manager.clamp_player_movement(
                old_px, old_py, player_x, player_y, player_size
            )

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # --- Objective logic ---
        obj_x, obj_y = wall_manager.objective_pos
        spawn_x, spawn_y = wall_manager.player_spawn

        if objective_state == OBJ_WAITING:
            # Check if player reached the objective
            obj_rect = pygame.Rect(
                obj_x - objective_size // 2, obj_y - objective_size // 2,
                objective_size, objective_size
            )
            if player_rect.colliderect(obj_rect):
                objective_state = OBJ_PICKED

        elif objective_state == OBJ_PICKED:
            # Check if player returned to spawn
            spawn_rect = pygame.Rect(
                spawn_x - 20, spawn_y - 20, 40, 40
            )
            if player_rect.colliderect(spawn_rect):
                objective_state = OBJ_COMPLETE

        # --- Update guards (only if level not complete) ---
        if objective_state != OBJ_COMPLETE:
            guard_manager.update(player_rect, dt)

        # --- Draw everything ---
        screen.fill((20, 20, 40))                              # Dark game background
        wall_manager.draw(screen)                               # Walls
        wall_manager.draw_level_name(screen)                    # Level name HUD

        # Draw spawn point marker (return target when carrying objective)
        if objective_state == OBJ_PICKED:
            # Pulsing spawn marker
            pulse_alpha = int(120 + 80 * math.sin(objective_pulse))
            spawn_surface = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.rect(spawn_surface, (0, 255, 100, pulse_alpha), (0, 0, 44, 44), 3)
            screen.blit(spawn_surface, (spawn_x - 22, spawn_y - 22))
            # "RETURN" text
            try:
                hint_font = pygame.font.Font(None, 20)
            except Exception:
                hint_font = pygame.font.SysFont("arial", 14)
            hint_text = hint_font.render("RETURN", True, (0, 255, 100))
            screen.blit(hint_text, (spawn_x - hint_text.get_width() // 2, spawn_y - 35))

        # Draw objective (if not picked up yet)
        if objective_state == OBJ_WAITING:
            # Glowing diamond shape
            glow = int(8 + 4 * math.sin(objective_pulse))
            glow_color = (
                255,
                200 + int(55 * math.sin(objective_pulse)),
                0,
                100 + int(50 * math.sin(objective_pulse * 0.7)),
            )
            # Glow circle
            glow_surface = pygame.Surface((glow * 4, glow * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow * 2, glow * 2), glow * 2)
            screen.blit(glow_surface, (obj_x - glow * 2, obj_y - glow * 2))
            # Diamond
            diamond_points = [
                (obj_x, obj_y - 12),
                (obj_x + 10, obj_y),
                (obj_x, obj_y + 12),
                (obj_x - 10, obj_y),
            ]
            pygame.draw.polygon(screen, (255, 215, 0), diamond_points)
            pygame.draw.polygon(screen, (255, 255, 200), diamond_points, 2)

        # Draw "carrying" indicator near player when objective is picked
        if objective_state == OBJ_PICKED:
            mini_diamond = [
                (player_x + player_size + 8, player_y - 4),
                (player_x + player_size + 14, player_y + 2),
                (player_x + player_size + 8, player_y + 8),
                (player_x + player_size + 2, player_y + 2),
            ]
            pygame.draw.polygon(screen, (255, 215, 0), mini_diamond)

        guard_manager.draw(screen)                              # Guards + vision cones

        # Draw player with texture or fallback cyan rect
        if player_texture is not None:
            scaled_player = pygame.transform.scale(player_texture, (player_size + 4, player_size + 4))
            angle_deg = -math.degrees(player_facing_angle)
            rotated_player = pygame.transform.rotate(scaled_player, angle_deg)
            player_tex_rect = rotated_player.get_rect(
                center=(int(player_x + player_size // 2), int(player_y + player_size // 2))
            )
            screen.blit(rotated_player, player_tex_rect)
            # Subtle cyan glow ring around player
            pygame.draw.circle(
                screen, (0, 200, 255),
                (int(player_x + player_size // 2), int(player_y + player_size // 2)),
                player_size // 2 + 3, 2
            )
        else:
            pygame.draw.rect(screen, (0, 200, 255), player_rect)   # Player (cyan)

        # --- HUD: objective status ---
        try:
            hud_font = pygame.font.Font(None, 24)
        except Exception:
            hud_font = pygame.font.SysFont("arial", 18)

        if objective_state == OBJ_WAITING:
            hud_text = hud_font.render(">> Reach the objective", True, (255, 215, 0))
        elif objective_state == OBJ_PICKED:
            hud_text = hud_font.render(">> Return to start!", True, (0, 255, 100))
        else:
            hud_text = None

        if hud_text:
            screen.blit(hud_text, (WIDTH - hud_text.get_width() - 15, 10))

        # --- Game over overlay ---
        guard_manager.draw_game_over(screen)

        # --- Level complete overlay ---
        if objective_state == OBJ_COMPLETE:
            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            try:
                font_large = pygame.font.Font(None, 72)
                font_small = pygame.font.Font(None, 30)
                font_btn = pygame.font.Font(None, 30)
            except Exception:
                font_large = pygame.font.SysFont("arial", 54)
                font_small = pygame.font.SysFont("arial", 22)
                font_btn = pygame.font.SysFont("arial", 22)

            # Title
            complete_text = font_large.render("LEVEL COMPLETE!", True, (0, 255, 150))
            complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(complete_text, complete_rect)

            # Subtitle
            sub_text = font_small.render(
                f'"{wall_manager.level_name}" cleared!', True, (200, 255, 220)
            )
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            screen.blit(sub_text, sub_rect)

            # Buttons
            mouse_pos = pygame.mouse.get_pos()
            buttons = [
                (btn_restart_rect, "Restart"),
                (btn_next_rect, "Next Level" if current_level < TOTAL_LEVELS else "Play Again"),
                (btn_menu_rect, "Return to Menu"),
            ]
            for btn_rect, btn_label in buttons:
                if btn_rect.collidepoint(mouse_pos):
                    color = (0, 220, 120)
                    text_c = (255, 255, 255)
                else:
                    color = (0, 140, 80)
                    text_c = (210, 210, 210)
                pygame.draw.rect(screen, color, btn_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2, border_radius=8)
                lbl = font_btn.render(btn_label, True, text_c)
                lbl_rect = lbl.get_rect(center=btn_rect.center)
                screen.blit(lbl, lbl_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
