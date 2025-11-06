from sys import exit

import pygame.time, time

from variables import *
import function
import menu

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Rhythm Game')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)
bigfont = pygame.font.SysFont(None, 100)

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

class Metronome:
    def __init__(self):
        self.bpm = bpm

class Beatline:
    def __init__(self,y = 0):
        self.bpm = 60000 / bpm
        self.y = y

    def main(self):
        self.scroll()
        self.draw()

    def scroll(self):
        self.y += speed

    def draw(self):
        for timing in range(0,401):
            if timing % 4 != 0:
                pygame.draw.line(screen, pygame.Color('Gray'),
                                 (LANE[1][0], (self.y - timing * (self.bpm * speed / 16))),
                                 ((LANE[5][0]), (self.y - timing * (self.bpm * speed / 16))), 5)
            pygame.draw.line(screen, pygame.Color('Red'),
                             (LANE[1][0], (self.y - timing * (self.bpm * speed / 4))),
                             ((LANE[5][0]), (self.y - timing * (self.bpm * speed / 4))), 5)

class Note:
    def __init__(self,lane,y,judge,timing,end):
        self.lane = lane
        self.timing = timing
        self.bpm = 60000 / bpm
        self.y = y * speed
        self.judge = judge
        self.end = end
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.y > HEIGHT:
            self.kys()
            judges.append('Miss')

    def judgement(self): #t = d/v
        timing_error = abs(self.timing - self.judge)
        if timing_error < 0.25:
            if timing_error < 0.01667: judge = 'Critical Perfect'
            elif timing_error < 0.04333: judge = 'Perfect'
            elif timing_error < 0.07777: judge = 'Great'
            elif timing_error < 0.1: judge = 'Good'
            else: judge = 'Miss'
            print(f'Perfect time = {self.timing} Lane: {self.lane}')
            print(f'Now = {self.judge}')
            judges.append(judge)
            return True
        return False

    def hit(self):
        if not self.pressed:
            self.judge = elapsed_time
            if self.judgement():
                self.pressed = True
                self.kys()
        return

    def release(self):
        pass

    def scroll(self):
        self.y += speed * fps * dt

    def draw(self):
        pygame.draw.line(screen,pygame.Color('Red'),(LANE[self.lane][0], self.y),
                         (LANE[self.lane+1][0], self.y), 20)

    def kys(self):
        notes.remove(self)

class Hold:
    def __init__(self,lane,y,judge,timing,end):
        self.lane = lane
        self.timing = timing
        self.bpm = 60000 / bpm
        self.y = y * speed
        self.judge = judge
        self.endjudge = 0
        self.end = end * speed
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.end > HEIGHT:
            self.kys()

    def judgement(self):  # t = d/v
        print(f'Perfect time = {self.timing} Lane: {self.lane}')
        print(f'Start = {self.judge}')
        print(f'End = {self.endjudge}')
        timing_error = abs(self.timing - self.judge)

    def hit(self):
        if not self.pressed:
            self.judge = elapsed_time
            self.pressed = True
            self.judgement()
        return

    def release(self):
        self.endjudge = elapsed_time
        self.judgement()
        self.kys()

    def scroll(self):
        self.y += speed * dt * fps
        self.end += speed * dt * fps

    def draw(self):
        if self.pressed:
            pygame.draw.line(screen, pygame.Color('Red'), (LANE[self.lane][0] + 50, judge_line),
                             (LANE[self.lane][0] + 50, self.end), 80)
            pygame.draw.line(screen, pygame.Color('Red'), (LANE[self.lane][0], self.end),
                             (LANE[self.lane + 1][0], self.end), 20)
            return
        pygame.draw.line(screen,pygame.Color('Red'),(LANE[self.lane][0]+50, self.y),
                         (LANE[self.lane][0]+50, self.end), 80)
        pygame.draw.line(screen,pygame.Color('Red'),(LANE[self.lane][0], self.y),
                         (LANE[self.lane+1][0], self.y), 20)
        pygame.draw.line(screen,pygame.Color('Red'),(LANE[self.lane][0], self.end),
                        (LANE[self.lane+1][0], self.end), 20)

    def kys(self):
        notes.remove(self)

class Swipe:
    def __init__(self,lane,y,judge,timing,side):
        self.lane = lane
        self.timing = timing
        self.bpm = 60000 / bpm
        self.y = y * speed
        self.judge = judge
        self.side = side
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.y > HEIGHT:
            self.kys()

    def judgement(self): #t = d/v
        print(f'Perfect time = {self.timing} Lane: {self.lane}')
        print(f'Now = {self.judge}')
        timing_error = abs(self.timing - self.judge)
        if timing_error < 0.01667:
            judge = 'Critical Perfect'
        elif timing_error < 0.04333:
            judge = 'Perfect'
        elif timing_error < 0.07777:
            judge = 'Great'
        elif timing_error < 0.1:
            judge = 'Good'
        elif timing_error < 0.3:
            judge = 'Miss'
        else:
            print('NOT YET')
            return False
        judge_text = font.render(judge, False, 'Red')
        judge_rect = text_surf.get_rect(center=(LANE[2][0], HEIGHT * 2 /3))
        screen.blit(judge_text, judge_rect)
        return True

    def hit(self):
        if not self.pressed:
            self.judge = elapsed_time
            if self.judgement():
                self.pressed = True
                self.kys()
        return

    def release(self):
        pass

    def scroll(self):
        self.y += speed * dt * fps

    def draw(self):
        pygame.draw.line(screen,pygame.Color('Pink'),(LANE[1][0], self.y),
                         (LANE[5][0], self.y), 20)

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

    def key_down(self):
        self.keystate = True

    def key_up(self):
        self.keystate = False
        self.ispressed = False

    def key_check(self): #Sends signal when first time pressing or release
        if self.waspressed and self.keystate == False:
            # print(f'Lane {self.num} Up')
            self.waspressed = False
            for noteup in notes:
                if noteup.lane == self.num:
                    noteup.release()
                    return

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

combo = 0
notes = []
judges = []

# menu.main_menu()
notes.clear()
judges.clear()

beatline = Beatline()
LANE1 = Lane(1,False,False,False)
LANE2 = Lane(2,False,False,False)
LANE3 = Lane(3,False,False,False)
LANE4 = Lane(4,False,False,False)

# read chart script add node class according to the type to notes list
with open('Songs/Mesmerizer/Mesmerizer', 'r') as f:
    for line in f:
        if not line.strip().startswith('#'):
            x = list(map(float,(line.strip().split(','))))
            if x[4] == 1 or x[4] == 2:
                notes.append(Swipe(*x))
            elif x[4] != 0:
                notes.append(Hold(*x))
            else:
                notes.append(Note(*x))

print('Start game')
pygame.key.set_repeat(0,0)
pygame.mixer.music.play()
running = True
start_time = time.time()
previous_time = time.time()
while running:
    clock.tick(fps)
    now = time.time()
    dt = now - previous_time
    previous_time = time.time()
    music_time = pygame.mixer.music.get_pos()
    if swipe_cd > 0: swipe_cd -= 1
    elapsed_time = round(now - start_time, 4)
    if 1.405 >= round(elapsed_time, 3) >= 1.395:
        print('Start of song')
    screen.fill((30, 30, 30))
    # print(f'Music time: {music_time}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            # movementx, movementy = pygame.mouse.get_rel()
            # if movementx > 40 and swipe_cd == 0:
            #     print('swipe right')
            #     swipe_cd = 5
            # elif movementx < -40 and swipe_cd == 0:
            #     print('swipe left')
            #     swipe_cd = 5
            # pygame.mouse.set_pos((WIDTH/2, HEIGHT/2))
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

    if judgement_fadeout > 0 & firstnote_clicked: judgement_fadeout -= 1
    if judges:
        judge_text = bigfont.render(judges[0], False, 'Red')
        judge_rect = judge_text.get_rect(center=(LANE[3][0], HEIGHT * 2 / 3))
        screen.blit(judge_text, judge_rect)
        if judgement_fadeout == 0:
            judgement_fadeout = 15
        if judgement_fadeout == 1:
            judges.remove(judges[0])
            firstnote_clicked = True


    speed_text = font.render(f'Speed: {speed}', False, 'White')
    speed_rect = speed_text.get_rect(topleft=(20, 80))
    screen.blit(speed_text, speed_rect)

    screen.blit(add_speed,add_speed_rect)
    screen.blit(minus_speed,minus_speed_rect)

    time_text = font.render(f'Time: {elapsed_time}', False, 'Gray')
    time_rect = time_text.get_rect(topleft=(20, 160))
    screen.blit(time_text, time_rect)

    pygame.display.update()
