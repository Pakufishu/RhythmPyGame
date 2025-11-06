import sys
import time
import pygame
from pygame import MOUSEMOTION

pygame.init()
screen = pygame.display.set_mode((600, 600))

pygame.mixer.music.load('Songs/Mesmerizer/Mesmerizer.mp3')
pygame.mixer_music.set_volume(0.1)
bpm = 185
speed = 5
swipe_cd = 0

class Metronome:
    def __init__(self):
        self.bpm = bpm

    def bpmcheck(self):
        x = round(60000/self.bpm,2)
        print("BPM is: " + str(x))

previous_time = time.time()
pygame.key.set_repeat(1,0)

while True:
    now = time.time()
    dt = now - previous_time
    previous_time = time.time()

    screen.fill(pygame.Color('Black'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    metronome = Metronome()
    metronome.bpmcheck()

    pygame.display.update()
    pygame.time.Clock().tick(60)