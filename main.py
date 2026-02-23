import pygame
import sys
from settings import WIDTH, HEIGHT, screen, clock, GRAVITY
from player import Player
from dummy import Dummy
from maps import maps
from menus import main_menu, character_menu, map_menu
from platform import Platform

# Controles
p1_controls = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "up": pygame.K_w,
    "down": pygame.K_s,
    "jump": pygame.K_SPACE,
    "attack": pygame.K_f
}

p2_controls = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "jump": pygame.K_RSHIFT,
    "attack": pygame.K_KP0
}


def start_game():
    mode = main_menu()

    # Selección de personajes
    p1_char = character_menu(1)
    p1 = Player(350, 200, p1_char, p1_controls)

    p2 = None
    dummy = None
    if mode == "VERSUS":
        p2_char = character_menu(2)
        p2 = Player(600, 200, p2_char, p2_controls)
    else:
        dummy = Dummy(600, 200)

    # --- Selección de mapa ---
    selected_map = map_menu()
    platforms = selected_map["platforms"]
    bg_color = selected_map["bg_color"]

    running = True
    while running:
        clock.tick(60)
        screen.fill(bg_color)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Volver al menú principal

        # Actualizar jugadores
        if p2:
            if keys[p1_controls["attack"]]:
                p1.attack(p2, keys)
            if keys[p2_controls["attack"]]:
                p2.attack(p1, keys)
            p2.update(platforms, keys)
        elif dummy:
            if keys[p1_controls["attack"]]:
                p1.attack(dummy, keys)
            dummy.update(platforms)

        p1.update(platforms, keys)

        # Dibujar plataformas
        for p in platforms:
            p.draw()

        # Dibujar jugadores
        p1.draw()
        if p2:
            p2.draw()
        elif dummy:
            dummy.draw()

        pygame.display.flip()


# LOOP PRINCIPAL
while True:
    start_game()
