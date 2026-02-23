import pygame
from settings import GRAVITY, screen, font

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

        if (self.rect.top > 600 or self.rect.left < -120 or self.rect.right > 1000+120):
            self.rect.center = (self.start_x, self.start_y)
            self.vel = pygame.Vector2(0, 0)
            self.knockback = pygame.Vector2(0, 0)
            self.damage = 0
            self.hitstun = 0

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        dmg = font.render(f"{int(self.damage)}%", True, (0,0,0))
        screen.blit(dmg, (self.rect.centerx - 14, self.rect.top - 22))
        label = font.render("DUMMY", True, (100,100,100))
        screen.blit(label, (self.rect.centerx - label.get_width()//2, self.rect.bottom + 5))
