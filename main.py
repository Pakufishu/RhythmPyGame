import json
import math
import os
import random
import sys
from sys import exit

import numpy as np
import pygame.time
import time
from scipy.io import wavfile

import dir
import function as func
from variables import *

pygame.init()

# --- Screen settings ---
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rhythm Game Menu")
clock = pygame.time.Clock()

# --- Base resolution ---
BASE_WIDTH = 1080
BASE_HEIGHT = 720

# --- Colors ---
TEXT_COLOR = (220, 240, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HOVER_COLOR = (255, 255, 0)
BG_COLOR = (10, 10, 20)
BG_COLOR2 = (20, 22, 28)
ARROW_COLOR = (255, 255, 255)

# --- Asset folders dict ---
songsdict = dir.getsongdict()

# --- Globals ---
background_img = None
audio_data = None
sample_rate = None
last_song = None
song_volume = 0.2
sfx_volume = 0.1

# --- Load backgrounds and music ---
class SongPlayer:
    def __init__(self):
        self.song = 'Mesmerizer'
        self.prevsong = self.song
        self.songdic = songsdict[self.song]
        self.music = songsdict[self.song]['Music']
        self.cover = songsdict[self.song]['Art']

    def play(self, chosen_song):
        self.song = songsdict[chosen_song]['name']
        if self.song != self.prevsong:
            pygame.mixer.music.stop()
            self.songdic = songsdict[self.song]
            self.music = songsdict[self.song]['Music']
            self.cover = songsdict[self.song]['Art']
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.set_volume(song_volume)
            pygame.mixer.music.play(-1)
            self.prevsong = self.song

    def randomSong(self):
        self.song = random.choice(list(songsdict.keys()))
        self.songdic = songsdict[self.song]
        self.music = songsdict[self.song]['Music']
        self.cover = songsdict[self.song]['Art']
        return self.song

class BackgroundManager:
    def __init__(self):
        self.songbgfolder = songsdict[song_player.song]['Bg']
        self.background_img = ''

    def loadBackground(self):
        self.songbgfolder = songsdict[song_player.song]['Bg']
        img = pygame.image.load(background.songbgfolder).convert()
        self.background_img = pygame.transform.scale(img, (WIDTH + 100, HEIGHT + 100))

song_player = SongPlayer()
background = BackgroundManager()

# --- Black overlay ---
black_overlay = pygame.Surface((WIDTH, HEIGHT))
black_overlay.fill(BLACK)
black_opacity = 100
black_overlay.set_alpha(black_opacity)

# --- Hover & other SFX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
hover_sound_path = os.path.join(BASE_DIR, "sfx", "hover.wav")
hover_sound = pygame.mixer.Sound(hover_sound_path)
hover_sound.set_volume(sfx_volume)

# --- Load a random main-menu song and matching background (if any) ---
def load_song_and_background():
    global audio_data, sample_rate, background_img, last_song
    new_song = song_player.randomSong()
    last_song = new_song
    music_path = song_player.music
    background.loadBackground()
    background_img = background.background_img
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(song_volume)
        pygame.mixer.music.play(-1)
        sample_rate, audio_data = wavfile.read(music_path)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
    except Exception:
        audio_data = None
        sample_rate = None

# initial main-menu music/background load
load_song_and_background()

# --- Font setup ---
def get_scale():
    return min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def update_fonts():
    global font_title, font_menu, font_under_title, font_under_menu, font_text, font_text_small, font_text_big
    scale = get_scale()
    font_title = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(70 * scale))
    font_under_title = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), int(70 * scale))
    font_menu = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(50 * scale))
    font_under_menu = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), int(50 * scale))
    font_text = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Designer.otf"), int(30 * scale))
    font_text_small = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Designer.otf"), int(20 * scale))
    font_text_big = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Designer.otf"), int(50 * scale))

update_fonts()

# --- Title ---
def draw_title():
    func.draw_double_text(screen, "PYTRHYTHM", font_title, font_under_title, TEXT_COLOR, BLACK,
                          (WIDTH / 2, HEIGHT * 0.18))

# --- Menu button ---
def draw_menu_button(text, y, hover=False):
    color_top = HOVER_COLOR if hover else TEXT_COLOR
    color_bottom = BLACK
    return func.draw_double_text(screen, text, font_menu, font_under_menu, color_top, color_bottom, (WIDTH / 2, y),
                                 center=True)
# --- Visualizer ---
bar_values = np.zeros(70)

def draw_visualizer(audio_data, sample_rate):
    global bar_values
    if audio_data is None or sample_rate is None: return
    pos_ms = pygame.mixer.music.get_pos()
    if pos_ms < 0: return
    idx = int((pos_ms / 1000.0) * sample_rate)
    window = 4096
    if idx + window > len(audio_data): return
    segment = audio_data[idx:idx + window]
    fft_data = np.abs(np.fft.rfft(segment))
    fft_data = fft_data[:len(fft_data) // 2]
    num_bars = len(bar_values)
    bar_width = WIDTH / num_bars
    fft_bins = np.linspace(0, len(fft_data), num_bars, endpoint=False, dtype=int)
    max_height = HEIGHT * 0.4
    smooth = 0.2
    if np.max(fft_data + 1e-6) == 0: return
    for i in range(num_bars):
        val = fft_data[fft_bins[i]] / np.max(fft_data + 1e-6)
        target = val * max_height
        bar_values[i] = bar_values[i] * (1 - smooth) + target * smooth
        x = i * bar_width
        pygame.draw.rect(screen, (255, 255, 255), (x, 0, bar_width - 2, bar_values[i]))
        pygame.draw.rect(screen, (255, 255, 255), (x, HEIGHT - bar_values[i], bar_width - 2, bar_values[i]))

bar_values_songselect = [0] * 70  # number of bars

def draw_songselect_visualizer(audio_data, sample_rate):
    global bar_values_songselect
    if audio_data is None or sample_rate is None:
        return

    pos_ms = pygame.mixer.music.get_pos()
    if pos_ms < 0:
        return

    idx = int((pos_ms / 1000.0) * sample_rate)
    window = 4096
    if idx + window > len(audio_data):
        return

    segment = audio_data[idx:idx + window]
    fft_data = np.abs(np.fft.rfft(segment))
    fft_data = fft_data[:len(fft_data) // 2]

    num_bars = len(bar_values_songselect)
    fft_bins = np.linspace(0, len(fft_data), num_bars, endpoint=False, dtype=int)
    max_height = HEIGHT * 1
    max_width = WIDTH
    smooth = 0.2

    if np.max(fft_data + 1e-6) == 0:
        return

    start_x = -50
    start_y = HEIGHT - 20

    for i in range(num_bars):
        val = fft_data[fft_bins[i]] / np.max(fft_data + 1e-6)
        target = val * max_height
        bar_values_songselect[i] = bar_values_songselect[i] * (1 - smooth) + target * smooth

        bar_height = bar_values_songselect[i]
        x0 = start_x + i * (max_width / num_bars)
        y0 = start_y
        x1 = x0 + bar_height * 0.5
        y1 = y0 - bar_height

        pygame.draw.line(screen, (255, 255, 255), (x0, y0), (x1, y1), 3)

# --- Cinematic bars ---
def draw_cinematic_bars():
    h = int(HEIGHT * 0.05)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, h))
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - h, WIDTH, h))

# --- Slider class (changed) ---
class Slider:
    def __init__(self, x, y, width, value=0.5):
        self.x = x
        self.y = y
        self.width = width
        self.value = value
        self.height = 20
        self.dragging = False

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        pygame.draw.rect(surface, (100, 100, 100), (self.x + ox, self.y + oy, self.width, self.height), border_radius=8)
        knob_x = int(self.x + ox + self.value * self.width)
        knob_y = self.y + oy + self.height // 2
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, knob_y), self.height // 2)

    def handle_event(self, event, offset=(0, 0)):
        ox, oy = offset
        mx, my = pygame.mouse.get_pos()
        mx -= ox
        my -= oy

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.value = max(0, min(1, (mx - self.x) / self.width))

class TextInputBox:
    def __init__(self, x, y, w, h, text='', font=None, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.font = font or pygame.font.Font(None, 32)
        self.active = False

        # Typing effect
        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_blink_speed = 30

        # <-- Add optional offset parameter -->

    def handle_event(self, event, offset=(0, 0)):
        ox, oy = offset
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            x -= ox
            y -= oy
            self.active = self.rect.collidepoint((x, y))
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                self.active = False
            else:
                if event.unicode.isdigit() or event.unicode == '.':
                    # append one character at a time
                    self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 50, 50), self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color, self.rect, 2)

        # Render text
        txt_surface = self.font.render(self.text, True, self.color)
        surface.blit(txt_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - txt_surface.get_height()) // 2))

        # Update cursor blink
        if self.active:
            self.cursor_counter += 1
            if self.cursor_counter >= self.cursor_blink_speed:
                self.cursor_counter = 0
                self.cursor_visible = not self.cursor_visible

            if self.cursor_visible:
                cursor_x = self.rect.x + 5 + txt_surface.get_width() + 2
                cursor_y = self.rect.y + 5
                cursor_h = self.rect.height - 10
                pygame.draw.rect(surface, self.color, (cursor_x, cursor_y, 3, cursor_h))

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where menu.py is

# Setting
def settings_scene():
    import variables
    global WIDTH, HEIGHT, screen, hover_sound, running, song_volume, sfx_volume

    snapshot = screen.copy()
    blurred = func.blur_surface(snapshot, passes=3, scale_factor=0.25)

    panel_w = int(WIDTH * 0.5)
    panel_h = int(HEIGHT * 0.68)
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_scale = panel_w / BASE_WIDTH

    # Fonts
    title_font = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(72 * panel_scale))
    label_font = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(40 * panel_scale))
    input_font = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(40 * panel_scale))

    # Slider positions relative to panel
    label_x = 90
    slider_x = 170
    slider_width = panel_w - slider_x - 50

    music_slider = Slider(slider_x, 128, slider_width,
                          pygame.mixer.music.get_volume() if pygame.mixer.music.get_busy() else 0.1)
    sfx_slider = Slider(slider_x, 228, slider_width, hover_sound.get_volume() if hover_sound else 0.5)
    speed_input = TextInputBox(slider_x, 300, slider_width, 40, text=str(variables.speed), font=input_font)

    back_rect = pygame.Rect(panel_w // 2 - 100, panel_h - 90, 200, 56)

    while running:
        dt = clock.tick(60)
        screen.blit(blurred, (0, 0))

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 160))
        screen.blit(overlay, (0, 0))

        # Draw panel gradient
        panel.fill((0, 0, 0, 0))
        for i in range(panel_h):
            t = i / panel_h
            r = int(20 + 30 * t)
            g = int(20 + 30 * t)
            b = int(30 + 20 * t)
            panel.fill((r, g, b, 220), rect=pygame.Rect(0, i, panel_w, 1))
        pygame.draw.rect(panel, (255, 255, 255, 12), (0, 0, panel_w, panel_h), border_radius=16)

        # Title
        func.draw_double_text(panel, "SETTINGS", title_font, title_font, TEXT_COLOR, BLACK, (panel_w // 2, 60))

        # Labels
        func.draw_double_text(panel, "MUSIC", label_font, label_font, TEXT_COLOR, BLACK, (label_x, 140), center=False)
        func.draw_double_text(panel, "SFX", label_font, label_font, TEXT_COLOR, BLACK, (label_x, 240), center=False)
        func.draw_double_text(panel, "SPEED", label_font, label_font, TEXT_COLOR, BLACK, (label_x, 320), center=False)

        # Update ishowspeed variable
        variables.speed = speed_input.get_value()

        # Draw sliders on panel
        music_slider.draw(panel)
        sfx_slider.draw(panel)
        speed_input.draw(panel)

        # Back button
        pygame.draw.rect(panel, (20, 22, 28), back_rect, border_radius=12)
        func.draw_double_text(panel, "BACK", label_font, label_font, TEXT_COLOR, BLACK, back_rect.center)

        # Blit panel to screen
        screen.blit(panel, (panel_x, panel_y))

        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            else:
                mx, my = pygame.mouse.get_pos()
                panel_mx = mx - panel_x
                panel_my = my - panel_y
                original_get_pos = pygame.mouse.get_pos
                pygame.mouse.get_pos = lambda: (panel_mx, panel_my)

                music_slider.handle_event(e)
                sfx_slider.handle_event(e)
                speed_input.handle_event(e, offset=(panel_x, panel_y))

                pygame.mouse.get_pos = original_get_pos

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    back_screen_rect = pygame.Rect(panel_x + back_rect.x, panel_y + back_rect.y, back_rect.w,
                                                   back_rect.h)
                    if back_screen_rect.collidepoint(mx, my):
                        main_menu()

        song_volume = music_slider.value
        sfx_volume = sfx_slider.value

        pygame.mixer.music.set_volume(song_volume)
        if hover_sound:
            hover_sound.set_volume(sfx_volume)

        pygame.display.flip()

def credits_scene():
    global WIDTH, HEIGHT, screen, running

    snapshot = screen.copy()
    blurred = func.blur_surface(snapshot, passes=3, scale_factor=0.25)

    panel_w = int(WIDTH * 0.6)
    panel_h = int(HEIGHT * 0.7)
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_scale = panel_w / BASE_WIDTH

    title_font = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(72 * panel_scale))
    title_font_under = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), int(72 * panel_scale))
    text_font = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), int(36 * panel_scale))
    text_font_under = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), int(36 * panel_scale))

    back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 90, 200, 56)

    credits_lines = [
        "-----------PYTRHYTHM GAME-----------",
        '',
        "-----MAIN CODERS-----",
        "6834418923 NATTHAPOOM PONGPONGSRI",
        "6834421723 TANPONG SANGRUNGARUN",
        "6834430323 PATIPOL CHOTIYANNON",
        '',
        "-----SONGS USED-----",
        "BAD APPLE BY NOMICO",
        "MESMERIZER BY 32KI",
        "MIZUOTO NO CURTAIN BY MIMI",
        "LEMON BY KENSHI YONEZU",
        "TIME FILES BY XI",
        "UNRAVEL BY TK",
        '',
        "THANK YOU FOR PLAYING!",
    ]

    scroll_speed = 1
    spacing = 50
    text_y_positions = [panel_h + i * spacing for i in range(len(credits_lines))]

    while running:
        dt = clock.tick(60)
        screen.blit(blurred, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 160))
        screen.blit(overlay, (0, 0))

        panel.fill((0, 0, 0, 0))
        for i in range(panel_h):
            t = i / panel_h
            r = int(20 + 30 * t)
            g = int(20 + 30 * t)
            b = int(30 + 20 * t)
            panel.fill((r, g, b, 220), rect=pygame.Rect(0, i, panel_w, 1))
        pygame.draw.rect(panel, (255, 255, 255, 12), (0, 0, panel_w, panel_h), border_radius=16)

        func.draw_double_text(screen, "CREDITS", title_font, title_font_under, TEXT_COLOR, BLACK, (WIDTH // 2, 60))

        for i, line in enumerate(credits_lines): #scrolling thing naja dont touch it
            text_y_positions[i] -= scroll_speed
            if text_y_positions[i] < -spacing:  # reset to bottom
                text_y_positions[i] = panel_h + (len(credits_lines) - 1) * spacing
            func.draw_double_text(panel, line, text_font, text_font_under, TEXT_COLOR, BLACK, (panel_w // 2, int(text_y_positions[i])))

        pygame.draw.rect(screen, (20, 22, 28), back_rect, border_radius=12)
        func.draw_double_text(screen, "BACK", text_font, text_font_under, TEXT_COLOR, BLACK, back_rect.center)
        screen.blit(panel, (panel_x, panel_y))

        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if back_rect.collidepoint(mx, my):
                    main_menu()

        pygame.display.flip()

# --- Song selection scene---
def song_selection_screen():
    global WIDTH, HEIGHT, screen, running
    scroll_offset = 0
    scroll_vel = 200 * random.random()
    cover_rotation = 0
    item_height = 200
    ishovered = False
    mx, my = pygame.mouse.get_pos()
    visible_items = HEIGHT // item_height + 5
    current_diff = 'Mas'

    while running:
        screen.fill(BG_COLOR)
        draw_songselect_visualizer(audio_data, sample_rate)
        cover_rotation += 0.005
        diff_color = diffcolor[current_diff]
        scroll_offset += round(scroll_vel)
        playing_song = song_player.song
        if scroll_vel > 0: scroll_vel -= 15
        if scroll_vel < 0: scroll_vel = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
            if cover_rect.collidepoint(mx, my):
                ishovered = True
            else:
                ishovered = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gamb_rect.collidepoint(mx, my):
                    scroll_vel += random.randint(400, 1000)
                diff_collider = {'Ez': ez_rect, 'Adv': adv_rect, 'Exp': exp_rect, 'Mas': mas_rect}
                for key, diffrect in diff_collider.items():
                    if diffrect.collidepoint(mx, my):
                        current_diff = key
                if cover_rect.collidepoint(mx, my):
                    try:
                        gamerun(playing_song, current_diff)
                    except:
                        print('Song is locked')
                        pygame.mixer.music.play()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    load_song_and_background()
                    main_menu()

            if event.type == pygame.MOUSEWHEEL:
                scroll_vel -= event.y * 10

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                WIDTH, HEIGHT = screen.get_size()

        items = [song for song in songsdict.keys()]
        total_height = len(items) * item_height
        scroll_offset = scroll_offset % total_height

        for i in range(-1, visible_items + 1):
            list_index = (int(scroll_offset // item_height) + i) % len(items)
            x = 0
            base_y = i * item_height - (scroll_offset % item_height)
            y = base_y + 200
            selected_index = int(scroll_offset // item_height) % len(items)

            if -item_height - 500 < y < HEIGHT + 200:
                with open(songsdict[items[list_index]]['settings'], 'r') as f:
                    settings = json.load(f)
                if list_index == selected_index:
                    playing_song = items[list_index]
                    song_player.play(playing_song)
                    x -= 50
                song = items[list_index]
                img = pygame.image.load(songsdict[song]['Art']).convert_alpha()
                selectart = pygame.transform.scale(img, (105, 105))
                selectart_rect = selectart.get_rect(topleft=(WIDTH//2 + 225 + x, 0 + y))
                screen.blit(selectart, selectart_rect)

                pygame.draw.polygon(screen, diff_color, ((WIDTH//2 + 220 + x, 0 + y),
                    (WIDTH//2 + 120 + x, 0 + y), (WIDTH//2 + 70 + x, 80 + y), (WIDTH//2 + 170 + x, 80 + y)))
                pygame.draw.polygon(screen, diff_color, ((WIDTH//2 + 100 + x, 0 + y),
                    (WIDTH//2 + 220 + x*2, 0 + y), (WIDTH//2 + 170 + x, 80 + y), (WIDTH//2 + 220 + x*2, 80 + y)))

                pygame.draw.polygon(screen, WHITE, ((WIDTH, 0 + y),
                    (WIDTH//2 + 300 + x, 0 + y), (WIDTH//2 + 300, 80 + y), (WIDTH, 80 + y)))
                pygame.draw.polygon(screen, WHITE, ((WIDTH//2 + 300, 0 + y),
                    (WIDTH, 0 + y), (WIDTH//2 + 170, 80 + y), (WIDTH, 80 + y)))
                pygame.draw.polygon(screen, pygame.Color('Gray'), ((WIDTH, 80 + y),
                    (WIDTH//2 + 70 + x, 80 + y), (WIDTH//2 + 120 + x, 120 + y), (WIDTH, 120 + y)))

                song_text = font_text.render(songsdict[song]['name'], True, BLACK)
                song_rect = song_text.get_rect(midleft=(WIDTH//2 + 400 + x, 60 + y))
                screen.blit(song_text, song_rect)
                diffnum = settings['Difficulty'][current_diff]
                if settings['Difficulty'][current_diff] == 0:
                    diffnum = '-'
                diff_text = font_text_big.render(str(diffnum), True, WHITE)
                diff_rect = diff_text.get_rect(center=(WIDTH//2 + 140 + x, 40 + y))
                screen.blit(diff_text, diff_rect)

        with open(songsdict[song_player.song]['settings'], 'r') as f:
            settings = json.load(f)

        # --- UI (Difficulty Selection, Cover art) ---
        img = pygame.image.load(song_player.cover).convert_alpha()
        cover_art = pygame.transform.scale(img, (HEIGHT * 3.5 // 7, HEIGHT * 3.5 // 7))
        cover_art = pygame.transform.rotate(cover_art, 6 + 3 * math.sin(cover_rotation))
        cover_rect = cover_art.get_rect(center=(WIDTH // 3, HEIGHT * 3 // 7))
        pygame.draw.rect(screen, diff_color, cover_rect.inflate(-40, -40))
        screen.blit(cover_art, cover_rect)

        func.draw_trapezoid(screen, pygame.Color(BG_COLOR2), 0, HEIGHT - 160, WIDTH // 2, 40, -30)
        func.draw_trapezoid(screen, pygame.Color(BG_COLOR2), 0, HEIGHT - 120, WIDTH // 2 + 30, 40, 30)

        if ishovered and settings['Difficulty'][current_diff] != 0:
            img = pygame.image.load(song_player.cover).convert_alpha()
            cover_art = pygame.transform.scale(img, (HEIGHT * 3.5 // 7, HEIGHT * 3.5 // 7))
            cover_art = pygame.transform.rotate(cover_art, 6 + 3 * math.sin(cover_rotation))
            cover_art.fill((0, 0, 0, 155))
            cover_rect = cover_art.get_rect(center=(WIDTH // 3, HEIGHT * 3 // 7))
            screen.blit(cover_art, cover_rect)

            pygame.draw.polygon(screen, WHITE, ((WIDTH // 3-20, HEIGHT * 3 // 7 - 50),      # Top point
                (WIDTH // 3-25, HEIGHT * 3 // 7 + 50),(WIDTH // 3 + 75, HEIGHT * 3 // 7)))

        if settings['Difficulty'][current_diff] == 0:
            cover_art.fill((0, 0, 0, 155))
            screen.blit(cover_art, cover_rect)
            img = pygame.image.load('images/Lock.png').convert_alpha()
            img = pygame.transform.scale(img, (100, 100))
            img_rect = img.get_rect(center=(WIDTH // 3, HEIGHT * 3 // 7))
            screen.blit(img, img_rect)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Ez'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        diffnum = settings['Difficulty']['Ez']
        if diffnum == 0: diffnum = '-'
        ez_diff = font_text.render(str(diffnum),True,WHITE)
        ez_rect = rotated_surface.get_rect(center=(100, HEIGHT - 120))
        ez_text = ez_diff.get_rect(center=(100, HEIGHT - 120))
        screen.blit(rotated_surface, ez_rect)
        screen.blit(ez_diff, ez_text)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Adv'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        diffnum = settings['Difficulty']['Adv']
        if diffnum == 0: diffnum = '-'
        adv_diff = font_text.render(str(diffnum), True, WHITE)
        adv_rect = rotated_surface.get_rect(center=(200, HEIGHT - 120))
        adv_text = adv_diff.get_rect(center=(200, HEIGHT - 120))
        screen.blit(rotated_surface, adv_rect)
        screen.blit(adv_diff, adv_text)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Exp'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        diffnum = settings['Difficulty']['Exp']
        if diffnum == 0: diffnum = '-'
        exp_diff = font_text.render(str(diffnum), True, WHITE)
        exp_rect = rotated_surface.get_rect(center=(300, HEIGHT - 120))
        exp_text = exp_diff.get_rect(center=(300, HEIGHT - 120))
        screen.blit(rotated_surface, exp_rect)
        screen.blit(exp_diff, exp_text)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Mas'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        diffnum = settings['Difficulty']['Mas']
        if diffnum == 0: diffnum = '-'
        mas_diff = font_text.render(str(diffnum), True, WHITE)
        mas_rect = rotated_surface.get_rect(center=(400, HEIGHT - 120))
        mas_text = mas_diff.get_rect(center=(400, HEIGHT - 120))
        screen.blit(rotated_surface, mas_rect)
        screen.blit(mas_diff, mas_text)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, (138, 87, 153), (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        gamb_diff = font_text.render('?', True, WHITE)
        gamb_rect = rotated_surface.get_rect(center=(WIDTH - 100, HEIGHT - 120))
        gamb_text = mas_diff.get_rect(center=(WIDTH - 100, HEIGHT - 120))
        screen.blit(rotated_surface, gamb_rect)
        screen.blit(gamb_diff, gamb_text)

        func.draw_double_text(screen, 'SONG SELECT', font_menu, font_under_menu,
                              WHITE, BLACK, (270, 50), center=False)

        text = font_text_big.render(settings['Name'], True, WHITE)
        text_rect = text.get_rect(midleft=(40, 120))
        screen.blit(text, text_rect)
        screen.blit(text, text_rect)

        text = font_text.render(settings['Artist'], True, WHITE)
        text_rect = text.get_rect(midleft=(40, 160))
        screen.blit(text, text_rect)

        text = font_text.render(f"BPM: {settings['Bpm']}", True, WHITE)
        text_rect = text.get_rect(midleft=(40, 200))
        screen.blit(text, text_rect)

        pygame.display.flip()

# --- Main Menu scene ---
def main_menu():
    global WIDTH, HEIGHT, screen, background_img, black_overlay, running
    buttons = ["PLAY", "SETTINGS", "CREDITS", "EXIT"]
    hovered = -1
    fading = False
    fade_alpha = 0
    old_bg = background_img.copy() if background_img else None
    new_bg = None
    hover_last = -1

    while running:
        dt = clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        # If nothing playing, load a new main-menu random track (only when not in a fade to avoid flicker)
        if not pygame.mixer.music.get_busy() and not fading:
            fading = True
            fade_alpha = 0
            old_bg = background_img.copy() if background_img else None
            load_song_and_background()
            new_bg = background_img.copy() if background_img else None

        if fading and old_bg and new_bg:
            fade_alpha += 5
            if fade_alpha >= 255:
                fade_alpha = 255
                fading = False
                old_bg = None
                background_img = new_bg
                new_bg = None
            if old_bg:
                t_old = pygame.transform.scale(old_bg, (WIDTH, HEIGHT)).copy()
                t_old.set_alpha(255 - fade_alpha)
                screen.blit(t_old, (0, 0))
            if new_bg:
                t_new = pygame.transform.scale(new_bg, (WIDTH, HEIGHT)).copy()
                t_new.set_alpha(fade_alpha)
                screen.blit(t_new, (0, 0))
        else:
            if background_img:
                screen.blit(pygame.transform.scale(background_img, (WIDTH, HEIGHT)), (0, 0))
            else:
                screen.fill(BG_COLOR)

        screen.fill(BLACK)
        # Parallax type shid
        if background_img:
            offset_x = int((mx - WIDTH // 2) * -0.02)
            offset_y = int((my - HEIGHT // 2) * -0.02)
            bg_scaled = pygame.transform.scale(background_img, (WIDTH * 1.1, HEIGHT * 1.1))
            bg_scaled_rect = bg_scaled.get_rect(center=(WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y))
            screen.blit(bg_scaled, bg_scaled_rect)

        if black_overlay.get_size() != (WIDTH, HEIGHT):
            black_overlay = pygame.Surface((WIDTH, HEIGHT))
            black_overlay.fill(BLACK)
            black_overlay.set_alpha(black_opacity)
        screen.blit(black_overlay, (0, 0))
        draw_title()
        y_start = int(HEIGHT // 2 - 100)
        spacing = int(120 * get_scale())
        rects = []
        hovered = -1
        for i, txt in enumerate(buttons):
            y = y_start + i * spacing
            rect = draw_menu_button(txt, y, False)
            if rect.collidepoint(mx, my):
                draw_menu_button(txt, y, True)
                hovered = i

        if hovered != hover_last:
            if hovered != -1 and hover_sound:
                hover_sound.play()
        hover_last = hovered

        draw_cinematic_bars()
        draw_visualizer(audio_data, sample_rate)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                update_fonts()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hovered == 0:
                    song_selection_screen()
                elif hovered == 1:
                    settings_scene()
                elif hovered == 2:
                    credits_scene()
                elif hovered == 3:
                    running = False

        pygame.display.flip()

def gamerun(current_song, difficulty):
    global LANE, JUDGE_LINE
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
    bpm = 185
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    combofont = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_under.ttf"), 40)
    combofontup = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "Platinum_over.ttf"), 40)

    songname_surf = combofont.render(current_song.upper(), False, 'Black')
    songname_surf_up = combofontup.render(current_song.upper(), False, 'White')
    songname_surf = pygame.transform.rotate(songname_surf, 90)
    songname_surf_up = pygame.transform.rotate(songname_surf_up, 90)
    songname_rect = songname_surf.get_rect(bottomleft=(20, HEIGHT-20))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    lane_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sfx', 'lanesound.wav'))
    lane_sound.set_volume(sfx_volume)

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
            # self.metronome()

        def metronome(self):  # flash every quarter note
            if self.lastbeat < 4:
                pygame.draw.circle(screen, WHITE, (800, 500), 20)
            elif self.lastbeat < 8:
                pygame.draw.circle(screen, WHITE, (800, 550), 20)
            elif self.lastbeat < 12:
                pygame.draw.circle(screen, WHITE, (800, 600), 20)
            else:
                pygame.draw.circle(screen, WHITE, (800, 650), 20)

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
                    song_selection_screen()

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
            for i in range(400):
                y_pos = self.y - self.pixel_per_beat * i
                if 0 < y_pos < HEIGHT:
                    pygame.draw.line(screen, pygame.Color('Red'),
                                     (self.lane_start, y_pos),
                                     (self.lane_end, y_pos), 7)
        def updatelane(self):
            self.lane_start = LANE[1][0]
            self.lane_end = LANE[5][0]

    class Note:
        def __init__(self, lane, bar, beat, x, xx):
            self.lane = lane
            self.lanestart = LANE[lane][0]
            self.laneend = LANE[lane+1][0]
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

        def update(self):
            self.lanestart = LANE[self.lane][0]
            self.laneend = LANE[self.lane+1][0]

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
                    judge = 'MARVELOUS'
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT'
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT'
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD'
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS'
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
                    judge = 'MARVELOUS'
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT'
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT'
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD'
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS'
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
                    judge = 'MARVELOUS'
                    Score.acc['MARVELOUS'] += 1
                elif timing_error <= 1:
                    judge = 'PERFECT'
                    Score.acc['PERFECT'] += 1
                elif timing_error <= 2:
                    judge = 'GREAT'
                    Score.acc['GREAT'] += 1
                elif timing_error <= 3:
                    judge = 'GOOD'
                    Score.acc['GOOD'] += 1
                else:
                    judge = 'MISS'
                    Score.acc['MISS'] += 1
                judges.append(judge)
                return True
            return False

        def kys(self):
            notes.remove(self)

        def swipe(self, direction):
            pass

        def update(self):
            self.lanestart = LANE[self.lane][0]
            self.laneend = LANE[self.lane+1][0]

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
                    judge = 'MARVELOUS'
                    if timing_error == 0:
                        judge = 'MARVELOUS'
                        Score.acc['MARVELOUS'] += 1
                    elif timing_error <= 1:
                        judge = 'Perfect'
                        Score.acc['PERFECT'] += 1
                    elif timing_error <= 2:
                        judge = 'Great'
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
        def update(self):
            self.lanestart = LANE[1][0]
            self.laneend = LANE[5][0]

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

        def senddata(self):
            return self.difficulty, self.score, self.maxcombo, self.accuracy, self.acc

    class Interface:
        def __init__(self):
            self.score_scale = 1
            self.score_timer = 0
            self.lastscore = 0
            self.judge_text = ""
            self.judge_color = WHITE
            self.judge_outline = BLACK
            self.judge_scale = 1.0
            self.judge_target_scale = 1.0
            self.judge_timer = 0
            self.judge_debounce = 2

        def display_UI(self):
            playlane_obj = pygame.Surface((400, HEIGHT), pygame.SRCALPHA, 32)
            playlane_rect = playlane_obj.get_rect(center=(((WIDTH / 3) + 200), HEIGHT / 2))
            playlane_obj = playlane_obj.convert_alpha()
            playlane_obj.fill((0, 0, 0, 255))
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
            self.judge_outline = BLACK if text == 'MARVELOUS' else WHITE
            self.judge_scale = 0.8
            self.judge_target_scale = 1
            self.judge_timer = 15
            self.judge_debounce = 10

        def display_info(self):
            if Score.combo > 3:
                combo_img = combofont.render('COMBO', True, (24, 24, 24))
                combo_img_up = combofontup.render('COMBO', True, WHITE)
                combo_rect = combo_img.get_rect(center=((WIDTH / 3) + 200, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 53))
                screen.blit(combo_img, combo_rect)
                combo_rect = combo_img.get_rect(center=((WIDTH / 3) + 200, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 + 49))
                screen.blit(combo_img_up, combo_rect)
                combo_num_img = combofont.render(f"{Score.combo}", True, (24, 24, 24))
                combo_num_img_up = combofontup.render(f"{Score.combo}", True, WHITE)
                combo_rect = combo_num_img.get_rect(center=((WIDTH / 3) + 200, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2))
                screen.blit(combo_num_img, combo_rect)
                combo_rect = combo_num_img.get_rect(center=((WIDTH / 3) + 200, (HEIGHT - (HEIGHT - JUDGE_LINE)) / 2 - 4))
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
                judge_rect = judge_img.get_rect(center=((WIDTH / 3) + 200, HEIGHT * 1 / 3))
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
                judge_rect = judge_img.get_rect(center=((WIDTH / 3) + 200, HEIGHT * 1 / 3))
                screen.blit(judge_img, judge_rect)
                screen.blit(judge_img_up, judge_rect)

        def display_lanes(self):
            pygame.draw.line(screen, pygame.Color('Green'), ((WIDTH / 3),JUDGE_LINE),
                             ((WIDTH / 3 + 400), JUDGE_LINE), 5)
            for i in range(0, 5):
                pygame.draw.line(screen, WHITE, ((WIDTH / 3) + i * 100, 0),
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
    global LANE, JUDGE_LINE
    JUDGE_LINE = HEIGHT - 100
    LANE = {
        1: ((WIDTH / 3), 0),
        2: ((WIDTH / 3) + 100, 0),
        3: ((WIDTH / 3) + 200, 0),
        4: ((WIDTH / 3) + 300, 0),
        5: ((WIDTH / 3) + 400, 0)
    }
    beatline.updatelane()
    for note in notes:
        note.update()
    pygame.key.set_repeat(0, 0)
    Music.play()
    isPaused = False
    while running:
        clock.tick_busy_loop(fps)
        if swipe_cd > 0: swipe_cd -= 1
        screen.fill((30, 30, 30))
        for j in range(30):
            for i in range(-20, 20):
                surf = pygame.Surface((abs(20 - j), abs(20 - j))).convert_alpha()
                surf.fill(WHITE)
                if -WIDTH < i * 40 < WIDTH:
                    screen.blit(surf, (WIDTH / 2 + i * 40, HEIGHT + 100 - j * 45))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            if event.type == pygame.VIDEORESIZE:
                JUDGE_LINE = HEIGHT - 100
                LANE = {
                    1: ((WIDTH / 3), 0),
                    2: ((WIDTH / 3) + 100, 0),
                    3: ((WIDTH / 3) + 200, 0),
                    4: ((WIDTH / 3) + 300, 0),
                    5: ((WIDTH / 3) + 400, 0)
                }
                beatline.updatelane()
                for note in notes:
                    note.update()
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
            difficulty,score,maxcombo,accuracy,acc = Score.senddata()
            result(current_song,difficulty,score,maxcombo,accuracy,acc)

        pygame.display.update()

def result(song,difficulty,score,maxcombo,accuracy,acc):
    pygame.init()

    BASE_WIDTH, BASE_HEIGHT = 1920, 1080

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    scale_x = WIDTH / BASE_WIDTH
    scale_y = HEIGHT / BASE_HEIGHT
    scale = min(scale_x, scale_y)
    songsdict = dir.getsongdict()

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

    song_name = songsdict[song]['name'].upper()
    gradeciteria = {100: 'SSS+', 95: 'SSS', 90: 'SS', 85: 'S', 80: 'A', 60: 'B', 40: 'C', 30: 'D', 10: 'F',
                    0: 'BRUH'}
    for accu, grade in gradeciteria.items():
        if accuracy >= accu:
            grade = grade
            break
    print(grade)
    marvelous = acc['MARVELOUS']
    perfect = acc['PERFECT']
    great = acc['GREAT']
    good = acc['GOOD']
    miss = acc['MISS']

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
                    song_selection_screen()
                elif retry_rect.collidepoint(mouse_pos):
                    gamerun(songsdict[song]['name'], difficulty)

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
        draw_rounded_rect(screen, diffcolor[difficulty], difficulty_rect_approx, 15)  # color change here

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
            screen.blit(stat_font.render(f"{label}", True, BLACK),
                        (label_x, y))  # stat(changing perfect, great, miss)
            screen.blit(stat_font.render(str(value), True, BLACK), (value_x, y))  # stat(changing number)

        # max combo
        max_label_text = stat_font.render("Max Combo", True, BLACK)
        label_rect = max_label_text.get_rect(
            topright=(panel_x + panel_width - int(50 * scale), panel_y + int(57 * scale)))
        screen.blit(max_label_text, label_rect)

        max_value_text = stat_font.render(str(maxcombo), True, BLACK)
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


running = True
main_menu()