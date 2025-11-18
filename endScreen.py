import pygame
import sys
import os

pygame.init()


BASE_WIDTH, BASE_HEIGHT = 1920, 1080

#new one change here naja
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


scale_x = WIDTH / BASE_WIDTH
scale_y = HEIGHT / BASE_HEIGHT
scale = min(scale_x, scale_y)

#Colors
PURPLE = (102, 51, 153)
RED = (255,0,0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#Fonts(Change later)
title_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(100 * scale))
score_font = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(55 * scale))
stat_font = pygame.font.Font(os.path.join("fonts", "Designer.otf"), int(30 * scale))
grade_font = pygame.font.Font(os.path.join("fonts", "Platinum_over.ttf"), int(400 * scale))
grade_font_under = pygame.font.Font(os.path.join("fonts", "Platinum_under.ttf"), int(400 * scale))

#Background = using songname.png
bg_image_path = os.path.join("background", "MESMERIZER.png")
bg_image = pygame.image.load(bg_image_path).convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
bg_opacity = 20
overlay_opacity = 100

difficulty = 'Expert'
song_name = "MESMERIZER"
accuracy = 69.67
grade = "A"
score = 6967
max_combo = 6967
perfect = 6967
great = 6967
good = 6967
miss = 6967

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
                print("Go back to song selection yessir")
            elif retry_rect.collidepoint(mouse_pos):
                print("you sucked so u retry it or you just want better score")

    bg_surface = bg_image.copy()
    bg_surface.set_alpha(bg_opacity)
    screen.blit(bg_surface, (0, 0))

    #difficulty
    difficulty_render = stat_font.render(difficulty, True, WHITE)
    difficulty_text_rect = difficulty_render.get_rect()
    diff_rect_width = panel_width - (diff_hori_freaking_margin * 2)
    diff_rect_height = difficulty_text_rect.height + diff_vert_padding * 2
    diff_x = panel_x + diff_hori_freaking_margin
    diff_y = panel_y + panel_height - diff_rect_height - diff_vert_padding

    difficulty_rect_approx = pygame.Rect(diff_x, diff_y, diff_rect_width, diff_rect_height)

    #bhind overlay
    overlay_surface = pygame.Surface((WIDTH, HEIGHT))
    overlay_surface.set_alpha(overlay_opacity)
    overlay_surface.fill(BLACK)
    screen.blit(overlay_surface, (0, 0))

    draw_rounded_rect(screen, WHITE, pygame.Rect(panel_x, panel_y, panel_width, panel_height), 30)
    draw_right_trapezoid(screen, WHITE, trapezoid_x, trapezoid_y, trapezoid_width, trapezoid_height, trapezoid_slant)
    draw_rounded_rect(screen, RED, difficulty_rect_approx, 15) #color change here

    text_blit_x = difficulty_rect_approx.x + diff_hori_freaking_margin #difficulty one
    text_blit_y = difficulty_rect_approx.y + diff_vert_padding

    score_text = score_font.render(f"Score: {score}", True, BLACK) #ts pmo it hella hard :pray: pls no more trapezoid
    text_rect = score_text.get_rect(midleft=(
    trapezoid_x + trapezoid_width / 2 - trapezoid_slant / 2 + score_offset_x,
    trapezoid_y + trapezoid_height / 2 + score_offset_y
    ))
    screen.blit(score_text, text_rect)

    stats = [("Perfect", perfect), ("Great", great), ("Good", good), ("Miss", miss)]
    label_x = panel_x + int(42 * scale)
    value_x = panel_x + int(250 * scale)
    for i, (label, value) in enumerate(stats):
        y = panel_y - int(65 * scale) + stats_top_margin + i * stats_spacing
        screen.blit(stat_font.render(f"{label}", True, BLACK), (label_x, y)) #stat(changing perfect, great, miss)
        screen.blit(stat_font.render(str(value), True, BLACK), (value_x, y)) # stat(changing number)

    #max combo
    max_label_text = stat_font.render("Max Combo", True, BLACK)
    label_rect = max_label_text.get_rect(topright=(panel_x + panel_width - int(50 * scale), panel_y + int(57 * scale)))
    screen.blit(max_label_text, label_rect)

    max_value_text = stat_font.render(str(max_combo), True, BLACK)
    value_rect = max_value_text.get_rect(topright=(panel_x + panel_width - int(50 * scale), label_rect.bottom + int(10 * scale)))
    screen.blit(max_value_text, value_rect)

    #song + difficulty + acc
    screen.blit(title_font.render(song_name, True, BLACK), (song_name_x, song_name_y))
    screen.blit(title_font.render(song_name, True, WHITE), (song_name_x, song_name_y))
    screen.blit(stat_font.render(f"Accuracy: {accuracy}%", True, WHITE), (accuracy_x, accuracy_y))
    screen.blit(difficulty_render, (text_blit_x, text_blit_y))

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