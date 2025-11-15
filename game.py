from sys import exit
import pygame.time, time

from variables import *
import function as func
import menu

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Rhythm Game')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)
combofont = pygame.font.Font('fonts/Platinum Sign Under.ttf', 40)
combofontup = pygame.font.Font('fonts/Platinum Sign Over.ttf', 40)

playlane_obj = pygame.Surface((400, HEIGHT), pygame.SRCALPHA, 32)
playlane_rect = playlane_obj.get_rect(center=(LANE[3][0],HEIGHT/2))
playlane_obj = playlane_obj.convert_alpha()
playlane_obj.fill((0,0,0,85))


songname_surf = combofont.render('MESMERIZER', False, 'Black')
songname_surf_up = combofontup.render('MESMERIZER', False, 'White')
songname_rect = songname_surf.get_rect(topleft=(20,20))

lane_sound = pygame.mixer.Sound('sfx/lanesound.wav')
lane_sound.set_volume(0.1)
# note_sound = pygame.mixer.Sound('sfx/notesound.wav')

class Conductor:
    def __init__(self, offset):
        self.offset = offset
        self.songpos = pygame.mixer.music.get_pos() - self.offset
        self.bpm = bpm
        self.beatDurationMs = round(60 / (bpm * 4) ,3) * 1000 # ms per 1 sixteenth note
        self.lastbeat = 0
        self.barnumber = 0
        self.nextbeatpos = self.beatDurationMs

    def main(self):
        self.update_music_pos()
        self.metronome()

    def metronome(self): # flash every quarter note
        if self.lastbeat < 4:
            pygame.draw.circle(screen,pygame.Color('White'),(800,500),20)
        elif self.lastbeat < 8:
            pygame.draw.circle(screen,pygame.Color('White'),(800,550),20)
        elif self.lastbeat < 12:
            pygame.draw.circle(screen,pygame.Color('White'),(800,600),20)
        else:
            pygame.draw.circle(screen,pygame.Color('White'),(800,650),20)

    def update_music_pos(self):
        self.songpos = pygame.mixer.music.get_pos() - self.offset
        if self.songpos >= self.nextbeatpos:
            self.lastbeat += 1
            self.nextbeatpos += self.beatDurationMs
        if self.lastbeat == 16:
            self.lastbeat = 0
            self.barnumber += 1

class Music:
    def __init__(self):
        self.duration = None
        pass

    def loadMusic(self,song):
        pygame.mixer.music.load(song)
        pygame.mixer_music.set_volume(0.1)
        self.duration = pygame.mixer.Sound(song).get_length()

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        global isPaused
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            isPaused = True
        else:
            pygame.mixer.music.unpause()
            isPaused = False

class PlayerInput:
    def __init__(self):
        pass
    def handle_event(self,event):
        global speed
        if event.type == pygame.MOUSEMOTION:
            global mx, my, swipe_cd
            mx, my = pygame.mouse.get_pos()
            movementx, movementy = pygame.mouse.get_rel()
            if movementx > 40 and swipe_cd == 0:
                for noteswipe in notes:
                    noteswipe.swipe('Right')
                swipe_cd = 5
            elif movementx < -40 and swipe_cd == 0:
                for noteswipe in notes:
                    noteswipe.swipe('Left')
                swipe_cd = 5
            # pygame.mouse.set_pos((WIDTH/2, HEIGHT/2))
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

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

        for key in pygame.key.get_pressed():
            if key == pygame.K_ESCAPE:
                menu.pause()

class Beatline:
    def __init__(self, y=JUDGE_LINE):
        self.bar = 0
        self.bpm = 185
        self.ms_per_beat = round(60 / (bpm*4), 3) * 1000
        self.pixel_per_beat = speed * self.ms_per_beat
        self.y = y
        self.lane_start = LANE[1][0]
        self.lane_end = LANE[5][0]
        self.visible_line = []
        self.lastline = 0

    def main(self):
        if Conductor.barnumber >= 0:
            self.draw()
            self.scroll()

    def scroll(self):
        self.y += speed

    def draw(self):
        bar = Conductor.barnumber/10000
        space = self.pixel_per_beat * speed
        for i in range(40):
            pygame.draw.line(screen, pygame.Color('Red'),
                (self.lane_start, self.y - self.pixel_per_beat*i),
                 (self.lane_end, self.y - self.pixel_per_beat*i), 7)

class Note:
    def __init__(self,lane,bar,beat,x,xx):
        self.lane = lane
        self.lanestart = LANE[lane][0]
        self.laneend = LANE[lane+1][0]
        self.pixel_per_beat = round(60 / (bpm * 4), 3) * 1000
        self.bar = bar
        self.beat = beat
        self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat/16)))
        self.initial_y = self.y
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.y > HEIGHT + speed * 10:
            self.kys()
            judges.append('MISS')

    def scroll(self):
        self.y += speed

    def draw(self):
        pygame.draw.line(screen,pygame.Color('Yellow'),(self.lanestart, self.y),
                         (self.laneend, self.y), 10)

    def hit(self):
        if not self.pressed:
            if self.judgement():
                self.pressed = True
                self.kys()
        return

    def judgement(self): #t = d/v
        bar, beat = Conductor.barnumber, Conductor.lastbeat
        hit_window = (bar + 1) * 16 + beat
        timing_window = (self.bar * 16) + self.beat
        timing_error = abs(hit_window - timing_window)
        if timing_error < 6:
            if timing_error == 0: judge = 'MARVELOUS'
            elif timing_error <= 1: judge = 'PERFECT'
            elif timing_error <= 2: judge = 'GREAT'
            elif timing_error <= 3: judge = 'GOOD'
            else: judge = 'MISS'
            judges.append(judge)
            return True
        return False

    def kys(self):
        notes.remove(self)

    def release(self):
        pass

    def swipe(self,direction):
        pass

class Hold:
    def __init__(self,lane,bar,beat,endbar,endbeat):
        self.lane = lane
        self.lanestart = LANE[lane][0]
        self.laneend = LANE[lane+1][0]
        self.pixel_per_beat = round(60 / (bpm * 4), 3) * 1000
        self.bar = bar
        self.beat = beat
        self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat/16)))
        self.initial_y = self.y
        self.endbar = endbar
        self.endbeat = endbeat
        self.end = JUDGE_LINE - (speed * self.pixel_per_beat * (self.endbar + (self.endbeat/16)))
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.end > HEIGHT + speed * 10:
            self.kys()
            judges.append('MISS')

    def scroll(self):
        self.y += speed
        self.end += speed

    def draw(self):
        if self.end > JUDGE_LINE:
            return
        if self.pressed:
            pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart + 50, JUDGE_LINE),
            (self.lanestart + 50, self.end), 80)
            pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart, self.end),
            (self.laneend, self.end), 20)
            return
        pygame.draw.line(screen,pygame.Color('Red'),(self.lanestart+50, self.y),
            (self.lanestart+50, self.end), 80)
        pygame.draw.line(screen,pygame.Color('Red'),(self.lanestart, self.y),
            (self.laneend, self.y), 20)
        pygame.draw.line(screen,pygame.Color('Red'),(self.lanestart, self.end),
            (self.laneend, self.end), 20)

    def hit(self):
        if not self.pressed:
            if self.judgement():
                self.pressed = True
        return

    def release(self):
        if self.pressed:
            if self.holdjudgement():
                self.kys()

    def judgement(self): #t = d/v
        bar, beat = Conductor.barnumber, Conductor.lastbeat
        hit_window = (bar + 1) * 16 + beat
        timing_window = (self.bar * 16) + self.beat
        timing_error = abs(hit_window - timing_window)
        if timing_error < 6:
            if timing_error == 0: judge = 'MARVELOUS'
            elif timing_error <= 1: judge = 'PERFECT'
            elif timing_error <= 2: judge = 'GREAT'
            elif timing_error <= 3: judge = 'GOOD'
            else: judge = 'MISS'
            judges.append(judge)
            return True
        return False

    def holdjudgement(self): #t = d/v
        bar, beat = Conductor.barnumber, Conductor.lastbeat
        hit_window = (bar + 1) * 16 + beat
        timing_window = (self.endbar * 16) + self.endbeat - 2
        timing_error = abs(hit_window - timing_window)
        if timing_error < 6:
            if timing_error == 0: judge = 'MARVELOUS'
            elif timing_error <= 1: judge = 'PERFECT'
            elif timing_error <= 2: judge = 'GREAT'
            elif timing_error <= 3: judge = 'GOOD'
            else: judge = 'MISS'
            judges.append(judge)
            return True
        return False

    def kys(self):
        notes.remove(self)

    def swipe(self,direction):
        pass

class Swipe:
    def __init__(self,lane,bar,beat,direction,xx):
        self.lane = lane
        self.lanestart = LANE[1][0]
        self.laneend = LANE[5][0]
        self.pixel_per_beat = round(60 / (bpm * 4), 3) * 1000
        self.bar = bar
        self.beat = beat
        if direction == -1:
            self.direction = 'Left'
        else:
            self.direction = 'Right'
        self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat/16)))
        self.initial_y = self.y
        self.pressed = False

    def main(self):
        self.scroll()
        self.draw()
        if self.y > HEIGHT + speed * 10:
            self.kys()
            judges.append('MISS')

    def scroll(self):
        self.y += speed

    def draw(self):
        if self.direction == 'Left':
            pygame.draw.line(screen,pygame.Color('Blue'),(self.lanestart, self.y),
                         (self.laneend, self.y), 10)
        else:
            pygame.draw.line(screen,pygame.Color('Pink'),(self.lanestart, self.y),
                         (self.laneend, self.y), 10)

    def hit(self):
        pass

    def swipe(self,direction):
        if not self.pressed:
            if self.judgement(direction):
                self.pressed = True
                self.kys()
        return

    def judgement(self,direction): #t = d/v
        bar, beat = Conductor.barnumber, Conductor.lastbeat
        hit_window = (bar + 1) * 16 + beat
        timing_window = (self.bar * 16) + self.beat
        timing_error = abs(hit_window - timing_window)
        if timing_error < 6:
            if self.direction == direction:
                if timing_error == 0: judge = 'MARVELOUS'
                elif timing_error <= 1: judge = 'Perfect'
                elif timing_error <= 2: judge = 'Great'
                judges.append(judge)
                return True
            if timing_error <= 3: judge = 'Good'
            else: judge = 'MISS'
            judges.append(judge)
            return True
        return False

    def kys(self):
        notes.remove(self)

    def release(self):
        pass

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
        lane_sound.play()
        lane_sound.fadeout(100)

    def key_up(self):
        self.keystate = False
        self.ispressed = False

    def key_check(self): #Sends signal when first time releasing
        if self.waspressed and self.keystate == False:
            # print(f'Lane {self.num} Up')
            self.waspressed = False
            for noteup in notes:
                if noteup.lane == self.num:
                    noteup.release()
                    return

        if self.keystate and self.ispressed == False: #Sends signal when first time pressing
            # print(f'Lane {self.num} Down')
            self.waspressed = True
            self.ispressed = True
            print(Conductor.barnumber, Conductor.lastbeat)
            for notedown in notes:
                if notedown.lane == self.num:
                    notedown.hit()
                    return

    def light_up(self):
        if self.waspressed:
            temp_rect = pygame.Rect(LANE[self.num][0], 100, 100, HEIGHT - (HEIGHT - JUDGE_LINE) - 100)
            func.gradientRect(screen, (200,200,200), (30, 30, 30, 0), temp_rect)

class Scoring:
    def __init__(self):
        self.score = 0
        self.combo = 1
        self.accuracy = 100.00

    def comboing(self,judge):
        if judge != 'MISS': self.combo += 1
        else: self.combo = 0

class Interface:
    def __init__(self):
        self.lane_mid = LANE[3][0]

    def display_UI(self):
        screen.blit(songname_surf, songname_rect)
        screen.blit(songname_surf_up, songname_rect)
        screen.blit(playlane_obj, playlane_rect)

        time_text = font.render(f'Time: {pygame.mixer.music.get_pos()/1000}', False, 'Gray')
        time_rect = time_text.get_rect(topleft=(20, 100))
        screen.blit(time_text, time_rect)

        conductor_text = font.render(f'Conductor: {Conductor.barnumber, Conductor.lastbeat}', False, 'White')
        conductor_rect = conductor_text.get_rect(topleft=(20, 150))
        screen.blit(conductor_text, conductor_rect)

        score_text = font.render(f'Score: {Score.score}', False, 'White')
        score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(score_text, score_rect)

    def display_info(self):
        maxsize, minsize =
        if Score.combo > 3:
            combo_img = combofont.render('COMBO', True, (24, 24, 24))
            combo_img_up = combofontup.render('COMBO', True, pygame.Color('White'))
            combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 53))
            screen.blit(combo_img, combo_rect)
            combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 49))
            screen.blit(combo_img_up, combo_rect)
            combo_img = combofont.render(f"{Score.combo}", True, (24,24,24))
            combo_img_up = combofontup.render(f"{Score.combo}", True, pygame.Color('White'))
            combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2))
            screen.blit(combo_img, combo_rect)
            combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 - 4))
            screen.blit(combo_img_up, combo_rect)

        if judges:
            judge_img = combofont.render(f"{judges[0]}", True, judgecolor[judges[0]])
            if judges[0] == 'MARVELOUS': outline = pygame.Color('Black')
            else: outline = pygame.Color('White')
            judge_img_up = combofontup.render(f"{judges[0]}", True, outline)
            judge_rect = judge_img.get_rect(center=(self.lane_mid, HEIGHT * 1 / 3))
            screen.blit(judge_img, judge_rect)
            judge_rect = judge_img.get_rect(center=(self.lane_mid, HEIGHT * 1 / 3 - 4))
            screen.blit(judge_img_up, judge_rect)
            if len(judges) > 1:
                judges.remove(judges[0])
                Score.comboing(judges[0])

    def display_lanes(self):
        pygame.draw.line(screen, pygame.Color('Green'), (LANE[1][0], JUDGE_LINE),
                         ((LANE[5][0]), JUDGE_LINE), 5)
        for i in range(0, 5):
            pygame.draw.line(screen, pygame.Color('White'), ((WIDTH / 3) + i * 100, 0),
                             ((WIDTH / 3) + i * 100, HEIGHT),5)

running = True
notes = []
judges = []

notes.clear()
judges.clear()

LANE1 = Lane(1,False,False,False)
LANE2 = Lane(2,False,False,False)
LANE3 = Lane(3,False,False,False)
LANE4 = Lane(4,False,False,False)
Music = Music()
Conductor = Conductor(1250)
beatline = Beatline()
Input = PlayerInput()
Interface = Interface()
Score = Scoring()

Music.loadMusic('Songs/Mesmerizer/Mesmerizer.mp3')
with open('Songs/Mesmerizer/Mesmerizer.txt', 'r') as f:
    for line in f:
        if not line.strip().startswith('#'):
            x = list(map(float,(line.strip().split(','))))
            if x[3] == -1 or x[3] == -2:
                notes.append(Swipe(*x))
            elif x[3] != 0:
                notes.append(Hold(*x))
            else:
                notes.append(Note(*x))

print('Start game')
pygame.key.set_repeat(0,0)
Music.play()
isPaused = False
start_time = time.time()
previous_time = time.time()
while running:
    clock.tick_busy_loop(fps)
    if swipe_cd > 0: swipe_cd -= 1
    screen.fill((30, 30, 30))
    for j in range(20):
        for i in range(-12, 12):
            surf = pygame.Surface((abs(20 - j), abs(20 - j))).convert_alpha()
            surf.fill(pygame.Color("white"))
            screen.blit(surf, (WIDTH/2 + i * 40, HEIGHT + 100 - j * 45))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        Input.handle_event(event)

    Interface.display_UI()

    if not isPaused:
        gameloop = [LANE1, LANE2, LANE3, LANE4,  Conductor, beatline]
        for main in gameloop:
            main.main()
        for note in notes:
            note.main()

    Interface.display_lanes()
    Interface.display_info()


    pygame.display.update()