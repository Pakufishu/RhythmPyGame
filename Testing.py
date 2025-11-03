import sys
import time
import pygame

pygame.init()
screen = pygame.display.set_mode((600, 600))

tbpm = round(60000 / 185)
speed = 5
y = 1
print(tbpm)
pygame.key.set_repeat(1,0)
while True:
    screen.fill(pygame.Color('Black'))
    y += speed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    for i in range(0,100):
        pygame.draw.line(screen,pygame.Color('White'),(0,y+i*-(100*speed)),(600,y+i*-(100*speed)),5)

    pygame.display.update()
    pygame.time.Clock().tick(60)