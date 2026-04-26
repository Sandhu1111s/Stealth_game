from tkinter import font
import math

import pygame
from Gaurd import GuardManager
from Walls import WallManager, TOTAL_LEVELS

pygame.init()
pygame.mixer.init()
WIDTH , HEIGHT = 800, 600
bg = pygame.image.load("newbg/new.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
menu_music_loaded = False
try:
    pygame.mixer.music.load("assests/mu.mp3")
    menu_music_loaded = True
except Exception:
    menu_music_loaded = False



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
OBJ_WAITING = 0     
OBJ_PICKED = 1     
OBJ_COMPLETE = 2      
objective_state = OBJ_WAITING
objective_size = 20
objective_pulse = 0.0  # For glowing animation
RETURN_TIME_LIMIT = 15.0
RETURN_WARNING_TIME = 5.0
return_time_left = 0.0

# Level complete buttons
btn_w, btn_h = 180, 45
btn_gap = 20
btn_restart_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50, btn_w, btn_h)
btn_next_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50 + btn_h + btn_gap, btn_w, btn_h)
btn_menu_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 50 + 2 * (btn_h + btn_gap), btn_w, btn_h)

# Wall & guard system
wall_manager = WallManager(WIDTH, HEIGHT)
guard_manager = GuardManager(WIDTH, HEIGHT, wall_manager=wall_manager)


def load_level(level_num):
    """Load a level — sets up walls, guards, player spawn, and objective."""
    global player_x, player_y, guard_manager, objective_state, return_time_left

    guard_configs = wall_manager.load_level(level_num)
    player_x, player_y = wall_manager.player_spawn
    objective_state = OBJ_WAITING
    return_time_left = 0.0

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
        if menu_music_loaded and not pygame.mixer.music.get_busy():
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
        if menu_music_loaded and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        dt = clock.get_time() / 1000.0  
        objective_pulse += dt * 3 

     
        if not guard_manager.game_over and objective_state != OBJ_COMPLETE:
            keys = pygame.key.get_pressed()
            old_px, old_py = player_x, player_y  
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += player_speed

            player_x = max(0, min(player_x, WIDTH - player_size))
            player_y = max(0, min(player_y, HEIGHT - player_size))

            player_x, player_y = wall_manager.clamp_player_movement(
                old_px, old_py, player_x, player_y, player_size
            )

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

      
        obj_x, obj_y = wall_manager.objective_pos
        spawn_x, spawn_y = wall_manager.player_spawn

        if objective_state == OBJ_WAITING:
            
            obj_rect = pygame.Rect(
                obj_x - objective_size // 2, obj_y - objective_size // 2,
                objective_size, objective_size
            )
            if player_rect.colliderect(obj_rect):
                objective_state = OBJ_PICKED
                return_time_left = RETURN_TIME_LIMIT

        elif objective_state == OBJ_PICKED:
            return_time_left -= dt

            if return_time_left <= 0:
                # Timer expired: trigger game over.
                guard_manager.game_over = True
                return_time_left = 0.0

            if not guard_manager.game_over:
                # Check if player returned to spawn
                spawn_rect = pygame.Rect(
                    spawn_x - 20, spawn_y - 20, 40, 40
                )
                if player_rect.colliderect(spawn_rect):
                    objective_state = OBJ_COMPLETE
                    return_time_left = 0.0

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

        if objective_state == OBJ_PICKED:
            timer_color = (255, 220, 120)
            if return_time_left <= RETURN_WARNING_TIME:
                # Flash red warning when time is about to expire.
                timer_color = (255, 70, 70) if int(objective_pulse * 6) % 2 == 0 else (255, 180, 180)

            timer_text = hud_font.render(f"Return in: {max(0.0, return_time_left):.1f}s", True, timer_color)
            screen.blit(timer_text, (15, HEIGHT - timer_text.get_height() - 15))

            if return_time_left <= RETURN_WARNING_TIME:
                warning_font = pygame.font.Font(None, 34)
                warning_text = warning_font.render("WARNING: RETURN NOW!", True, (255, 60, 60))
                screen.blit(warning_text, (WIDTH // 2 - warning_text.get_width() // 2, 45))

        guard_manager.draw_game_over(screen)

    
        if objective_state == OBJ_COMPLETE:
       
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

            is_final_level = current_level >= TOTAL_LEVELS

            # Title
            title_label = "CONGRATULATIONS! YOU WON" if is_final_level else "LEVEL COMPLETE!"
            complete_text = font_large.render(title_label, True, (0, 255, 150))
            complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(complete_text, complete_rect)

            # Subtitle
            subtitle_label = (
                "All levels completed! Great stealth run."
                if is_final_level
                else f'"{wall_manager.level_name}" cleared!'
            )
            sub_text = font_small.render(subtitle_label, True, (200, 255, 220))
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
