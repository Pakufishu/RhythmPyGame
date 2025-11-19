import sys
import os
import pygame
import dir
from variables import *
import menu

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Rhythm Game")

songsdict = dir.getsongdict()
img = pygame.image.load('Songs/Mesmerizer/Mesmerizer_art.png').convert_alpha()
cover_art = pygame.transform.scale(img, (HEIGHT*3.5 // 7, HEIGHT*3.5 // 7))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    menu.main_menu()


    pygame.display.update()
