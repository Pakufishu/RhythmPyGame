import sys
import os
import math
import json
from variables import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Song Selection")

# Color scheme
TEXT_COLOR = (220, 240, 255)   # ice white-blue
HOVER_COLOR = (255, 255, 0)    # yellow for hover
SELECTED_COLOR = (255, 100, 100)  # red for selected
BASE_GLOW = (0, 200, 255)      # neon cyan
BG_COLOR = (10, 10, 20)        # deep navy
CARD_COLOR = (30, 40, 60)      # darker blue for song cards
CARD_HOVER_COLOR = (50, 60, 80)  # lighter for hover

# Fonts
font_title = pygame.font.SysFont(None, 80)
font_song = pygame.font.SysFont(None, 48)
font_info = pygame.font.SysFont(None, 36)
font_button = pygame.font.SysFont(None, 48)

# Background
background_path = "background2.png"
if os.path.exists(background_path):
    background_img = pygame.image.load(background_path).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
else:
    background_img = None

# Sound effects
hover_sound_path = "hover.wav"
hover_sound = pygame.mixer.Sound(hover_sound_path) if os.path.exists(hover_sound_path) else None
running = True

class Song:
    def __init__(self, name, folder_path, audio_file, chart_file, bpm=185, difficulty="Normal"):
        self.name = name
        self.folder_path = folder_path
        self.audio_file = audio_file
        self.chart_file = chart_file
        self.bpm = bpm
        self.difficulty = difficulty
        self.preview_start = 0  # Could be used for preview playback

def scan_songs():
    """Scan the Songs folder for available songs"""
    songs = []
    songs_dir = "Songs"
    
    if not os.path.exists(songs_dir):
        return songs
    
    for folder_name in os.listdir(songs_dir):
        folder_path = os.path.join(songs_dir, folder_name)
        if os.path.isdir(folder_path):
            # Look for audio file (.mp3, .wav, .ogg)
            audio_file = None
            chart_file = None
            for file in os.listdir(folder_path):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    audio_file = os.path.join(folder_path, file)
                elif not file.endswith(('.mp3', '.wav', '.ogg', '.json', '.txt')) and '.' not in file:
                    # Assume chart file (no extension or specific extensions)
                    chart_file = os.path.join(folder_path, file)
            
            # Check for metadata file
            metadata_path = os.path.join(folder_path, "metadata.json")
            bpm = 185
            difficulty = "Normal"
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        bpm = metadata.get('bpm', 185)
                        difficulty = metadata.get('difficulty', 'Normal')
                except:
                    pass
            
            if audio_file and chart_file:
                song = Song(folder_name, folder_path, audio_file, chart_file, bpm, difficulty)
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

def draw_carousel_card(song, x, y, width, height, scale=1.0, is_center=False, alpha=255):
    """Draw a song card in carousel style with scaling and transparency"""
    # Create a surface for the card with alpha
    card_surf = pygame.Surface((int(width * scale), int(height * scale)), pygame.SRCALPHA)
    
    # Card background with transparency
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
    
    # Song name - adjust font size based on scale
    font_size = int(48 * scale) if is_center else int(36 * scale)
    scaled_font = pygame.font.SysFont(None, max(24, font_size))
    name_color = (*SELECTED_COLOR, alpha) if is_center else (*TEXT_COLOR, alpha)
    
    # Truncate long names
    display_name = song.name
    if len(display_name) > 15:
        display_name = display_name[:12] + "..."
    
    name_surf = scaled_font.render(display_name, True, name_color)
    name_rect = name_surf.get_rect(center=(int(width * scale) // 2, int(30 * scale)))
    card_surf.blit(name_surf, name_rect)
    
    # Song info
    info_font_size = int(28 * scale) if is_center else int(20 * scale)
    info_font = pygame.font.SysFont(None, max(16, info_font_size))
    info_text = f"BPM: {song.bpm}"
    if is_center:
        info_text += f" | {song.difficulty}"
    
    info_surf = info_font.render(info_text, True, (*TEXT_COLOR, alpha))
    info_rect = info_surf.get_rect(center=(int(width * scale) // 2, int(height * scale) - 25))
    card_surf.blit(info_surf, info_rect)
    
    # Position the card surface on screen
    final_rect = card_surf.get_rect(center=(x, y))
    screen.blit(card_surf, final_rect)
    
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
    text_surf = render_glow_text("← Back", font_button, color, BASE_GLOW, glow_strength)
    rect = text_surf.get_rect(topleft=(x, y))
    screen.blit(text_surf, rect)
    return rect

def draw_play_button(x, y, is_hovered=False, enabled=True):
    """Draw the play/start button"""
    if not enabled:
        color = (100, 100, 100)
        glow_color = (50, 50, 50)
    else:
        color = HOVER_COLOR if is_hovered else TEXT_COLOR
        glow_color = BASE_GLOW
    
    glow_strength = 8 if is_hovered and enabled else 4
    text_surf = render_glow_text("♪ PLAY ♪", font_button, color, glow_color, glow_strength)
    rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, rect)
    return rect

def song_selection():
    songs = scan_songs()
    current_index = 0  # Currently focused song in center
    hovered_left_arrow = False
    hovered_right_arrow = False
    hovered_back = False
    hovered_play = False
    time_elapsed = 0
    running = True
    # If no songs found, show message
    if not songs:
        print("No songs found in Songs folder!")
        # Show empty state and return
        while running:
            dt = clock.tick(60) / 1000.0
            screen.fill(BG_COLOR)
            
            no_songs_text = "No songs found! Add songs to the 'Songs' folder."
            no_songs_surf = font_info.render(no_songs_text, True, TEXT_COLOR)
            no_songs_rect = no_songs_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(no_songs_surf, no_songs_rect)
            
            # Back button
            back_rect = draw_back_button(30, HEIGHT - 60, False)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(event.pos):
                    return None
            
            pygame.display.flip()
        return None
    
    while True:
        dt = clock.tick(60) / 1000.0
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
        title_surf = render_glow_text("SELECT SONG", font_title, TEXT_COLOR, glow_intensity, 8)
        title_rect = title_surf.get_rect(center=(WIDTH/2, 80))
        screen.blit(title_surf, title_rect)
        
        # Get mouse position
        mx, my = pygame.mouse.get_pos()
        
        # Reset hover states
        hovered_left_arrow = False
        hovered_right_arrow = False
        hovered_back = False
        hovered_play = False
        
        # Carousel layout parameters
        center_x = WIDTH // 2
        center_y = HEIGHT // 2 - 20
        card_width = 400
        card_height = 180
        side_card_width = 250
        side_card_height = 120
        spacing = 280
        
        # Draw carousel cards
        visible_range = 2  # Show 2 cards on each side of center
        song_rects = []
        
        for i in range(-visible_range, visible_range + 1):
            song_index = (current_index + i) % len(songs)
            song = songs[song_index]
            
            # Calculate position and scale
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
                # Side cards get smaller based on distance from center
                distance = abs(i)
                scale = max(0.6, 1.0 - (distance * 0.2))
                # Set side cards to approximately 50% opacity (128 out of 255)
                alpha = max(80, 120 - (distance * 30))
                width, height = side_card_width, side_card_height
            
            # Only draw if card would be visible
            if x > -width and x < WIDTH + width:
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
        right_arrow_rect = draw_navigation_arrow(right_arrow_x, arrow_y, "right", hovered_right_arrow, right_arrow_enabled)
        
        # Check arrow hovers
        if left_arrow_rect.collidepoint(mx, my) and left_arrow_enabled:
            hovered_left_arrow = True
            draw_navigation_arrow(left_arrow_x, arrow_y, "left", hovered_left_arrow, left_arrow_enabled)
        
        if right_arrow_rect.collidepoint(mx, my) and right_arrow_enabled:
            hovered_right_arrow = True
            draw_navigation_arrow(right_arrow_x, arrow_y, "right", hovered_right_arrow, right_arrow_enabled)
        
        # Current song info panel
        current_song = songs[current_index]
        info_y = HEIGHT - 120
        
        # Semi-transparent background for info panel
        info_panel = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 200))
        screen.blit(info_panel, (0, info_y))
        
        # Song details
        title_text = current_song.name
        title_surf = font_song.render(title_text, True, SELECTED_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH/2, info_y + 20))
        screen.blit(title_surf, title_rect)
        
        details_text = f"BPM: {current_song.bpm} | Difficulty: {current_song.difficulty}"
        details_surf = font_info.render(details_text, True, TEXT_COLOR)
        details_rect = details_surf.get_rect(center=(WIDTH/2, info_y + 45))
        screen.blit(details_surf, details_rect)
        
        path_text = f"Folder: {current_song.folder_path}"
        path_surf = pygame.font.SysFont(None, 24).render(path_text, True, (150, 150, 150))
        path_rect = path_surf.get_rect(center=(WIDTH/2, info_y + 70))
        screen.blit(path_surf, path_rect)
        
        # Control instructions
        instructions = "Use < > arrows or click arrows to navigate | Enter or click PLAY to select | ESC to go back"
        inst_surf = pygame.font.SysFont(None, 28).render(instructions, True, TEXT_COLOR)
        inst_rect = inst_surf.get_rect(center=(WIDTH/2, 120))
        screen.blit(inst_surf, inst_rect)
        
        # Back button
        back_rect = draw_back_button(30, HEIGHT - 60, hovered_back)
        if back_rect.collidepoint(mx, my):
            hovered_back = True
            draw_back_button(30, HEIGHT - 60, hovered_back)
        
        # Play button
        play_rect = draw_play_button(WIDTH - 150, HEIGHT - 40, hovered_play, True)
        if play_rect.collidepoint(mx, my):
            hovered_play = True
            draw_play_button(WIDTH - 150, HEIGHT - 40, hovered_play, True)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            
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
                if event.button == 1:  # Left click
                    # Check back button
                    if back_rect.collidepoint(event.pos):
                        return None
                    
                    # Check play button
                    if play_rect.collidepoint(event.pos):
                        return songs[current_index]
                    
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

def get_selected_song_data():
    """
    Run song selection and return song data in a format compatible with main.py
    Returns a dictionary with song information or None if cancelled
    """
    selected_song = song_selection()
    if selected_song:
        return {
            'name': selected_song.name,
            'audio_path': selected_song.audio_file,
            'chart_path': selected_song.chart_file,
            'bpm': selected_song.bpm,
            'folder_path': selected_song.folder_path
        }
    return None

# For testing purposes - remove this when integrating with main game
if __name__ == "__main__":
    selected_song = song_selection()
    if selected_song:
        print(f"Selected song: {selected_song.name}")
        print(f"Audio file: {selected_song.audio_file}")
        print(f"Chart file: {selected_song.chart_file}")
    else:
        print("No song selected")
    pygame.quit()
    sys.exit()

