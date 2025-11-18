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

pygame.init()

# --- Screen settings ---
WIDTH, HEIGHT = 1080, 720
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
ARROW_COLOR = (255, 255, 255)

# --- Asset folders dict ---
songsdict = dir.getsongdict()

# --- Load backgrounds and music ---
class SongPlayer:
    def __init__(self):
        self.song = 'Mesmerizer'
        self.songplaytrack = []
        self.songdic = songsdict[self.song]
        self.music = songsdict[self.song]['Music']
        self.cover = songsdict[self.song]['Art']

    def play(self):
        pass

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
        self.background_img = pygame.transform.scale(img, (WIDTH+100, HEIGHT+100))

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
hover_sound = pygame.mixer.Sound("sfx/hover.wav")
# other_sfx = pygame.mixer.Sound("sfx.wav")

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
with open(songsdict[song_player.song]['settings'],'r') as f:
    settings = json.load(f)
print(song_player.song)
print(settings)

# --- Font setup ---
def get_scale():
    return min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)

def update_fonts():
    global font_title, font_menu, font_under_title, font_under_menu, font_text, font_text_big
    scale = get_scale()
    font_title = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(70 * scale))
    font_under_title = pygame.font.Font(os.path.join("fonts", "Platinum_under.ttf"), int(70 * scale))
    font_menu = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(50 * scale))
    font_under_menu = pygame.font.Font(os.path.join("fonts", "Platinum_under.ttf"), int(50 * scale))
    font_text = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(30 * scale))
    font_text_big = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(50 * scale))

update_fonts()

# --- Title ---
def draw_title():
    func.draw_double_text(screen,"RHYTHM GAME", font_title, font_under_title, TEXT_COLOR, BLACK, (WIDTH / 2, HEIGHT * 0.18))

# --- Menu button ---
def draw_menu_button(text, y, hover=False):
    color_top = HOVER_COLOR if hover else TEXT_COLOR
    color_bottom = BLACK
    return func.draw_double_text(screen, text, font_menu, font_under_menu, color_top, color_bottom, (WIDTH / 2, y), center=True)

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

# --- Cinematic bars ---
def draw_cinematic_bars():
    h = int(HEIGHT * 0.05)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, h))
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - h, WIDTH, h))

# --- Slider class (unchanged) ---
class Slider:
    def __init__(self, x, y, width, value=0.5):
        self.x, self.y, self.width, self.value = int(x), int(y), int(width), float(value)
        self.height, self.handle_radius = 8, 12
        self.dragging = False

    def draw(self, surf):
        pygame.draw.rect(surf, (140, 140, 160), (self.x, self.y - self.height // 2, self.width, self.height),
                         border_radius=4)
        pygame.draw.rect(surf, (60, 200, 255),
                         (self.x, self.y - self.height // 2, int(self.width * self.value), self.height),
                         border_radius=4)
        hx = self.x + int(self.value * self.width)
        pygame.draw.circle(surf, (250, 250, 250), (hx, self.y), self.handle_radius)
        pygame.draw.circle(surf, (100, 100, 120), (hx, self.y), self.handle_radius, 3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            hx = self.x + int(self.value * self.width)
            if (mx - hx) ** 2 + (my - self.y) ** 2 <= self.handle_radius ** 2: self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx = event.pos[0]
            self.value = max(0.0, min(1.0, (mx - self.x) / self.width))

# --- Settings scene ---
def settings_scene():
    global WIDTH, HEIGHT, screen, hover_sound, running
    snapshot = screen.copy()
    blurred = func.blur_surface(snapshot, passes=3, scale_factor=0.25)
    panel_w = int(WIDTH * 0.5)
    panel_h = int(HEIGHT * 0.68)
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

    panel_scale = panel_w / BASE_WIDTH
    title_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(72 * panel_scale))
    label_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(40 * panel_scale))

    slider_width = int(panel_w * 0.55)
    music_slider = Slider(panel_x + 220, panel_y + 140, slider_width,
                          pygame.mixer.music.get_volume() if pygame.mixer.music.get_busy() else 0.1)
    sfx_slider = Slider(panel_x + 220, panel_y + 240, slider_width, hover_sound.get_volume() if hover_sound else 0.5)

    while running:
        dt = clock.tick(60)
        screen.blit(blurred, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 160))
        screen.blit(overlay, (0, 0))

        # Draw panel gradient
        for i in range(panel_h):
            t = i / panel_h
            r = int(20 + 30 * t)
            g = int(20 + 30 * t)
            b = int(30 + 20 * t)
            panel.fill((r, g, b, 220), rect=pygame.Rect(0, i, panel_w, 1))
        pygame.draw.rect(panel, (255, 255, 255, 12), (0, 0, panel_w, panel_h), border_radius=16)

        # Title
        func.draw_double_text(screen,"SETTINGS", title_font, title_font, TEXT_COLOR, BLACK, (panel_w // 2, 60))

        # Labels
        func.draw_double_text(screen,"MUSIC", title_font, title_font, TEXT_COLOR, BLACK, (100, 135))
        func.draw_double_text(screen,"SFX", title_font, title_font, TEXT_COLOR, BLACK, (100, 235), center=False)

        # Sliders
        music_slider.draw(screen)
        sfx_slider.draw(screen)

        # Back button
        back_rect = pygame.Rect(panel_w // 2 - 100, panel_h - 90, 200, 56)
        pygame.draw.rect(panel, (70, 160, 255), back_rect, border_radius=12)
        func.draw_double_text(screen,"BACK", label_font, label_font, TEXT_COLOR, BLACK, (panel_w // 2, panel_h - 90 + 28))

        screen.blit(panel, (panel_x, panel_y))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            else:
                music_slider.handle_event(e)
                sfx_slider.handle_event(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    back_screen_rect = pygame.Rect(panel_x + back_rect.x, panel_y + back_rect.y, back_rect.w,
                                                   back_rect.h)
                    if back_screen_rect.collidepoint(mx, my):
                        main_menu()

        pygame.mixer.music.set_volume(music_slider.value)
        if hover_sound: hover_sound.set_volume(sfx_slider.value)
        pygame.display.flip()

def start_preview(song_file):
    pygame.mixer.music.load(song_file)
    pygame.mixer.music.set_volume(0.06)
    pygame.mixer.music.play(-1 ,settings['Preview_start'])

# --- Song selection scene---
def song_selection_screen():
    global WIDTH, HEIGHT, screen, running
    cover_rotation = 0
    while running:
        screen.fill(BG_COLOR)
        cover_rotation += 0.001

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if cover_rect.collidepoint(mx, my):
                    print('k')

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * 4

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                global HEIGHT, WIDTH
                WIDTH, HEIGHT = screen.get_size()

        img = pygame.image.load(song_player.cover).convert_alpha()
        cover_art = pygame.transform.scale(img, (HEIGHT*3.5 // 7, HEIGHT*3.5 // 7))
        cover_art = pygame.transform.rotate(cover_art, 6 + 3*math.sin(cover_rotation))
        cover_rect = cover_art.get_rect(midbottom=(WIDTH//3, HEIGHT*3//4))
        screen.blit(cover_art, cover_rect)

        img = pygame.image.load(song_player.cover).convert_alpha()
        selectart = pygame.transform.scale(img, (80, 80))
        selectart_rect = selectart.get_rect(topleft=(WIDTH-300,200))

        screen.blit(selectart, selectart_rect)

        pygame.draw.polygon(screen, pygame.Color('Purple'), ((WIDTH-300, 200),
                                    (WIDTH-400, 200), (WIDTH-450, 280), (WIDTH-350, 280)))
        pygame.draw.polygon(screen, pygame.Color('White'), ((WIDTH, 200),
                                    (WIDTH - 220, 200), (WIDTH - 270, 280),(WIDTH, 280)))
        diff_text = font_text_big.render(str(settings['Difficulty']), True, pygame.Color('White'))
        diff_rect = diff_text.get_rect(center=(WIDTH - 380, 240))
        screen.blit(diff_text, diff_rect)

        func.draw_trapezoid(screen, pygame.Color('White'), 200, HEIGHT-160, 400, 40, -20)
        func.draw_trapezoid(screen, pygame.Color('White'), 200, HEIGHT-120, 420, 40, 20)
        func.draw_trapezoid(screen, pygame.Color('Gray'), 0, HEIGHT-160, 380, 40, -20)
        func.draw_trapezoid(screen, pygame.Color('Gray'), 0, HEIGHT-120, 400, 40, 20)
        func.draw_trapezoid(screen, pygame.Color('Pink'), 0, HEIGHT-160, 260, 40, -20)
        func.draw_trapezoid(screen, pygame.Color('Pink'), 0, HEIGHT-120, 280, 40, 20)
        func.draw_trapezoid(screen, pygame.Color('Red'), 0, HEIGHT-160, 180, 40, -20)
        func.draw_trapezoid(screen, pygame.Color('Red'), 0, HEIGHT-120, 200, 40, 20)

        func.draw_double_text(screen, 'SONG SELECT', font_menu, font_under_menu,
                            pygame.Color('White'), pygame.Color('Black'), (270,50), center=False)

        text = font_text_big.render(song_player.song, True, pygame.Color('White'))
        text_rect = text.get_rect(midleft=(40,120))
        screen.blit(text, text_rect)

        text = font_text.render(settings['Artist'], True, pygame.Color('White'))
        text_rect = text.get_rect(midleft=(40, 160))
        screen.blit(text, text_rect)

        text = font_text.render(f'BPM: {settings['Bpm']}', True, pygame.Color('White'))
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
            fading = True;
            fade_alpha = 0
            old_bg = background_img.copy() if background_img else None
            load_song_and_background()
            new_bg = background_img.copy() if background_img else None

        if fading and old_bg and new_bg:
            fade_alpha += 5
            if fade_alpha >= 255:
                fade_alpha = 255;
                fading = False;
                old_bg = None;
                background_img = new_bg;
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
            bg_scaled = pygame.transform.scale(background_img, (WIDTH*1.1, HEIGHT*1.1))
            bg_scaled_rect = bg_scaled.get_rect(center=(WIDTH//2 + offset_x, HEIGHT//2 + offset_y))
            screen.blit(bg_scaled, bg_scaled_rect)

        if black_overlay.get_size() != (WIDTH, HEIGHT):
            black_overlay = pygame.Surface((WIDTH, HEIGHT))
            black_overlay.fill(BLACK)
            black_overlay.set_alpha(black_opacity)
        screen.blit(black_overlay, (0, 0))
        draw_title()
        y_start = int(HEIGHT//2 - 100)
        spacing = int(120 * get_scale())
        rects = []
        hovered = -1
        for i, txt in enumerate(buttons):
            y = y_start + i * spacing
            rect = draw_menu_button(txt, y, False)
            if rect.collidepoint(mx, my):
                rect = draw_menu_button(txt, y, True)
                hovered = i
            rects.append(rect)

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