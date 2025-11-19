from sys import exit
import pygame.time, time
from pygame import SCRAP_CLIPBOARD

from variables import *
import function as func
import dir
import json
import os
import menu

def run(current_song, difficulty):
    global Conductor, Music, PlayerInput, Beatline, Note, Hold, Swipe, Lane, Score, Interface

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Rhythm Game')
    clock = pygame.time.Clock()

    current_song = current_song
    current_diff = difficulty
    songsdic = dir.getsongdict()

    with open(songsdic[current_song]['settings'], 'r') as f:
        settings = json.load(f)

    bpm = settings['Bpm']
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    combofont = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), 40)
    combofontup = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), 40)
    playlane_obj = pygame.Surface((400, HEIGHT), pygame.SRCALPHA, 32)
    playlane_rect = playlane_obj.get_rect(center=(LANE[3][0], HEIGHT / 2))
    playlane_obj = playlane_obj.convert_alpha()
    playlane_obj.fill((0, 0, 0, 255))

    songname_surf = combofont.render(current_song.upper(), False, 'Black')
    songname_surf_up = combofontup.render(current_song.upper(), False, 'White')
    songname_surf = pygame.transform.rotate(songname_surf, 90)
    songname_surf_up = pygame.transform.rotate(songname_surf_up, 90)
    songname_rect = songname_surf.get_rect(bottomleft=(20, HEIGHT-20))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    lane_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sfx', 'lanesound.wav'))
    lane_sound.set_volume(0.1)

    text_anim = {
        'judge_scale': 1.0,  # current scale of judgment text
        'judge_timer': 0  # frames remaining for animation
    }

    class Conductor:
        def __init__(self, offset):
            self.offset = offset
            self.songpos = pygame.mixer.music.get_pos() - self.offset
            self.bpm = bpm
            self.beatDurationMs = round(60 / (bpm * 4), 3) * 1000  # ms per 1 sixteenth note
            self.lastbeat = 0
            self.barnumber = 0
            self.nextbeatpos = self.beatDurationMs

        def main(self):
            self.update_music_pos()
            self.metronome()

        def metronome(self):  # flash every quarter note
            if self.lastbeat < 4:
                pygame.draw.circle(screen, pygame.Color('White'), (800, 500), 20)
            elif self.lastbeat < 8:
                pygame.draw.circle(screen, pygame.Color('White'), (800, 550), 20)
            elif self.lastbeat < 12:
                pygame.draw.circle(screen, pygame.Color('White'), (800, 600), 20)
            else:
                pygame.draw.circle(screen, pygame.Color('White'), (800, 650), 20)

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
            self.song = songsdic[current_song]['Music']
            pass

        def loadMusic(self, song):
            pygame.mixer.music.load(self.song)
            pygame.mixer_music.set_volume(0.1)
            self.duration = pygame.mixer.Sound(self.song).get_length()

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

        def handle_event(self, event):
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print(pygame.mixer.music.get_pos())
                    Music.pause()

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                global HEIGHT, WIDTH, LANE
                WIDTH, HEIGHT = screen.get_size()
                LANE = {
                    1: ((WIDTH / 3), 0),
                    2: ((WIDTH / 3) + 100, 0),
                    3: ((WIDTH / 3) + 200, 0),
                    4: ((WIDTH / 3) + 300, 0),
                    5: ((WIDTH / 3) + 400, 0)
                }

    class Beatline:
        def __init__(self, y=JUDGE_LINE):
            self.bar = 0
            self.ms_per_beat = round(60 / (bpm * 4), 3) * 1000
            self.pixel_per_beat = speed * self.ms_per_beat
            self.y = y
            self.y_first = y
            self.lane_start = LANE[1][0]
            self.lane_end = LANE[5][0]

        def main(self):
            if Conductor.barnumber >= 0:
                self.draw()
                self.scroll()

        def scroll(self):
            self.y += speed

        def draw(self):
            bar = Conductor.barnumber / 10000
            space = self.pixel_per_beat * speed
            for i in range(40):
                y_pos = self.y - self.pixel_per_beat * i
                if 0 < y_pos < HEIGHT:
                    pygame.draw.line(screen, pygame.Color('Red'),
                                     (self.lane_start, y_pos),
                                     (self.lane_end, y_pos), 7)

    class Note:
        def __init__(self, lane, bar, beat, x, xx):
            self.lane = lane
            self.lanestart = LANE[lane][0]
            self.laneend = LANE[lane + 1][0]
            self.pixel_per_beat = round(60 / (bpm * 4), 3) * 1000
            self.bar = bar
            self.beat = beat
            self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat / 16)))
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
            if HEIGHT > self.y > 0:
                pygame.draw.line(screen, pygame.Color('Yellow'), (self.lanestart, self.y),
                                 (self.laneend, self.y), 30)

        def hit(self):
            if not self.pressed:
                if self.judgement():
                    self.pressed = True
                    self.kys()
            return

        def judgement(self):  # t = d/v
            bar, beat = Conductor.barnumber, Conductor.lastbeat
            hit_window = (bar + 1) * 16 + beat
            timing_window = (self.bar * 16) + self.beat
            timing_error = abs(hit_window - timing_window)
            if timing_error < 4:
                if timing_error == 0:
                    judge = 'MARVELOUS';
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT';
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT';
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD';
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS';
                    Score.acc['MISS'] += 1
                judges.append(judge)
                return True
            return False

        def kys(self):
            notes.remove(self)

        def release(self):
            pass

        def swipe(self, direction):
            pass

    class Hold:
        def __init__(self, lane, bar, beat, endbar, endbeat):
            self.lane = lane
            self.lanestart = LANE[lane][0]
            self.laneend = LANE[lane + 1][0]
            self.pixel_per_beat = round(60 / (bpm * 4), 3) * 1000
            self.bar = bar
            self.beat = beat
            self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat / 16)))
            self.initial_y = self.y
            self.endbar = endbar
            self.endbeat = endbeat
            self.end = JUDGE_LINE - (speed * self.pixel_per_beat * (self.endbar + (self.endbeat / 16)))
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
            if self.y > 0:
                if self.end > JUDGE_LINE:
                    return
                if self.pressed and self.y > JUDGE_LINE:
                    pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart + 50, JUDGE_LINE),
                                     (self.lanestart + 50, self.end), 80)
                    pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart, self.end),
                                     (self.laneend, self.end), 20)
                    return
                pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart + 50, self.y),
                                 (self.lanestart + 50, self.end), 80)
                pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart, self.y),
                                 (self.laneend, self.y), 20)
                pygame.draw.line(screen, pygame.Color('Red'), (self.lanestart, self.end),
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

        def judgement(self):  # t = d/v
            bar, beat = Conductor.barnumber, Conductor.lastbeat
            hit_window = (bar + 1) * 16 + beat
            timing_window = (self.bar * 16) + self.beat
            timing_error = abs(hit_window - timing_window)
            if timing_error < 6:
                if timing_error == 0:
                    judge = 'MARVELOUS';
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT';
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT';
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD';
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS';
                    Score.acc['MISS'] += 1
                judges.append(judge)
                return True
            return False

        def holdjudgement(self):  # t = d/v
            bar, beat = Conductor.barnumber, Conductor.lastbeat
            hit_window = (bar + 1) * 16 + beat
            timing_window = (self.endbar * 16) + self.endbeat
            timing_error = abs(hit_window - timing_window)
            if timing_error < 6:
                if timing_error == 0:
                    judge = 'MARVELOUS';
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT';
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT';
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD';
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS';
                    Score.acc['MISS'] += 1
                judges.append(judge)
                return True
            return False

        def kys(self):
            notes.remove(self)

        def swipe(self, direction):
            pass

    class Swipe:
        def __init__(self, lane, bar, beat, direction, xx):
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
            self.y = JUDGE_LINE - (speed * self.pixel_per_beat * (self.bar + (self.beat / 16)))
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
                pygame.draw.line(screen, pygame.Color('Blue'), (self.lanestart, self.y),
                                 (self.laneend, self.y), 10)
            else:
                pygame.draw.line(screen, pygame.Color('Pink'), (self.lanestart, self.y),
                                 (self.laneend, self.y), 10)

        def hit(self):
            pass

        def swipe(self, direction):
            if not self.pressed:
                if self.judgement(direction):
                    self.pressed = True
                    self.kys()
            return

        def judgement(self, direction):  # t = d/v
            bar, beat = Conductor.barnumber, Conductor.lastbeat
            hit_window = (bar + 1) * 16 + beat
            timing_window = (self.bar * 16) + self.beat
            timing_error = abs(hit_window - timing_window)
            if timing_error < 6:
                if self.direction == direction:
                    judge = 'MARVELOUS';
                    if timing_error == 0:
                        judge = 'MARVELOUS';
                        Score.acc['MARVELOUS'] += 1
                    elif timing_error <= 1:
                        judge = 'Perfect';
                        Score.acc['PERFECT'] += 1
                    elif timing_error <= 2:
                        judge = 'Great';
                        Score.acc['GREAT'] += 1
                    judges.append(judge)
                    return True
                if timing_error <= 3:
                    judge = 'Good'
                else:
                    judge = 'MISS'
                judges.append(judge)
                return True
            return False

        def kys(self):
            notes.remove(self)

        def release(self):
            pass

    class Lane:
        def __init__(self, num, keystate, ispressed, waspressed):
            self.num = num
            self.keystate = keystate
            self.ispressed = ispressed
            self.waspressed = waspressed
            self.fadealpha = 0

        def main(self):  # Continuous function
            self.key_check()
            self.light_up()
            if self.waspressed: self.fadealpha = 200
            if self.fadealpha > 0: self.fadealpha -= 25

        def key_down(self):
            self.keystate = True
            print(Conductor.barnumber, Conductor.lastbeat)
            lane_sound.play()
            lane_sound.fadeout(100)

        def key_up(self):
            self.keystate = False
            self.ispressed = False

        def key_check(self):  # Sends signal when first time releasing
            if self.waspressed and self.keystate == False:
                # print(f'Lane {self.num} Up')
                self.waspressed = False
                for noteup in notes:
                    if noteup.lane == self.num:
                        noteup.release()
                        return

            if self.keystate and self.ispressed == False:  # Sends signal when first time pressing
                # print(f'Lane {self.num} Down')
                self.waspressed = True
                self.ispressed = True
                for notedown in notes:
                    if notedown.lane == self.num:
                        notedown.hit()
                        return

        def light_up(self):
            if self.fadealpha > 0:
                temp_rect = pygame.Rect(LANE[self.num][0], 100, 100, HEIGHT - (HEIGHT - JUDGE_LINE) - 100)
                light = self.fadealpha
                func.gradientRect(screen, (light, light, light), (0, 0, 0, 0), temp_rect)

    class Scoring:
        def __init__(self):
            self.difficulty = difficulty
            self.score = 0
            self.notecount = 0
            self.combo = 1
            self.maxcombo = 0
            self.accuracy = 100.00
            self.acc = {'MARVELOUS': 0, 'PERFECT': 0, 'GREAT': 0, 'GOOD': 0, 'MISS': 0}

        def main(self):
            self.score = self.acc['MARVELOUS'] * 310 + self.acc['PERFECT'] * 300 + self.acc['GREAT'] * 200 + self.acc['GOOD'] * 50

        def comboing(self, judge):
            if judge != 'MISS':
                self.combo += 1
                Interface.score_timer = 10
            else:
                if self.combo > self.maxcombo:
                    self.maxcombo = self.combo
                self.combo = 0
                Interface.score_timer = 10

        def calculateacc(self):
            self.accuracy = (self.score / (self.notecount * 310)) * 100

    class Interface:
        def __init__(self):
            self.lane_mid = LANE[3][0]
            self.score_scale = 1
            self.score_timer = 0
            self.lastscore = 0

            self.judge_text = ""
            self.judge_color = pygame.Color('White')
            self.judge_outline = pygame.Color('Black')
            self.judge_scale = 1.0
            self.judge_target_scale = 1.0
            self.judge_timer = 0
            self.judge_debounce = 2

        def display_UI(self):
            screen.blit(songname_surf, songname_rect)
            screen.blit(songname_surf_up, songname_rect)
            screen.blit(playlane_obj, playlane_rect)

            score_text = combofont.render(str(Score.score), False, 'Black')
            score_text = pygame.transform.scale(score_text, (int(score_text.get_width() * self.score_scale),
                                                             int(score_text.get_height() * self.score_scale)))
            score_text_up = combofontup.render(str(Score.score), False, 'White')
            score_text_up = pygame.transform.scale(score_text_up, (int(score_text_up.get_width() * self.score_scale),
                                                                   int(score_text_up.get_height() * self.score_scale)))
            score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
            screen.blit(score_text, score_rect)
            screen.blit(score_text_up, score_rect)

        def trigger_judge_animation(self, text, color):
            if self.judge_debounce > 0:
                return  # ignore new hit until debounce finishes

            self.judge_text = text
            self.judge_color = color
            self.judge_outline = pygame.Color('Black') if text == 'MARVELOUS' else pygame.Color('White')
            self.judge_scale = 0.8
            self.judge_target_scale = 1
            self.judge_timer = 15
            self.judge_debounce = 10

        def display_info(self):
            if Score.combo > 3:
                combo_img = combofont.render('COMBO', True, (24, 24, 24))
                combo_img_up = combofontup.render('COMBO', True, pygame.Color('White'))
                combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 53))
                screen.blit(combo_img, combo_rect)
                combo_rect = combo_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 49))
                screen.blit(combo_img_up, combo_rect)
                combo_num_img = combofont.render(f"{Score.combo}", True, (24, 24, 24))
                combo_num_img_up = combofontup.render(f"{Score.combo}", True, pygame.Color('White'))
                combo_rect = combo_num_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2))
                screen.blit(combo_num_img, combo_rect)
                combo_rect = combo_num_img.get_rect(center=(self.lane_mid, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 - 4))
                screen.blit(combo_num_img_up, combo_rect)

            if self.judge_text:
                judge_img = combofont.render(self.judge_text, True, self.judge_color)
                judge_img_up = combofontup.render(self.judge_text, True, self.judge_outline)
                judge_img = pygame.transform.scale(judge_img, (
                    int(judge_img.get_width() * self.judge_scale),
                    int(judge_img.get_height() * self.judge_scale)
                ))
                judge_img_up = pygame.transform.scale(judge_img_up, (
                    int(judge_img_up.get_width() * self.judge_scale),
                    int(judge_img_up.get_height() * self.judge_scale)
                ))
                judge_rect = judge_img.get_rect(center=(self.lane_mid, HEIGHT * 1 / 3))
                screen.blit(judge_img, judge_rect)
                screen.blit(judge_img_up, judge_rect)

            if judges:
                text = judges.pop(0)
                color = judgecolor[text]
                Interface.trigger_judge_animation(text, color)
                Score.comboing(text)

            if self.judge_text:
                judge_img = combofont.render(self.judge_text, True, self.judge_color)
                judge_img_up = combofontup.render(self.judge_text, True, self.judge_outline)
                judge_img = pygame.transform.scale(judge_img, (int(judge_img.get_width() * self.judge_scale),
                                                               int(judge_img.get_height() * self.judge_scale)))
                judge_img_up = pygame.transform.scale(judge_img_up, (int(judge_img_up.get_width() * self.judge_scale),
                                                                     int(judge_img_up.get_height() * self.judge_scale)))
                judge_rect = judge_img.get_rect(center=(self.lane_mid, HEIGHT * 1 / 3))
                screen.blit(judge_img, judge_rect)
                screen.blit(judge_img_up, judge_rect)

        def display_lanes(self):
            pygame.draw.line(screen, pygame.Color('Green'), (LANE[1][0], JUDGE_LINE),
                             ((LANE[5][0]), JUDGE_LINE), 5)
            for i in range(0, 5):
                pygame.draw.line(screen, pygame.Color('White'), ((WIDTH / 3) + i * 100, 0),
                                 ((WIDTH / 3) + i * 100, HEIGHT), 5)

        def update_score_animation(self):
            if self.score_timer > 0:
                if self.lastscore != Score.score:
                    self.score_scale = 1.2
                self.score_timer -= 1
                self.lastscore = Score.score

            else:
                self.score_scale = max(1, self.score_scale - 0.05)

            if self.judge_timer > 0:
                self.judge_scale += (self.judge_target_scale - self.judge_scale) * 0.2
                self.judge_timer -= 1
            else:
                self.judge_target_scale = 1.0
                self.judge_scale += (self.judge_target_scale - self.judge_scale) * 0.1

            if self.judge_debounce > 0:
                self.judge_debounce -= 1

    running = True
    notes = []
    judges = []

    notes.clear()
    judges.clear()
    swipe_cd = 0

    LANE1 = Lane(1, False, False, False)
    LANE2 = Lane(2, False, False, False)
    LANE3 = Lane(3, False, False, False)
    LANE4 = Lane(4, False, False, False)
    Music = Music()
    Conductor = Conductor(settings['offset'])
    beatline = Beatline()
    Input = PlayerInput()
    Interface = Interface()
    Score = Scoring()

    Music.loadMusic(songsdic[current_song]['Music'])
    with open(songsdic[current_song][current_diff], 'r') as f:
        for line in f:
            if not line.strip().startswith('#'):
                x = list(map(float, (line.strip().split(','))))
                if x[3] == -1 or x[3] == -2:
                    notes.append(Swipe(*x))
                    Score.notecount += 1
                elif x[3] != 0:
                    notes.append(Hold(*x))
                    Score.notecount += 2
                else:
                    notes.append(Note(*x))
                    Score.notecount += 1

    print('Start game')
    pygame.key.set_repeat(0, 0)
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
                screen.blit(surf, (WIDTH / 2 + i * 40, HEIGHT + 100 - j * 45))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            Input.handle_event(event)

        Interface.display_UI()

        if not isPaused:
            gameloop = [LANE1, LANE2, LANE3, LANE4, Conductor, beatline, Score]
            for main in gameloop:
                main.main()
            for note in notes:
                note.main()

        Interface.update_score_animation()

        Interface.display_lanes()
        Interface.display_info()

        if isPaused:
            blurred = func.blur_surface(screen.copy(), passes=3, scale_factor=0.25)
            screen.blit(blurred, (0, 0))

        if pygame.mixer.music.get_pos() == -1:
            Score.calculateacc()
            result(current_song)

        pygame.display.update()

def result(song):
    global Conductor, Music, PlayerInput, Beatline, Note, Hold, Swipe, Lane, Score, Interface
    pygame.init()

    BASE_WIDTH, BASE_HEIGHT = 1920, 1080

    # new one change here naja
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    scale_x = WIDTH / BASE_WIDTH
    scale_y = HEIGHT / BASE_HEIGHT
    scale = min(scale_x, scale_y)
    songsdict = dir.getsongdict()

    # Colors
    PURPLE = (102, 51, 153)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Fonts(Change later)
    title_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(100 * scale))
    score_font = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(55 * scale))
    stat_font = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(30 * scale))
    grade_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(400 * scale))
    grade_font_under = pygame.font.Font(os.path.join("fonts", "Platinum_under.ttf"), int(400 * scale))

    # Background = using songname.png
    bg_image_path = songsdict[song]['Bg']
    bg_image = pygame.image.load(bg_image_path).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    bg_opacity = 20
    overlay_opacity = 100

    difficulty = Score.difficulty
    song_name = songsdict[song]['name'].upper()
    accuracy = Score.accuracy
    grade = "A"
    score = Score.score
    max_combo = Score.maxcombo
    marvelous = Score.acc['MARVELOUS']
    perfect = Score.acc['PERFECT']
    great = Score.acc['GREAT']
    good = Score.acc['GOOD']
    miss = Score.acc['MISS']

    # Rectangle
    def draw_rounded_rect(surface, color, rect, radius):
        pygame.draw.rect(surface, color, rect, border_radius=int(radius * scale))

    # Trapezoid
    def draw_right_trapezoid(surface, color, x, y, w, h, slant):
        p1 = (x, y)
        p2 = (x + w, y)
        p3 = (x + w - slant, y + h)
        p4 = (x, y + h)
        pygame.draw.polygon(surface, color, [p1, p2, p3, p4])

    # adjusting number
    panel_width = int(700 * scale)
    panel_height = int(400 * scale)
    panel_x = int(100 * scale)
    panel_y = int(300 * scale)

    trapezoid_width = int(600 * scale)
    trapezoid_height = int(120 * scale)
    trapezoid_slant = int(-100 * scale)
    trapezoid_x = int(100 * scale)
    trapezoid_y = int(150 * scale)

    stats_top_margin = int(120 * scale)
    stats_spacing = int(60 * scale)

    score_offset_x = int(-305 * scale)
    score_offset_y = int(0 * scale)

    song_name_x = int(panel_x + 850 * scale)
    song_name_y = int(panel_y - 168 * scale)

    accuracy_x = int(panel_x + 45 * scale)
    accuracy_y = int(panel_y + 500 * scale)

    grade_x = int(panel_x + 950 * scale)
    grade_y = int(panel_y - 50 * scale)

    button_width = int(200 * scale)
    button_height = int(80 * scale)
    button_spacing = int(30 * scale)

    button_continue_x = int(WIDTH - button_width - 50 * scale)
    button_continue_y = int(HEIGHT - button_height - 50 * scale)

    button_retry_x = int(WIDTH - button_width - 280 * scale)
    button_retry_y = int(HEIGHT - button_height - 50 * scale)

    difficulty_box = int(20 * scale)
    difficulty_x = int(panel_x + 15 * scale)
    difficulty_y = int(panel_y + panel_height - 45 * scale)

    diff_hori_freaking_margin = int(20 * scale)
    diff_vert_padding = int(8 * scale)

    #####################################################
    continue_rect = pygame.Rect(button_continue_x, button_continue_y, button_width, button_height)
    retry_rect = pygame.Rect(button_retry_x, button_retry_y, button_width, button_height)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if continue_rect.collidepoint(mouse_pos):
                    menu.song_selection_screen()
                    print("Go back to song selection yessir")
                elif retry_rect.collidepoint(mouse_pos):
                    run(songsdict[song]['name'],diff)
                    print("you sucked so u retry it or you just want better score")

        bg_surface = bg_image.copy()
        bg_surface.set_alpha(bg_opacity)
        screen.blit(bg_surface, (0, 0))

        # difficulty
        difficulty_render = stat_font.render(difficulty, True, WHITE)
        difficulty_text_rect = difficulty_render.get_rect()
        diff_rect_width = panel_width - (diff_hori_freaking_margin * 2)
        diff_rect_height = difficulty_text_rect.height + diff_vert_padding * 2
        diff_x = panel_x + diff_hori_freaking_margin
        diff_y = panel_y + panel_height - diff_rect_height - diff_vert_padding

        difficulty_rect_approx = pygame.Rect(diff_x, diff_y, diff_rect_width, diff_rect_height)

        # bhind overlay
        overlay_surface = pygame.Surface((WIDTH, HEIGHT))
        overlay_surface.set_alpha(overlay_opacity)
        overlay_surface.fill(BLACK)
        screen.blit(overlay_surface, (0, 0))

        draw_rounded_rect(screen, WHITE, pygame.Rect(panel_x, panel_y, panel_width, panel_height), 30)
        draw_right_trapezoid(screen, WHITE, trapezoid_x, trapezoid_y, trapezoid_width, trapezoid_height,
                             trapezoid_slant)
        draw_rounded_rect(screen, diffcolor[Score.difficulty], difficulty_rect_approx, 15)  # color change here

        text_blit_x = difficulty_rect_approx.x + diff_hori_freaking_margin  # difficulty one
        text_blit_y = difficulty_rect_approx.y + diff_vert_padding

        score_text = score_font.render(f"Score: {score}", True,
                                       BLACK)  # ts pmo it hella hard :pray: pls no more trapezoid
        text_rect = score_text.get_rect(midleft=(
            trapezoid_x + trapezoid_width / 2 - trapezoid_slant / 2 + score_offset_x,
            trapezoid_y + trapezoid_height / 2 + score_offset_y
        ))
        screen.blit(score_text, text_rect)

        stats = [("Marvelous", marvelous), ("Perfect", perfect), ("Great", great), ("Good", good), ("Miss", miss)]
        label_x = panel_x + int(42 * scale)
        value_x = panel_x + int(275 * scale)
        for i, (label, value) in enumerate(stats):
            y = panel_y - int(65 * scale) + stats_top_margin + i * stats_spacing
            screen.blit(stat_font.render(f"{label}", True, BLACK), (label_x, y))  # stat(changing perfect, great, miss)
            screen.blit(stat_font.render(str(value), True, BLACK), (value_x, y))  # stat(changing number)

        # max combo
        max_label_text = stat_font.render("Max Combo", True, BLACK)
        label_rect = max_label_text.get_rect(
            topright=(panel_x + panel_width - int(50 * scale), panel_y + int(57 * scale)))
        screen.blit(max_label_text, label_rect)

        max_value_text = stat_font.render(str(max_combo), True, BLACK)
        value_rect = max_value_text.get_rect(
            topright=(panel_x + panel_width - int(50 * scale), label_rect.bottom + int(10 * scale)))
        screen.blit(max_value_text, value_rect)

        # song + difficulty + acc
        screen.blit(title_font.render(song_name, True, BLACK), (song_name_x, song_name_y))
        screen.blit(title_font.render(song_name, True, WHITE), (song_name_x, song_name_y))
        screen.blit(stat_font.render(f"Accuracy: {accuracy}%", True, WHITE), (accuracy_x, accuracy_y))
        screen.blit(difficulty_render, (text_blit_x, text_blit_y))

        grade_text_under = grade_font.render(grade, True, BLACK)
        grade_text_over = grade_font.render(grade, True, WHITE)
        screen.blit(grade_text_under, (grade_x + int(20 * scale), grade_y))
        screen.blit(grade_text_over, (grade_x, grade_y))

        pygame.draw.rect(screen, WHITE, continue_rect, border_radius=int(20 * scale))
        pygame.draw.rect(screen, WHITE, retry_rect, border_radius=int(20 * scale))
        continue_text_surf = stat_font.render("Continue", True, BLACK)
        retry_text_surf = stat_font.render("Retry", True, BLACK)
        screen.blit(continue_text_surf, continue_text_surf.get_rect(center=continue_rect.center))
        screen.blit(retry_text_surf, retry_text_surf.get_rect(center=retry_rect.center))

        pygame.display.update()
        clock.tick(60)

run('Mesmerizer','Exp')