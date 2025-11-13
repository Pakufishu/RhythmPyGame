import sys
import os
import math
from variables import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Rhythm Game Menu")

TEXT_COLOR = (220, 240, 255)   # ice white-blue
HOVER_COLOR = (255, 255, 0)    # yellow for hover
BASE_GLOW = (0, 200, 255)      # neon cyan
BG_COLOR = (10, 10, 20)        # deep navy

font_title = pygame.font.SysFont(None, 100)  # Title size
font_button = pygame.font.SysFont(None, 60)  # Button sized

screen = pygame.display.set_mode((WIDTH, HEIGHT))
movement = 1
scale = 0
x = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for j in range(80):
        for i in range(-120, 120):
            surf = pygame.Surface((abs(20 - j), abs(20 - j))).convert_alpha()
            surf.fill(pygame.Color("white"))
            screen.blit(surf, ((WIDTH/2 + i * 45) + x, (j * 45) + x))

    pygame.display.flip()