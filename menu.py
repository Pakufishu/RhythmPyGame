import sys
import os
import pygame
import numpy as np
from scipy.io import wavfile
import random
import dir
import function as func
import json
import math
from variables import *
import game

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
HOVER_COLOR = (255, 255, 0)
BG_COLOR = (10, 10, 20)
BG_COLOR2 = (20, 22, 28)

ARROW_COLOR = (255, 255, 255)

# --- Asset folders dict ---
songsdict = dir.getsongdict()


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
            pygame.mixer.music.set_volume(0.1)
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

# --- Globals ---
background_img = None
audio_data = None
sample_rate = None
last_song = None

# --- Black overlay ---
black_overlay = pygame.Surface((WIDTH, HEIGHT))
black_overlay.fill(BLACK)
black_opacity = 100
black_overlay.set_alpha(black_opacity)

# --- Hover & other SFX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
hover_sound_path = os.path.join(BASE_DIR, "sfx", "hover.wav")
hover_sound = pygame.mixer.Sound(hover_sound_path)


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
        pygame.mixer.music.set_volume(0.1)
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
    global WIDTH, HEIGHT, screen, hover_sound, running

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
        pygame.draw.rect(panel, (70, 160, 255), back_rect, border_radius=12)
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

        pygame.mixer.music.set_volume(music_slider.value)
        if hover_sound:
            hover_sound.set_volume(sfx_slider.value)

        pygame.display.flip()


def start_preview(song_file, settings_file):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    pygame.mixer.music.load(song_file)
    pygame.mixer.music.set_volume(0.06)
    pygame.mixer.music.play(-1, settings["Preview_start"] * 1000)


# --- Song selection scene---
def song_selection_screen():
    global WIDTH, HEIGHT, screen, running
    scroll_offset = 0
    scroll_vel = 0
    cover_rotation = 0
    item_height = 200
    visible_items = HEIGHT // item_height + 5
    current_diff = 'Mas'

    while running:
        screen.fill(BG_COLOR)
        draw_songselect_visualizer(audio_data, sample_rate)
        cover_rotation += 0.002
        diff_color = diffcolor[current_diff]
        scroll_offset += round(scroll_vel)
        if scroll_vel > 0: scroll_vel -= 15
        if scroll_vel < 0: scroll_vel = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                diff_collider = {'Ez': ez_rect, 'Adv': adv_rect, 'Exp': exp_rect, 'Mas': mas_rect}
                for key, diffrect in diff_collider.items():
                    if diffrect.collidepoint(mx, my):
                        current_diff = key

                if cover_rect.collidepoint(mx, my):
                    game.run(song, current_diff)

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
            y = base_y + 200  # Center the list vertically
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
                selectart_rect = selectart.get_rect(topleft=(WIDTH - 325 + x, 0 + y))
                screen.blit(selectart, selectart_rect)

                pygame.draw.polygon(screen, diff_color, ((WIDTH - 300 + x, 0 + y),
                                    (WIDTH - 400 + x, 0 + y), (WIDTH - 450 + x, 80 + y), (WIDTH - 350 + x, 80 + y)))
                pygame.draw.polygon(screen, diff_color, ((WIDTH - 400 + x, 0 + y),
                                    (WIDTH - 300 + x*2, 0 + y), (WIDTH - 350 + x, 80 + y), (WIDTH - 250 + x*2, 80 + y)))
                pygame.draw.polygon(screen, pygame.Color('White'), ((WIDTH, 0 + y),
                                    (WIDTH - 220 + x, 0 + y), (WIDTH - 270, 80 + y), (WIDTH, 80 + y)))
                pygame.draw.polygon(screen, pygame.Color('White'), ((WIDTH - 300, 0 + y),
                                    (WIDTH - 220 + x, 0 + y), (WIDTH - 270, 80 + y), (WIDTH, 80 + y)))
                pygame.draw.polygon(screen, pygame.Color('Gray'), ((WIDTH, 80 + y),
                                    (WIDTH - 450 + x, 80 + y), (WIDTH - 270 + x, 120 + y), (WIDTH, 120 + y)))

                song_text = font_text.render(songsdict[song]['name'], True, BLACK)
                song_rect = song_text.get_rect(midleft=(WIDTH - 200 + x, 60 + y))
                screen.blit(song_text, song_rect)
                diff_text = font_text_big.render(str(settings['Difficulty'][current_diff]), True, pygame.Color('White'))
                diff_rect = diff_text.get_rect(center=(WIDTH - 380 + x, 40 + y))
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

        ez_rect = rotated_surface.get_rect(center=(100, HEIGHT - 120))
        screen.blit(rotated_surface, ez_rect)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Adv'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)

        adv_rect = rotated_surface.get_rect(center=(250, HEIGHT - 120))
        screen.blit(rotated_surface, adv_rect)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Exp'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)
        exp_rect = rotated_surface.get_rect(center=(400, HEIGHT - 120))
        screen.blit(rotated_surface, exp_rect)

        square_surface = pygame.Surface((75, 75), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, diffcolor['Mas'], (0, 0, 75, 75))
        rotated_surface = pygame.transform.rotate(square_surface, 45)

        mas_rect = rotated_surface.get_rect(center=(550, HEIGHT - 120))
        screen.blit(rotated_surface, mas_rect)

        func.draw_double_text(screen, 'SONG SELECT', font_menu, font_under_menu,
                              pygame.Color('White'), pygame.Color('Black'), (270, 50), center=False)

        text = font_text_big.render(settings['Name'], True, pygame.Color('White'))
        text_rect = text.get_rect(midleft=(40, 120))
        screen.blit(text, text_rect)
        screen.blit(text, text_rect)

        text = font_text.render(settings['Artist'], True, pygame.Color('White'))
        text_rect = text.get_rect(midleft=(40, 160))
        screen.blit(text, text_rect)

        text = font_text.render(f"BPM: {settings['Bpm']}", True, pygame.Color('White'))
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

    parallax_offsets = [0, 0.0, 0.0]  # layers
    parallax_speeds = [0.02, 0.05, 0.08]  # speed

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
                    print("Credits Scene")
                elif hovered == 3:
                    running = False

        pygame.display.flip()
running = True
main_menu()