from sys import exit

import pygame.time, time

from variables import *
import function
import menu

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Test')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)

pygame.mixer.music.load('Songs/Mesmerizer/Mesmerizer.mp3')
pygame.mixer_music.set_volume(0.1)

playlane_obj = pygame.Surface(((WIDTH / 10) - 10, HEIGHT))
playlane_obj.fill('White')

text_surf = font.render('Rhythm Game Ah', False, 'White')
text_rect = text_surf.get_rect(topleft=(20,20))

minus_speed = font.render('-', False, 'White')
minus_speed_rect = minus_speed.get_rect(topleft=(20,120))

add_speed = font.render('+', False, 'White')
add_speed_rect = add_speed.get_rect(topleft=(40,120))

class Beatline:
    def __init__(self,y = 0):
        self.bpm = 60000 / bpm
        self.y = y

    def main(self):
        self.scroll()
        self.draw()

    def scroll(self):
        self.y += speed * fps * dt

    def draw(self):
        for timing in range(0,401):
            pygame.draw.line(screen, pygame.Color('Gray'), (LANE[1][0], (self.y - timing * (self.bpm * speed / 4))),
                             ((LANE[5][0]), (self.y - timing * (self.bpm * speed / 4))), 5)


class Note:
    def __init__(self,lane,y,judge,timing,end):
        self.lane = lane
        self.timing = timing
        self.bpmline = 60000 / bpm
        self.y = y * speed
        self.judge = judge
        self.end = end
        self.scrollspeed = speed
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.y > HEIGHT:
            self.kys()

    def printer(self):
        print(str(self.lane),str(self.y),str(self.judge),str(self.end))

    def judgement(self): #t = d/v
        timing_perfect = self.timing
        print(f'Perfect time = {timing_perfect} Lane: {self.lane}')
        print(f'Now = {now}')
        timing_error = abs( - self.judge)

    def hit(self):
        if not self.pressed:
            self.judge = now
            self.pressed = True
            print(self.judgement())
            self.kys()
        return

    def scroll(self):
        self.y += self.scrollspeed * dt * fps

    def draw(self):
        pygame.draw.line(screen,pygame.Color('Red'),(LANE[self.lane][0], self.y),
                         (LANE[self.lane+1][0], self.y), 20)

    def kys(self):
        notes.remove(self)

class Lane:
    def __init__(self,num,keystate,ispressed,waspressed):
        self.num = num
        self.keystate = keystate
        self.ispressed = ispressed
        self.waspressed = waspressed

    def main(self): #Continuous function
        self.key_check()
        self.light_up()

    def booldown(self):
        return self.ispressed

    def key_down(self):
        self.keystate = True

    def key_up(self):
        self.keystate = False
        self.ispressed = False

    def key_check(self): #Sends signal when first time pressing or release
        if self.waspressed and self.keystate == False:
            # print(f'Lane {self.num} Up')
            self.waspressed = False

        if self.keystate and self.ispressed == False:
            # print(f'Lane {self.num} Down')
            self.waspressed = True
            self.ispressed = True
            for notedown in notes:
                if notedown.lane == self.num:
                    notedown.hit()
                    return

    def light_up(self):
        if self.waspressed:
            temp_rect = pygame.Rect(LANE[self.num][0], 100, 100, HEIGHT - (HEIGHT - judge_line) - 100)
            function.gradientRect(screen, pygame.Color((200,200,200)), pygame.Color((30, 30, 30)), temp_rect)

beatline = Beatline()
LANE1 = Lane(1,False,False,False)
LANE2 = Lane(2,False,False,False)
LANE3 = Lane(3,False,False,False)
LANE4 = Lane(4,False,False,False)

combo = 0
notes = []

menu.main_menu()
notes.clear()
with open('Songs/Mesmerizer/Mesmerizer', 'r') as f:
    for line in f:
        if not line.strip().startswith('#'):
            x = list(map(int,(line.strip().split(','))))
            notes.append(Note(*x))
# read chart script add to notes list
print('Start')
pygame.key.set_repeat(0,0)
previous_time = time.time()
pygame.mixer.music.play()
running = True

while running:
    dt = time.time() - previous_time
    previous_time = time.time()
    screen.fill((30, 30, 30))
    now = pygame.mixer.music.get_pos()

    if pygame.mixer.music.get_pos() == -1:
        pass
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEMOTION:
            mx,     my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if minus_speed_rect.collidepoint(mx, my):
                speed -= 1
            if add_speed_rect.collidepoint(mx, my):
                speed += 1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d: LANE1.key_down()
            if event.key == pygame.K_f: LANE2.key_down()
            if event.key == pygame.K_j: LANE3.key_down()
            if event.key == pygame.K_k: LANE4.key_down()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d: LANE1.key_up()
            if event.key == pygame.K_f: LANE2.key_up()
            if event.key == pygame.K_j: LANE3.key_up()
            if event.key == pygame.K_k: LANE4.key_up()

    LANE1.main(), LANE2.main(), LANE3.main(), LANE4.main()
    beatline.main()

    if now > 0:
        for note in notes:
            note.main()

    pygame.draw.line(screen, pygame.Color('Green'), (LANE[1][0], judge_line), ((LANE[5][0]), judge_line), 5)
    for i in range(0, 5):
        pygame.draw.line(screen, pygame.Color('White'), ((WIDTH / 3) + i * 100, 0), ((WIDTH / 3) + i * 100, HEIGHT), 5)

    screen.blit(text_surf,text_rect)

    combo_img = font.render(f"{combo}", True, (255, 222, 0))
    combo_rect = combo_img.get_rect(center=(LANE[3][0],(HEIGHT-(HEIGHT-judge_line))/2))
    screen.blit(combo_img, combo_rect)

    speed_text = font.render(f'Speed: {speed}', False, 'White')
    speed_rect = speed_text.get_rect(topleft=(20, 80))
    screen.blit(speed_text, speed_rect)

    screen.blit(add_speed,add_speed_rect)
    screen.blit(minus_speed,minus_speed_rect)

    pygame.display.update()
    clock.tick(fps)