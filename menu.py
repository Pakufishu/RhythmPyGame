import sys
import os
import math
from variables import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Rhythm Game Menu")

# Color scheme
TEXT_COLOR = (220, 240, 255)   # ice white-blue
HOVER_COLOR = (255, 255, 0)    # yellow for hover
SELECTED_COLOR = (255, 255, 255)  # red for selected
BASE_GLOW = (0, 200, 255)      # neon cyan
BG_COLOR = (10, 10, 20)        # deep navy
CARD_COLOR = (255, 92, 255)      # darker blue for song cards
CARD_HOVER_COLOR = (255, 92, 255)  # lighter for hover
CARD_TEXT_BACK = (50, 60, 80)

# Fonts
font_title = pygame.font.SysFont(None, 80)
font_song = pygame.font.SysFont(None, 48)
font_info = pygame.font.SysFont(None, 36)
font_button = pygame.font.SysFont(None, 48)
combofont = pygame.font.Font('fonts/Platinum_under.ttf', 40)
combofontup = pygame.font.Font('fonts/Platinum_over.ttf', 40)

background_path = "background2.png"
if os.path.exists(background_path):
    background_img = pygame.image.load(background_path).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
else:
    background_img = None

hover_sound_path = "sfx/hover.wav"
hover_sound = pygame.mixer.Sound(hover_sound_path) if os.path.exists(hover_sound_path) else None

class Song:
    def __init__(self, name, bpm, difficulty, preview_start, genre, folder_path, audio_file, chart_file, image_file):
        self.name = name
        self.bpm = bpm
        self.difficulty = difficulty
        self.preview_start = preview_start
        self.genre = genre
        self.folder_path = folder_path
        self.audio_file = audio_file
        self.chart_file = chart_file
        self.image_file = image_file

def scan_songs():
    songs = []
    songs_dir = "Songs"

    if not os.path.exists(songs_dir):
        return songs
    for folder_name in os.listdir(songs_dir):
        folder_path = os.path.join(songs_dir, folder_name)
        if os.path.isdir(folder_path):
            audio_file = None
            chart_file = None
            for file in os.listdir(folder_path):
                if file.endswith('.mp3'):
                    audio_file = os.path.join(folder_path, file)
                if file.endswith('.txt') and not file.endswith('settings.txt'):
                    chart_file = os.path.join(folder_path, file)
                if file.endswith('.jpg') or file.endswith('.png'):
                    image = os.path.join(folder_path, file)
            metadata_path = os.path.join(folder_path, 'settings.txt')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    info = []
                    for line in f:
                        if line.strip().startswith('Name='):
                            name = line.strip('Name= ').strip()
                            continue
                        data = line.split(' ')[1].strip('\n')
                        try: data = int(data)
                        except:
                            try: data = float(data);
                            except: pass
                        info.append(data)
                    song = Song(name, *info, folder_path, audio_file, chart_file, image)
                    songs.append(song)
    return songs

def render_glow_text(text, font, color, glow_color, glow_strength=4):
    base = font.render(text, True, color)
    glow = font.render(text, True, glow_color)
    surf = pygame.Surface((base.get_width() + 20, base.get_height() + 20), pygame.SRCALPHA)
    for dx in range(-glow_strength, glow_strength + 1):
        for dy in range(-glow_strength, glow_strength + 1):
            if dx**2 + dy**2 <= glow_strength**2:
                surf.blit(glow, (dx + 10, dy + 10))
    surf.blit(base, (10, 10))
    return surf

def draw_menu_button(text, pos_y, hover=False, glow_color=BASE_GLOW):
    color = HOVER_COLOR if hover else TEXT_COLOR
    glow_strength = 8 if hover else 3
    text_surf = render_glow_text(text, font_button, color, glow_color, glow_strength)
    rect = text_surf.get_rect(center=(WIDTH/2, pos_y))
    screen.blit(text_surf, rect)
    return rect

def draw_title(glow_color):
    rhythm = render_glow_text("RHYTHM GAME", font_title, TEXT_COLOR, glow_color, 8)
    rect = rhythm.get_rect(center=(WIDTH/2, 200))
    screen.blit(rhythm, rect)

buttons = ["Play", "Options", "Credits", "Back to desktop"]

def main_menu():
    global running
    running = True
    time_elapsed = 0
    bar_alpha = 0
    bar_fade_speed = 200
    hovered_index = -1
    while running:
        dt = clock.tick(60) / 1000.0
        time_elapsed += dt

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BG_COLOR)

        pulse = (math.sin(time_elapsed * 2.5) + 1) / 2  # 0→1 smoothly
        glow_intensity = (
            int(BASE_GLOW[0] * (0.5 + 0.5 * pulse)),
            int(BASE_GLOW[1] * (0.7 + 0.3 * pulse)),
            int(BASE_GLOW[2])
        )
        draw_title(glow_intensity)

        if bar_alpha < 180:
            bar_alpha += bar_fade_speed * dt
            if bar_alpha > 180:
                bar_alpha = 180
        bar_height = 100
        top_bar = pygame.Surface((WIDTH, bar_height), pygame.SRCALPHA)
        top_bar.fill((0, 0, 0, int(bar_alpha)))
        screen.blit(top_bar, (0, 0))
        bottom_bar = pygame.Surface((WIDTH, bar_height), pygame.SRCALPHA)
        bottom_bar.fill((0, 0, 0, int(bar_alpha)))
        screen.blit(bottom_bar, (0, HEIGHT - bar_height))

        mx, my = pygame.mouse.get_pos()
        base_y = HEIGHT/2 - 30
        spacing = 100
        button_rects = []
        new_hovered_index = -1

        for i, text in enumerate(buttons):
            rect = draw_menu_button(text, base_y + i * spacing, hover=False, glow_color=glow_intensity)
            if rect.collidepoint(mx, my):
                rect = draw_menu_button(text, base_y + i * spacing, hover=True, glow_color=glow_intensity)
                new_hovered_index = i
            button_rects.append(rect)

        if new_hovered_index != hovered_index:
            hovered_index = new_hovered_index
            if hovered_index != -1 and hover_sound:
                hover_sound.play()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        print(f"{buttons[i]} clicked")
                        if buttons[i] == "Play":
                            song_select()
                        if buttons[i] == "Back to desktop":
                            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def draw_carousel_card(song, x, y, width, height, scale=1.0, is_center=False, alpha=255):
    card_surf = pygame.Surface((int(width * scale), int(height * scale)), pygame.SRCALPHA)
    card_color = (*CARD_COLOR, alpha) if not is_center else (*CARD_HOVER_COLOR, alpha)
    if is_center:
        # Center card gets a special glow effect
        glow_color = (*BASE_GLOW, alpha // 2)
        pygame.draw.rect(card_surf, glow_color, (0, 0, int(width * scale), int(height * scale)))
        pygame.draw.rect(card_surf, card_color, (5, 5, int(width * scale) - 10, int(height * scale) - 10))
        pygame.draw.rect(card_surf, (*SELECTED_COLOR, alpha), (0, 0, int(width * scale), int(height * scale)), 4)
    else:
        pygame.draw.rect(card_surf, card_color, (0, 0, int(width * scale), int(height * scale)))
        pygame.draw.rect(card_surf, (*TEXT_COLOR, alpha // 2), (0, 0, int(width * scale), int(height * scale)), 2)

    font_size = int(48 * scale) if is_center else int(36 * scale)
    scaled_font = pygame.font.SysFont(None, max(24, font_size))
    name_color = (*SELECTED_COLOR, alpha) if is_center else (*TEXT_COLOR, alpha)

    # Truncate long names
    display_name = song.name
    if len(display_name) > 15:
        display_name = display_name[:12] + "..."

    name_surf = scaled_font.render(display_name, True, name_color)
    name_rect = name_surf.get_rect(center=(int(width * scale) // 2, int(height * scale)))
    card_surf.blit(name_surf, name_rect)

    # Position the card surface on screen
    final_rect = card_surf.get_rect(center=(x, y))
    screen.blit(card_surf, final_rect)

    image = pygame.image.load(song.image_file).convert()
    image = pygame.transform.scale(image, (int(width * scale * 0.75), int(height * scale * 0.75)))
    image_rect = image.get_rect(center=(x,y))
    screen.blit(image, image_rect)

    return pygame.Rect(final_rect.x, final_rect.y, int(width * scale), int(height * scale))


def draw_navigation_arrow(x, y, direction, is_hovered=False, enabled=True):
    """Draw navigation arrows (left/right)"""
    if not enabled:
        color = (100, 100, 100)
        alpha = 100
    else:
        color = HOVER_COLOR if is_hovered else TEXT_COLOR
        alpha = 255

    # Create arrow surface
    arrow_size = 60 if is_hovered else 50
    arrow_surf = pygame.Surface((arrow_size, arrow_size), pygame.SRCALPHA)

    # Draw arrow shape
    center = arrow_size // 2
    if direction == "left":
        arrow_text = "<"
    else:  # right
        arrow_text = '>'
    if is_hovered and enabled:
        glow_font = pygame.font.SysFont(None, arrow_size + 10)
        glow_surf = glow_font.render(arrow_text, True, (*BASE_GLOW, alpha // 2))
        glow_rect = glow_surf.get_rect(center=(center, center))
        arrow_surf.blit(glow_surf, glow_rect)

    # Draw main arrow
    main_font = pygame.font.SysFont(None, arrow_size)
    main_surf = main_font.render(arrow_text, True, (*color, alpha))
    main_rect = main_surf.get_rect(center=(center, center))
    arrow_surf.blit(main_surf, main_rect)

    # Position on screen
    final_rect = arrow_surf.get_rect(center=(x, y))
    screen.blit(arrow_surf, final_rect)

    return final_rect


def draw_back_button(x, y, is_hovered=False):
    """Draw the back button"""
    color = HOVER_COLOR if is_hovered else TEXT_COLOR
    glow_strength = 6 if is_hovered else 3
    text_surf = render_glow_text("Back", font_button, color, BASE_GLOW, glow_strength)
    rect = text_surf.get_rect(topleft=(x, y))
    screen.blit(text_surf, rect)
    return rect

def song_select():
    global running
    songs = scan_songs()
    current_index = 0  # Currently focused song in center
    time_elapsed = 0
    hovered_left_arrow = False
    hovered_right_arrow = False
    hovered_back = False

    while running:
        dt = clock.tick(fps) / 1000.0
        time_elapsed += dt

        # Background
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BG_COLOR)

        # Animated glow effect
        pulse = (math.sin(time_elapsed * 2.5) + 1) / 2
        glow_intensity = (
            int(BASE_GLOW[0] * (0.5 + 0.5 * pulse)),
            int(BASE_GLOW[1] * (0.7 + 0.3 * pulse)),
            int(BASE_GLOW[2])
        )

        # Title
        title_surf = render_glow_text('idk', font_title, TEXT_COLOR, glow_intensity, 8)
        title_rect = title_surf.get_rect(center=(WIDTH / 2, 80))
        screen.blit(title_surf, title_rect)

        # Get mouse position
        mx, my = pygame.mouse.get_pos()

        # Reset hover states
        hovered_left_arrow = False
        hovered_right_arrow = False
        hovered_back = False

        # Carousel layout parameters
        center_x = WIDTH // 2
        center_y = HEIGHT // 2 - 50
        card_width = 300
        card_height = 300
        side_card_width = 200
        side_card_height = 200
        spacing = 250

        # Draw carousel cards
        visible_range = 2  # Show 2 cards on each side of center
        song_rects = []

        for i in range(-visible_range, visible_range + 1):
            song_index = (current_index + i) % len(songs)
            song = songs[song_index]

            offset_x = i * spacing
            x = center_x + offset_x
            y = center_y

            # Center card is largest and most prominent
            is_center = (i == 0)
            if is_center:
                scale = 1.0
                alpha = 255
                width, height = card_width, card_height
            else:
                distance = abs(i)
                scale = max(0.6, 1.0 - (distance * 0.1))
                alpha = 80
                width, height = side_card_width, side_card_height

            if -width < x < WIDTH + width:
                card_rect = draw_carousel_card(song, x, y, width, height, scale, is_center, alpha)
                if is_center:
                    song_rects.append((card_rect, song_index))

        # Navigation arrows
        left_arrow_x = 80
        right_arrow_x = WIDTH - 80
        arrow_y = center_y

        left_arrow_enabled = len(songs) > 1
        right_arrow_enabled = len(songs) > 1

        left_arrow_rect = draw_navigation_arrow(left_arrow_x, arrow_y, "left", hovered_left_arrow, left_arrow_enabled)
        right_arrow_rect = draw_navigation_arrow(right_arrow_x, arrow_y, "right", hovered_right_arrow,
                                                 right_arrow_enabled)

        # Check arrow hovers
        if left_arrow_rect.collidepoint(mx, my) and left_arrow_enabled:
            hovered_left_arrow = True
            draw_navigation_arrow(left_arrow_x, arrow_y, "left", hovered_left_arrow, left_arrow_enabled)

        if right_arrow_rect.collidepoint(mx, my) and right_arrow_enabled:
            hovered_right_arrow = True
            draw_navigation_arrow(right_arrow_x, arrow_y, "right", hovered_right_arrow, right_arrow_enabled)

        current_song = songs[current_index]
        info_y = HEIGHT - 120

        info_panel = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 200))
        screen.blit(info_panel, (0, info_y))

        # Song details
        title_text = current_song.name
        title_surf = font_song.render(title_text, True, SELECTED_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH / 2, info_y + 30))
        screen.blit(title_surf, title_rect)

        details_text = f"BPM: {current_song.bpm} | Difficulty: {current_song.difficulty}"
        details_surf = font_info.render(details_text, True, TEXT_COLOR)
        details_rect = details_surf.get_rect(center=(WIDTH / 2, info_y + 65))
        screen.blit(details_surf, details_rect)

        back_rect = draw_back_button(30, HEIGHT - 60, hovered_back)
        if back_rect.collidepoint(mx, my):
            hovered_back = True
            draw_back_button(30, HEIGHT - 60, hovered_back)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_LEFT:
                    if len(songs) > 1:
                        current_index = (current_index - 1) % len(songs)
                        if hover_sound:
                            hover_sound.play()
                elif event.key == pygame.K_RIGHT:
                    if len(songs) > 1:
                        current_index = (current_index + 1) % len(songs)
                        if hover_sound:
                            hover_sound.play()
                elif event.key == pygame.K_RETURN:
                    return songs[current_index]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_rect.collidepoint(event.pos):
                        main_menu()

                    # Check navigation arrows
                    if left_arrow_rect.collidepoint(event.pos) and left_arrow_enabled:
                        current_index = (current_index - 1) % len(songs)
                        if hover_sound:
                            hover_sound.play()
                    elif right_arrow_rect.collidepoint(event.pos) and right_arrow_enabled:
                        current_index = (current_index + 1) % len(songs)
                        if hover_sound:
                            hover_sound.play()

                    # Check center card (click to select)
                    elif song_rects:
                        center_rect, song_idx = song_rects[0]
                        if center_rect.collidepoint(event.pos):
                            return songs[current_index]

        pygame.display.flip()
    return None

running = True
song_select()