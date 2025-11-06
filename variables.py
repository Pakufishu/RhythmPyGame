import pygame

WIDTH, HEIGHT = 1080 , 720
fps = 60
speed = 8
judge_line = HEIGHT - 100 #620
songoffset = 0
bpm = 185
now = 0
swipe_cd = 0
judgement_fadeout = 10
firstnote_clicked = False

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