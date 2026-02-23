import pygame
from settings import screen

class Platform:
    def __init__(self, x, y, w, h, solid=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.solid = solid

    def draw(self):
        color = (60, 180, 90) if self.solid else (80, 200, 120)
        pygame.draw.rect(screen, color, self.rect)
