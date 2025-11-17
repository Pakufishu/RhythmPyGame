import sys
import os
import pygame
import numpy as np
from scipy.io import wavfile
import random
import dir

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

# --- Asset folders ---
songsdict = dir.getsongdict()
SONGS_FOLDER = "Songs"
COVERS_FOLDER = "covers"

# --- Load all backgrounds and music ---
class SongPlayer:
    def __init__(self):
        self.song = 'Mesmerizer'
        self.songplaytrack = []
        self.music = songsdict[self.song]['Music']

    def play(self):
        pass

    def randomSong(self):
        self.song = random.choice(list(songsdict.keys()))
        self.music = songsdict[self.song]['Music']
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
hover_sound = pygame.mixer.Sound("sfx/hover.wav") if os.path.exists("sfx/hover.wav") else None
other_sfx = pygame.mixer.Sound("sfx.wav") if os.path.exists("sfx.wav") else None


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

def update_fonts():
    global font_title, font_menu, font_under_title, font_under_menu
    scale = get_scale()
    try:
        font_title = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(70 * scale))
        font_under_title = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(70 * scale))
        font_menu = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(50 * scale))
        font_under_menu = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(50 * scale))
    except Exception:
        font_title = pygame.font.SysFont("arial", int(120 * scale))
        font_under_title = pygame.font.SysFont("arial", int(120 * scale))
        font_menu = pygame.font.SysFont("bahnschrift", int(80 * scale))
        font_under_menu = pygame.font.SysFont("bahnschrift", int(80 * scale))

update_fonts()

# --- Double text helper ---
def draw_double_text(text, font_top, font_bottom, color_top, color_bottom, pos, offset=(4, 4), center=True,
                     surface=None):
    if surface is None:
        surface = screen
    surf_bottom = font_bottom.render(text, True, color_bottom)
    rect_bottom = surf_bottom.get_rect(center=pos if center else pos)
    rect_bottom.move_ip(offset)
    surface.blit(surf_bottom, rect_bottom)
    surf_top = font_top.render(text, True, color_top)
    rect_top = surf_top.get_rect(center=pos if center else pos)
    surface.blit(surf_top, rect_top)
    return rect_top

# --- Title ---
def draw_title():
    draw_double_text("RHYTHM GAME", font_title, font_under_title, TEXT_COLOR, BLACK, (WIDTH / 2, HEIGHT * 0.18))


# --- Menu button ---
def draw_menu_button(text, y, hover=False):
    color_top = HOVER_COLOR if hover else TEXT_COLOR
    color_bottom = BLACK
    return draw_double_text(text, font_menu, font_under_menu, color_top, color_bottom, (WIDTH / 2, y))

# --- Visualizer ---
bar_values = np.zeros(60)

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

# --- High-quality blur ---
def blur_surface(surface, passes=3, scale_factor=0.25):
    if scale_factor <= 0 or scale_factor >= 1:
        return surface.copy()
    result = surface.copy()
    for _ in range(passes):
        w = max(2, int(result.get_width() * scale_factor))
        h = max(2, int(result.get_height() * scale_factor))
        try:
            small = pygame.transform.smoothscale(result, (w, h))
            result = pygame.transform.smoothscale(small, surface.get_size())
        except Exception:
            return surface.copy()
    return result

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
    global WIDTH, HEIGHT, screen, hover_sound
    snapshot = screen.copy()
    blurred = blur_surface(snapshot, passes=3, scale_factor=0.25)
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

    running = True
    while running:
        dt = clock.tick(60)
        screen.blit(blurred, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 160))
        screen.blit(overlay, (0, 0))

        # Draw panel gradient
        for i in range(panel_h):
            t = i / panel_h
            r = int(20 + 30 * t);
            g = int(20 + 30 * t);
            b = int(30 + 20 * t)
            panel.fill((r, g, b, 220), rect=pygame.Rect(0, i, panel_w, 1))
        pygame.draw.rect(panel, (255, 255, 255, 12), (0, 0, panel_w, panel_h), border_radius=16)

        # Title
        draw_double_text("SETTINGS", title_font, title_font, TEXT_COLOR, BLACK, (panel_w // 2, 60), surface=panel)

        # Labels
        draw_double_text("MUSIC", title_font, title_font, TEXT_COLOR, BLACK, (100, 135), surface=panel)
        draw_double_text("SFX", title_font, title_font, TEXT_COLOR, BLACK, (100, 235), center=False, surface=panel)

        # Sliders
        music_slider.draw(screen)
        sfx_slider.draw(screen)

        # Back button
        back_rect = pygame.Rect(panel_w // 2 - 100, panel_h - 90, 200, 56)
        pygame.draw.rect(panel, (70, 160, 255), back_rect, border_radius=12)
        draw_double_text("BACK", label_font, label_font, TEXT_COLOR, BLACK, (panel_w // 2, panel_h - 90 + 28),
                         surface=panel)

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
                    if back_screen_rect.collidepoint(mx, my): running = False

        pygame.mixer.music.set_volume(music_slider.value)
        if hover_sound: hover_sound.set_volume(sfx_slider.value)
        pygame.display.flip()

# --- Song selection screen with instant preview, double underline and lowered layout ---
def song_selection_screen():
    global WIDTH, HEIGHT, screen, music_files

    if not music_files:
        return

    running = True
    selected = 0
    current_previewed_song = None

    title_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(65 * get_scale()))
    song_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(50 * get_scale()))
    play_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(60 * get_scale()))

    arrow_size = 60
    arrow_padding = 30

    # Stop whatever was playing on main menu and start preview of the first selected song
    def start_preview(song_filename):
        nonlocal current_previewed_song
        try:
            pygame.mixer.music.stop()
            preview_path = os.path.join(MUSIC_FOLDER, song_filename)
            pygame.mixer.music.load(preview_path)
            pygame.mixer.music.set_volume(0.06)  # low-volume preview
            pygame.mixer.music.play(-1)
            current_previewed_song = song_filename
        except Exception as ex:
            print("Preview error:", ex)
            current_previewed_song = None

    # initial preview
    start_preview(music_files[selected])

    # Layout: shift title up and box down so things are not stacked
    title_y = int(HEIGHT * 0.12)
    box_y = int(HEIGHT * 0.25)  # lowered so title and underlines have space

    while running:
        dt = clock.tick(60)
        screen.fill(BG_COLOR)

        # Title + double underline (white)
        title_pos = (WIDTH // 2, title_y)
        title_rect = draw_double_text("SONG SELECTION", title_font, title_font, TEXT_COLOR, BLACK, title_pos)
        # two white underlines
        underline_height = 4
        underline_gap = 8
        ux1 = title_rect.left
        ux2 = title_rect.right
        uy = title_rect.bottom + 8
        pygame.draw.rect(screen, (255, 255, 255), (ux1, uy, ux2 - ux1, underline_height))
        pygame.draw.rect(screen, (255, 255, 255),
                         (ux1, uy + underline_height + underline_gap, ux2 - ux1, underline_height))

        # Center box
        box_width = int(WIDTH * 0.5)
        box_height = int(HEIGHT * 0.45)
        box_x = (WIDTH - box_width) // 2
        pygame.draw.rect(screen, (50, 50, 60), (box_x, box_y, box_width, box_height), border_radius=16)
        pygame.draw.rect(screen, (200, 200, 220), (box_x, box_y, box_width, box_height), 3, border_radius=16)

        # Song cover (attempt to fill box entirely; center-cropped if aspect differs)
        song_file = music_files[selected]
        song_name = os.path.splitext(song_file)[0]
        cover_file = os.path.join(COVERS_FOLDER, f"{song_name}.png")
        if os.path.exists(cover_file):
            try:
                cover_img = pygame.image.load(cover_file).convert_alpha()
                # We want the cover to fill the box as much as possible without leaving margins.
                # Compute scale so the smaller dimension fills, then crop centered if needed.
                bw, bh = box_width, box_height
                iw, ih = cover_img.get_width(), cover_img.get_height()
                scale = max(bw / iw, bh / ih)  # fill (cover may overflow one axis)
                new_w = int(iw * scale)
                new_h = int(ih * scale)
                scaled = pygame.transform.smoothscale(cover_img, (new_w, new_h))
                # crop center to box size
                crop_x = max(0, (new_w - bw) // 2)
                crop_y = max(0, (new_h - bh) // 2)
                cover_surface = pygame.Surface((bw, bh), pygame.SRCALPHA)
                cover_surface.blit(scaled, (-crop_x, -crop_y))
                screen.blit(cover_surface, (box_x, box_y))
            except Exception as e:
                print("Error loading cover:", e)

        # Song name above box (outside box)
        draw_double_text(song_name, song_font, song_font, TEXT_COLOR, BLACK, (WIDTH // 2, box_y - 40))

        # PLAY button below the box (outside)
        play_rect = pygame.Rect(0, 0, 220, 64)
        play_rect.center = (WIDTH // 2, box_y + box_height + 80)
        pygame.draw.rect(screen, (70, 160, 255), play_rect, border_radius=12)
        draw_double_text("PLAY", play_font, play_font, TEXT_COLOR, BLACK, play_rect.center)

        # Arrows (left/right) to switch song
        left_rect = pygame.Rect(box_x - arrow_size - arrow_padding, box_y + box_height // 2 - arrow_size // 2,
                                arrow_size, arrow_size)
        right_rect = pygame.Rect(box_x + box_width + arrow_padding, box_y + box_height // 2 - arrow_size // 2,
                                 arrow_size, arrow_size)
        pygame.draw.polygon(screen, ARROW_COLOR, [(left_rect.right, left_rect.top), (left_rect.right, left_rect.bottom),
                                                  (left_rect.left, left_rect.centery)])
        pygame.draw.polygon(screen, ARROW_COLOR,
                            [(right_rect.left, right_rect.top), (right_rect.left, right_rect.bottom),
                             (right_rect.right, right_rect.centery)])

        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                update_fonts()
                # recompute positions next loop
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if play_rect.collidepoint(mx, my):
                    # Play full selected song (stop preview and play song at normal volume)
                    try:
                        pygame.mixer.music.stop()
                        song_path = os.path.join(MUSIC_FOLDER, song_file)
                        pygame.mixer.music.load(song_path)
                        pygame.mixer.music.set_volume(0.12)
                        pygame.mixer.music.play(-1)
                    except Exception as ex:
                        print("Error loading selected song:", ex)
                    running = False
                elif left_rect.collidepoint(mx, my):
                    selected = (selected - 1) % len(music_files)
                    sf = music_files[selected]
                    if current_previewed_song != sf:
                        start_preview(sf)
                elif right_rect.collidepoint(mx, my):
                    selected = (selected + 1) % len(music_files)
                    sf = music_files[selected]
                    if current_previewed_song != sf:
                        start_preview(sf)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # stop preview and return to main menu (main menu will later potentially load background music again)
                    pygame.mixer.music.stop()
                    running = False

        pygame.display.flip()

# --- Main menu ---
def main_menu():
    global WIDTH, HEIGHT, screen, background_img, black_overlay
    running = True
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
            offset_x = int((mx - WIDTH / 2) * 0.05)
            offset_y = int((my - HEIGHT / 2) * 0.05)
            bg_scaled = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
            screen.blit(bg_scaled, (offset_x, offset_y))

        if black_overlay.get_size() != (WIDTH, HEIGHT):
            black_overlay = pygame.Surface((WIDTH, HEIGHT))
            black_overlay.fill(BLACK)
            black_overlay.set_alpha(black_opacity)
        screen.blit(black_overlay, (0, 0))
        draw_title()
        y_start = int(HEIGHT * 0.5)
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
                    # Enter song selection (this will stop the main-menu music and start previews)
                    song_selection_screen()
                elif hovered == 1:
                    settings_scene()
                elif hovered == 2:
                    print("Credits Scene")
                elif hovered == 3:
                    running = False

        pygame.display.flip()

# --- Run main menu ---
if __name__ == "__main__":
    main_menu()
    pygame.quit()
    sys.exit()