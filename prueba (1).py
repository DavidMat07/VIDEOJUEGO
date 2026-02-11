import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Prototipo Smash 2D")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

GRAVITY = 0.9

# ---------- PERSONAJES ----------
characters = [
    {"name": "Rápido", "color": (80, 180, 255), "speed": 7, "attack": 5, "jump": -17},
    {"name": "Fuerte", "color": (220, 80, 80), "speed": 4, "attack": 10, "jump": -17},
    {"name": "Equilibrio", "color": (80, 220, 120), "speed": 5, "attack": 7, "jump": -17},
    {"name": "Saltador", "color": (240, 220, 80), "speed": 5, "attack": 6, "jump": -17}
]

# ---------- PLATAFORMA ----------
class Platform:
    def __init__(self, x, y, w, h, solid=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.solid = solid

    def draw(self):
        color = (60, 180, 90) if self.solid else (80, 200, 120)
        pygame.draw.rect(screen, color, self.rect)

# ------------ PLAYER ------------
class Player:
    def __init__(self, x, y, character, controls):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = character["color"]
        self.speed = character["speed"]
        self.attack_power = character["attack"]
        self.jump_force = character["jump"]
        self.controls = controls

        self.vel = pygame.Vector2(0, 0)
        self.knockback = pygame.Vector2(0, 0)

        self.on_ground = False
        self.double_jump = True
        self.facing = 1

        self.damage = 0
        self.hitstun = 0

        # NUEVO: inmunidad tras reaparecer
        self.invulnerable_timer = 0  # en frames

        # Control de salto (evitar doble salto instantáneo)
        self.jump_pressed = False

        # Cooldown de ataque
        self.attack_cooldown = 0

    def get_attack_dir(self, keys):
        d = pygame.Vector2(0, 0)
        if keys[self.controls["left"]]: d.x = -1
        if keys[self.controls["right"]]: d.x = 1
        if keys[self.controls["up"]]: d.y = -1
        if keys[self.controls["down"]]: d.y = 1
        if d.length() == 0:
            d.x = self.facing
        return d.normalize()

    def attack(self, other, keys):
        if self.attack_cooldown > 0:
            return
        hitbox = self.rect.inflate(40, 40)
        if hitbox.colliderect(other.rect) and other.hitstun == 0:
            direction = self.get_attack_dir(keys)
            other.receive_hit(direction, self.attack_power)
            self.attack_cooldown = 20  # Cooldown de ~0.33 segundos

    def receive_hit(self, direction, power):
        # Ignorar daño si está invulnerable
        if self.invulnerable_timer > 0:
            return
        self.damage = min(self.damage + 8 * power / 5, 200)
        force = 6 + self.damage * 0.12
        self.knockback = direction * force
        self.hitstun = 15

    def update(self, platforms, keys):
        prev_bottom = self.rect.bottom
        prev_jump_pressed = self.jump_pressed  # Guardar estado anterior

        # Gravedad normal (invulnerabilidad no afecta física)
        gravity = GRAVITY

        if self.hitstun > 0:
            self.rect.x += int(self.knockback.x)
            self.rect.y += int(self.knockback.y)
            self.knockback.y += gravity * 0.4
            self.hitstun -= 1
        else:
            self.vel.x = 0
            if keys[self.controls["left"]]:
                self.vel.x = -self.speed
                self.facing = -1
            if keys[self.controls["right"]]:
                self.vel.x = self.speed
                self.facing = 1

            self.vel.y += gravity
            self.rect.x += self.vel.x
            self.rect.y += self.vel.y

        # Actualizar estado actual al final
        self.jump_pressed = keys[self.controls["jump"]]

        self.on_ground = False

        for p in platforms:
            if self.rect.colliderect(p.rect):
                # Plataformas no sólidas: solo colisión desde arriba
                # Plataformas sólidas: colisión completa
                if self.vel.y >= 0 and prev_bottom <= p.rect.top:
                    self.rect.bottom = p.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.double_jump = True  # Resetear doble salto al aterrizar
                    # Resetear knockback al aterrizar
                    if self.hitstun > 0:
                        self.knockback = pygame.Vector2(0, 0)
                        self.hitstun = 0
                elif p.solid:  # Solo colisiones laterales/inferiores en plataformas sólidas
                    if self.vel.x > 0 and self.rect.right > p.rect.left and prev_bottom > p.rect.top:
                        self.rect.right = p.rect.left
                    elif self.vel.x < 0 and self.rect.left < p.rect.right and prev_bottom > p.rect.top:
                        self.rect.left = p.rect.right

        # AHORA procesar salto (después de colisiones, cuando on_ground está correcto)
        if self.hitstun == 0:  # Solo saltar si no estás en hitstun
            jump_key = keys[self.controls["jump"]]
            if jump_key and not prev_jump_pressed:  # Transición de False a True
                if self.on_ground:
                    self.vel.y = self.jump_force
                elif self.double_jump:
                    self.vel.y = self.jump_force
                    self.double_jump = False

        if (self.rect.top > HEIGHT or
            self.rect.left < -120 or
            self.rect.right > WIDTH + 120 or
            self.rect.bottom < -150):
            self.respawn()
            return  # Salir para evitar colisiones en el frame de respawn

        # Reducir el timer de inmunidad
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # Reducir cooldown de ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def respawn(self):
        self.rect.center = (WIDTH // 2, 200)
        self.vel = pygame.Vector2(0, 0)
        self.knockback = pygame.Vector2(0, 0)
        self.damage = 0
        self.hitstun = 0
        self.invulnerable_timer = 180  # 3 segundos de inmunidad a 60 FPS
        self.jump_pressed = False
        self.double_jump = True  # Resetear doble salto
        self.attack_cooldown = 0
        self.on_ground = True  # Empezar en el suelo

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        dmg = font.render(f"{int(self.damage)}%", True, (0, 0, 0))
        screen.blit(dmg, (self.rect.centerx - 14, self.rect.top - 22))

# -------- PLATAFORMAS --------
platforms = [
    Platform(100, 460, 800, 35, solid=True),
    Platform(260, 330, 200, 20, solid=False),
    Platform(540, 270, 200, 20, solid=False)
]

# -------- CONTROLES --------
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

# -------- MENÚ PRINCIPAL --------
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
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if vs_button.collidepoint(mx, my):
                    selected_mode = "VERSUS"
                    menu_running = False
                elif train_button.collidepoint(mx, my):
                    selected_mode = "ENTRENAMIENTO"
                    menu_running = False

        pygame.display.flip()
        clock.tick(60)
    return selected_mode

# -------- MENÚ DE SELECCIÓN DE PERSONAJE --------
def character_menu(player_num):
    menu_running = True
    selected_char = None
    while menu_running:
        # Diferenciar color de fondo según jugador
        screen.fill((180, 220, 255) if player_num == 1 else (255, 180, 180))

        mx, my = pygame.mouse.get_pos()

        spacing = 200
        start_x = WIDTH//2 - 300
        y_pos = 200
        buttons = []

        for i, char in enumerate(characters):
            rect = pygame.Rect(start_x + i*spacing, y_pos, 100, 100)
            pygame.draw.rect(screen, char["color"], rect)

            # Nombre y stats
            name_text = font.render(char["name"], True, (0,0,0))
            speed_text = font.render(f"Vel: {char['speed']}", True, (0,0,0))
            attack_text = font.render(f"Ataq: {char['attack']}", True, (0,0,0))
            jump_text = font.render(f"Salto: {-char['jump']}", True, (0,0,0))

            screen.blit(name_text, (rect.centerx - name_text.get_width()//2, rect.bottom + 5))
            screen.blit(speed_text, (rect.centerx - speed_text.get_width()//2, rect.bottom + 25))
            screen.blit(attack_text, (rect.centerx - attack_text.get_width()//2, rect.bottom + 45))
            screen.blit(jump_text, (rect.centerx - jump_text.get_width()//2, rect.bottom + 65))

            buttons.append((rect, char))

        info_text = font.render(f"Jugador {player_num}, selecciona tu personaje", True, (0,0,0))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, char in buttons:
                    if rect.collidepoint(mx, my):
                        selected_char = char
                        menu_running = False

        pygame.display.flip()
        clock.tick(60)
    return selected_char

# -------- DUMMY PARA ENTRENAMIENTO --------
class Dummy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = (150, 150, 150)
        self.damage = 0
        self.hitstun = 0
        self.knockback = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)
        self.invulnerable_timer = 0
        self.start_x = x
        self.start_y = y

    def receive_hit(self, direction, power):
        self.damage = min(self.damage + 8 * power / 5, 200)
        force = 6 + self.damage * 0.12
        self.knockback = direction * force
        self.hitstun = 15

    def update(self, platforms):
        prev_bottom = self.rect.bottom

        if self.hitstun > 0:
            self.rect.x += int(self.knockback.x)
            self.rect.y += int(self.knockback.y)
            self.knockback.y += GRAVITY * 0.4
            self.hitstun -= 1
        else:
            self.vel.y += GRAVITY
            self.rect.y += self.vel.y

        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel.y >= 0 and prev_bottom <= p.rect.top:
                    self.rect.bottom = p.rect.top
                    self.vel.y = 0
                    if self.hitstun > 0:
                        self.knockback = pygame.Vector2(0, 0)
                        self.hitstun = 0

        # Respawn si sale de pantalla
        if (self.rect.top > HEIGHT or
            self.rect.left < -120 or
            self.rect.right > WIDTH + 120):
            self.rect.center = (self.start_x, self.start_y)
            self.vel = pygame.Vector2(0, 0)
            self.knockback = pygame.Vector2(0, 0)
            self.damage = 0
            self.hitstun = 0

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        dmg = font.render(f"{int(self.damage)}%", True, (0, 0, 0))
        screen.blit(dmg, (self.rect.centerx - 14, self.rect.top - 22))
        label = font.render("DUMMY", True, (100, 100, 100))
        screen.blit(label, (self.rect.centerx - label.get_width()//2, self.rect.bottom + 5))

# -------- INICIO DEL JUEGO --------
def start_game():
    mode = main_menu()

    # Selección de P1
    p1_char = character_menu(1)
    p1 = Player(350, 200, p1_char, p1_controls)

    # Selección de P2 solo si VERSUS, o crear dummy para entrenamiento
    p2 = None
    dummy = None
    if mode == "VERSUS":
        p2_char = character_menu(2)
        p2 = Player(600, 200, p2_char, p2_controls)
    else:
        dummy = Dummy(600, 200)

    running = True
    while running:
        clock.tick(60)
        screen.fill((245, 245, 245))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

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

        for p in platforms:
            p.draw()

        p1.draw()
        if p2:
            p2.draw()
        elif dummy:
            dummy.draw()

        pygame.display.flip()

# ------------ LOOP PRINCIPAL ------------
while True:
    start_game()
