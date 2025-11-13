import sys
import os
import math
from variables import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Rhythm Game Menu")

TEXT_COLOR = (220, 240, 255)   # ice white-blue
HOVER_COLOR = (255, 255, 0)    # yellow for hover
BASE_GLOW = (0, 200, 255)      # neon cyan
BG_COLOR = (10, 10, 20)        # deep navy

font_title = pygame.font.SysFont(None, 100)  # Title size
font_button = pygame.font.SysFont(None, 60)  # Button sized

background_path = "background2.png"
if os.path.exists(background_path):
    background_img = pygame.image.load(background_path).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
else:
    background_img = None

hover_sound_path = "hover.wav"
hover_sound = pygame.mixer.Sound(hover_sound_path) if os.path.exists(hover_sound_path) else None

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

running = True
buttons = ["Play", "Options", "Credits", "Back to desktop"]


def main_menu():
    global running
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
                            return

                        if buttons[i] == "Back to desktop":
                            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()