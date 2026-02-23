import pygame
from settings import GRAVITY, screen, font

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
        self.invulnerable_timer = 0
        self.jump_pressed = False
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
        if hitbox.colliderect(other.rect) and getattr(other, "hitstun", 0) == 0:
            direction = self.get_attack_dir(keys)
            other.receive_hit(direction, self.attack_power)
            self.attack_cooldown = 20

    def receive_hit(self, direction, power):
        if self.invulnerable_timer > 0:
            return
        self.damage = min(self.damage + 8 * power / 5, 200)
        force = 6 + self.damage * 0.12
        self.knockback = direction * force
        self.hitstun = 15

    def update(self, platforms, keys):
        prev_bottom = self.rect.bottom
        prev_jump_pressed = self.jump_pressed
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

        self.jump_pressed = keys[self.controls["jump"]]
        self.on_ground = False

        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel.y >= 0 and prev_bottom <= p.rect.top:
                    self.rect.bottom = p.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.double_jump = True
                    if self.hitstun > 0:
                        self.knockback = pygame.Vector2(0, 0)
                        self.hitstun = 0
                elif p.solid:
                    if self.vel.x > 0 and self.rect.right > p.rect.left and prev_bottom > p.rect.top:
                        self.rect.right = p.rect.left
                    elif self.vel.x < 0 and self.rect.left < p.rect.right and prev_bottom > p.rect.top:
                        self.rect.left = p.rect.right

        if self.hitstun == 0:
            jump_key = keys[self.controls["jump"]]
            if jump_key and not prev_jump_pressed:
                if self.on_ground:
                    self.vel.y = self.jump_force
                elif self.double_jump:
                    self.vel.y = self.jump_force
                    self.double_jump = False

        if (self.rect.top > 600 or self.rect.left < -120 or self.rect.right > 1000+120 or self.rect.bottom < -150):
            self.respawn()

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def respawn(self):
        self.rect.center = (500, 200)
        self.vel = pygame.Vector2(0, 0)
        self.knockback = pygame.Vector2(0, 0)
        self.damage = 0
        self.hitstun = 0
        self.invulnerable_timer = 180
        self.jump_pressed = False
        self.double_jump = True
        self.attack_cooldown = 0
        self.on_ground = True

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        dmg = font.render(f"{int(self.damage)}%", True, (0,0,0))
        screen.blit(dmg, (self.rect.centerx - 14, self.rect.top - 22))
