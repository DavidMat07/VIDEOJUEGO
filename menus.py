import pygame
from settings import screen, font, WIDTH, HEIGHT
from characters import characters
from maps import maps

def main_menu():
    menu_running = True
    selected_mode = None
    while menu_running:
        screen.fill((200, 200, 200))
        mx, my = pygame.mouse.get_pos()

        vs_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)
        train_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)

        pygame.draw.rect(screen, (150, 150, 250), vs_button)
        pygame.draw.rect(screen, (150, 250, 150), train_button)

        vs_text = font.render("VERSUS", True, (0,0,0))
        train_text = font.render("ENTRENAMIENTO", True, (0,0,0))
        info_text = font.render("Pulsa ESC durante el juego para volver al menú", True, (0,0,0))

        screen.blit(vs_text, (vs_button.centerx - vs_text.get_width()//2, vs_button.centery - 10))
        screen.blit(train_text, (train_button.centerx - train_text.get_width()//2, train_button.centery - 10))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if vs_button.collidepoint(mx, my):
                    selected_mode = "VERSUS"
                    menu_running = False
                elif train_button.collidepoint(mx, my):
                    selected_mode = "ENTRENAMIENTO"
                    menu_running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)
    return selected_mode


def character_menu(player_num):
    menu_running = True
    selected_char = None
    while menu_running:
        screen.fill((180, 220, 255) if player_num == 1 else (255, 180, 180))
        mx, my = pygame.mouse.get_pos()

        spacing = 200
        start_x = WIDTH//2 - 300
        y_pos = 200
        buttons = []

        for i, char in enumerate(characters):
            rect = pygame.Rect(start_x + i*spacing, y_pos, 100, 100)
            pygame.draw.rect(screen, char["color"], rect)

            name_text = font.render(char["name"], True, (0,0,0))
            screen.blit(name_text, (rect.centerx - name_text.get_width()//2, rect.bottom + 5))
            buttons.append((rect, char))

        info_text = font.render(f"Jugador {player_num}, selecciona tu personaje", True, (0,0,0))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, char in buttons:
                    if rect.collidepoint(mx, my):
                        selected_char = char
                        menu_running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)
    return selected_char


def map_menu():
    while True:
        screen.fill((200, 200, 200))
        mx, my = pygame.mouse.get_pos()

        title = font.render("Selecciona el mapa", True, (0,0,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        y = 150
        for m in maps:
            rect = pygame.Rect(WIDTH//2 - 150, y, 300, 50)
            pygame.draw.rect(screen, (160,160,240), rect)
            text = font.render(m["name"], True, (0,0,0))
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - 10))

            if pygame.mouse.get_pressed()[0] and rect.collidepoint(mx, my):
                return m
            y += 70

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)
