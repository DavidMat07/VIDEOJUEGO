import pygame

WIDTH, HEIGHT = 1000, 600
GRAVITY = 0.9

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Prototipo Smash 2D")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)
