from tkinter import font

import pygame

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
        pygame.draw.rect(screen, (0,255,0), (100,100,50,50))
        pygame.mixer.music.stop()
    pygame.display.update()
    clock.tick(60)

pygame.quit()