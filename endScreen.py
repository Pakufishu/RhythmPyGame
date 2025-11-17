import pygame
import sys
import os

pygame.init()
BASE_WIDTH, BASE_HEIGHT = 1920, 1080

#new one change here naja
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

scale_x = WIDTH / BASE_WIDTH
scale_y = HEIGHT / BASE_HEIGHT
scale = min(scale_x, scale_y)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#Fonts(Change later)
title_font = pygame.font.SysFont("arial", int(70 * scale), bold=True)
score_font = pygame.font.SysFont("arial", int(55 * scale), bold=True)
stat_font = pygame.font.SysFont("arial", int(45 * scale), bold=True)
grade_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(400 * scale))
grade_font_under = pygame.font.Font(os.path.join("fonts", "Platinum_under.ttf"), int(400 * scale))

#Background = using songname.png
bg_image_path = os.path.join("Songs/Mesmerizer", "Mesmerizer_bg.png")
bg_image = pygame.image.load(bg_image_path).convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
bg_opacity = 20
overlay_opacity = 100

song_name = "MESMERIZER"
accuracy = 0.00
grade = "A"
score = 0
max_combo = 0
perfect = 0
great = 0
good = 0
miss = 0

#Rectangle
def draw_rounded_rect(surface, color, rect, radius):
    pygame.draw.rect(surface, color, rect, border_radius=int(radius * scale))

#Trapezoid
def draw_right_trapezoid(surface, color, x, y, w, h, slant):
    p1 = (x, y)
    p2 = (x + w, y)
    p3 = (x + w - slant, y + h)
    p4 = (x, y + h)
    pygame.draw.polygon(surface, color, [p1, p2, p3, p4])

#adjusting number
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
stats_spacing = int(80 * scale)

score_offset_x = int(-145 * scale)
score_offset_y = int(0 * scale)

song_name_x = int(panel_x + 1000 * scale)
song_name_y = int(panel_y - 100 * scale)

accuracy_x = int(panel_x + 55 * scale)
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
                print("Go back to song selection yessir")
            elif retry_rect.collidepoint(mouse_pos):
                print("you sucked so u retry it or you just want better score")

    bg_surface = bg_image.copy()
    bg_surface.set_alpha(bg_opacity)
    screen.blit(bg_surface, (0, 0))

    #bhind overlay
    overlay_surface = pygame.Surface((WIDTH, HEIGHT))
    overlay_surface.set_alpha(overlay_opacity)
    overlay_surface.fill(BLACK)
    screen.blit(overlay_surface, (0, 0))

    draw_rounded_rect(screen, WHITE, pygame.Rect(panel_x, panel_y, panel_width, panel_height), 30)
    draw_right_trapezoid(screen, WHITE, trapezoid_x, trapezoid_y, trapezoid_width, trapezoid_height, trapezoid_slant)

    score_text = score_font.render(f"Score: {score}", True, BLACK)
    text_rect = score_text.get_rect(center=(trapezoid_x + trapezoid_width / 2 - trapezoid_slant / 2 + score_offset_x,
                                            trapezoid_y + trapezoid_height / 2 + score_offset_y))
    screen.blit(score_text, text_rect)

    stats = [f"Perfect {perfect}", f"Great {great}", f"Good {good}", f"Miss {miss}"]
    for i, text in enumerate(stats):
        screen.blit(stat_font.render(text, True, BLACK),
                    (panel_x + int(50 * scale), panel_y - int(65 * scale) + stats_top_margin + i * stats_spacing))

    #max combo
    max_label_text = stat_font.render("Max Combo", True, BLACK)
    label_rect = max_label_text.get_rect(topright=(panel_x + panel_width - int(50 * scale), panel_y + int(50 * scale)))
    screen.blit(max_label_text, label_rect)

    max_value_text = stat_font.render(str(max_combo), True, BLACK)
    value_rect = max_value_text.get_rect(topright=(panel_x + panel_width - int(50 * scale), label_rect.bottom + int(10 * scale)))
    screen.blit(max_value_text, value_rect)

    screen.blit(title_font.render(song_name, True, WHITE), (song_name_x, song_name_y))
    screen.blit(stat_font.render(f"Accuracy: {accuracy}%", True, WHITE), (accuracy_x, accuracy_y))

    grade_text_under = grade_font.render(grade, True, BLACK)
    grade_text_over = grade_font.render(grade, True, WHITE)
    screen.blit(grade_text_under, (grade_x+int(20*scale), grade_y))
    screen.blit(grade_text_over, (grade_x, grade_y))

    pygame.draw.rect(screen, WHITE, continue_rect, border_radius=int(20*scale))
    pygame.draw.rect(screen, WHITE, retry_rect, border_radius=int(20*scale))
    continue_text_surf = stat_font.render("Continue", True, BLACK)
    retry_text_surf = stat_font.render("Retry", True, BLACK)
    screen.blit(continue_text_surf, continue_text_surf.get_rect(center=continue_rect.center))
    screen.blit(retry_text_surf, retry_text_surf.get_rect(center=retry_rect.center))

    pygame.display.update()
    clock.tick(60)