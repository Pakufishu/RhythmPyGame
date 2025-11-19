import pygame

# --- Interface ---
WIDTH, HEIGHT = 1080 , 720
JUDGE_LINE = HEIGHT - 100
fps = 60
speed = 18
songoffset = 0
bpm = 185
now = 0
swipe_cd = 0
mx, my = 0,0
judgement_fadeout = 10
firstnote_clicked = False

# --- Lane stuff ---
LANE = {
1 : ((WIDTH / 3) , 0),
2 : ((WIDTH / 3) + 100, 0),
3 : ((WIDTH / 3) + 200, 0),
4 : ((WIDTH / 3) + 300, 0),
5 : ((WIDTH / 3) + 400, 0)
}

KEYS = {
    pygame.K_d : LANE[1],
    pygame.K_f : LANE[2],
    pygame.K_j : LANE[3],
    pygame.K_k : LANE[4],
}

# --- Colors ---
judgecolor = {
    'MARVELOUS': pygame.Color('White'),
    'PERFECT': pygame.Color('Orange'),
    'GREAT': pygame.Color('Pink'),
    'GOOD': pygame.Color('Green'),
    'MISS': pygame.Color('Red'),
}

diffcolor = {
    'Ez': pygame.Color(51, 204, 255),
    'Adv': pygame.Color(255, 238, 0),
    'Exp': pygame.Color('Red'),
    'Mas': pygame.Color('Purple'),
}

# --- Folders ---

SONGS_FOLDER = 'Songs'
SFX_FOLDER = 'sfx'