from tkinter import font

import pygame
from Gaurd import GuardManager

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

# Player setup
player_x, player_y = 100, 500
player_speed = 4
player_size = 30

# Guard system
guard_manager = GuardManager(WIDTH, HEIGHT)
guard_manager.create_default_guards()

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
                if event.key == pygame.K_ESCAPE:
                    running = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_rect.collidepoint(event.pos):
                    state = GAME 
                if quit_rect.collidepoint(event.pos):
                    running = False

        if state == GAME:
            if guard_manager.handle_event(event):
                # Restart the game
                player_x, player_y = 100, 500
                guard_manager.reset()
    

        

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

        # --- Player movement (WASD or arrow keys) ---
        if not guard_manager.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += player_speed

            # Keep player on screen
            player_x = max(0, min(player_x, WIDTH - player_size))
            player_y = max(0, min(player_y, HEIGHT - player_size))

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # --- Update guards ---
        guard_manager.update(player_rect, dt)

        # --- Draw everything ---
        screen.fill((20, 20, 40))                              # Dark game background
        guard_manager.draw(screen)                              # Guards + vision circles
        pygame.draw.rect(screen, (0, 200, 255), player_rect)   # Player (cyan)
        guard_manager.draw_game_over(screen)                    # Game over overlay
    pygame.display.update()
    clock.tick(60)

pygame.quit()
