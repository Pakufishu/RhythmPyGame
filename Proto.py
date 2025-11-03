import pygame as p
import sys
import random
import time

p.init()

WIDTH, HEIGHT = 1920, 1080
screen = p.display.set_mode((WIDTH, HEIGHT), p.FULLSCREEN)
clock = p.time.Clock()
font = p.font.SysFont(None, 48)
combo = 0
max_combo = 0
LANES = 4
LANE_WIDTH = WIDTH // LANES
KEYS = [p.K_d, p.K_f, p.K_j, p.K_k]
KEY_NAMES = ['D', 'F', 'J', 'K']
PLAY_AREA_WIDTH = 800  # or any width you like
LANE_WIDTH = PLAY_AREA_WIDTH // LANES
PLAY_AREA_X = (WIDTH - PLAY_AREA_WIDTH) // 2  # left offset for centering
hit_line = HEIGHT - 400
center_x = WIDTH // 2 - 200
center_y = hit_line // 2 + 50
note_speed = 8  # Default note speed
# Each note: [lane, y, speed]
notes = []
score = 0
judgment = ""
judgment_time = 0
running = True
pending_miss_sounds = []
MISS_SOUND_DELAY = 0.5  # seconds
p.mixer.init()
sound_perfect = p.mixer.Sound("sfx/perfect.wav")
sound_great = p.mixer.Sound("sfx/perfect.wav")
sound_good = p.mixer.Sound("sfx/perfect.wav")
sound_bad = p.mixer.Sound("sfx/perfect.wav")
sound_miss = p.mixer.Sound("sfx/miss.wav")

sound_perfect.set_volume(1.0)
sound_great.set_volume(0.3)
sound_bad.set_volume(0.1)
sound_miss.set_volume(1.0)

def spawn_note():
    lane = random.randint(0, LANES - 1)
    y = -50
    speed = note_speed
    # Calculate when the note will reach the hit line
    frames_to_hit = (hit_line - y) / speed
    hit_time = time.time() + frames_to_hit / 144  # 144 is your FPS
    notes.append([lane, y, speed, hit_time])

def settings_menu():
    global note_speed,center_x,center_y
    settings_running = True
    while settings_running:
        screen.fill((20, 20, 40))
        title = font.render("Settings", True, (255, 255, 0))
        prompt = font.render("Back", True, (255, 255, 255))
        speed_label = font.render(f"Note Speed: {note_speed}", True, (0, 255, 255))
        left_btn = font.render("<", True, (180, 180, 180))
        right_btn = font.render(">", True, (180, 180, 180))

        # Button rects
        back_rect = prompt.get_rect(center=(center_x, center_y + 120))
        left_rect = left_btn.get_rect(center=(center_x - 80, center_y + 20))
        right_rect = right_btn.get_rect(center=(center_x + 80, center_y + 20))
        speed_rect = speed_label.get_rect(center=(center_x, center_y + 20))

        screen.blit(title, (center_x - title.get_width() // 2, center_y - 120))
        screen.blit(speed_label, speed_rect)
        screen.blit(left_btn, left_rect)
        screen.blit(right_btn, right_rect)
        screen.blit(prompt, back_rect)

        p.display.flip()
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if left_rect.collidepoint(mx, my):
                    note_speed = max(1, note_speed - 1)
                elif right_rect.collidepoint(mx, my):
                    note_speed = min(20, note_speed + 1)
                elif back_rect.collidepoint(mx, my):
8                    settings_running = False
            if event.type == p.KEYDOWN and event.key == p.K_ESCAPE:
                settings_running = False

def pause_menu():
    paused = True
    selected = 0
    options = ["Continue", "Retry", "Exit to Main Menu"]
    global center_x,center_y
    while paused:
        screen.fill((30, 30, 60))
        title = font.render("Paused", True, (255, 255, 0))
        screen.blit(title, (center_x - title.get_width() // 2, center_y - 120))
        for i, opt in enumerate(options):
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            label = font.render(opt, True, color)
            screen.blit(label, (center_x - label.get_width() // 2, center_y - 40 + i * 60))
        p.display.flip()
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.KEYDOWN:
                if event.key == p.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == p.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == p.K_RETURN or event.key == p.K_SPACE:
                    if options[selected] == "Continue":
                        # 3 second countdown
                        for sec in range(3, 0, -1):
                            screen.fill((30, 30, 60))
                            msg = font.render(f"Resuming in {sec}", True, (0, 255, 255))
                            screen.blit(msg, (center_x - msg.get_width() // 2, center_y))
                            p.display.flip()
                            p.time.delay(1000)
                        paused = False
                        return "continue"
                    elif options[selected] == "Retry":
                        paused = False
                        return "retry"
                    elif options[selected] == "Exit to Main Menu":
                        paused = False
                        return "menu"

def main_menu():
    menu_running = True
    global center_x,center_y
    while menu_running:
        screen.fill((20, 20, 20))

        title = font.render("4K Rhythm Game", True, (0, 255, 255))
        start_btn = font.render("Start", True, (255, 255, 255))
        settings_btn = font.render("Settings", True, (255, 255, 0))
        quit_btn = font.render("Quit", True, (255, 80, 80))

        start_rect = start_btn.get_rect(center=(center_x, center_y))
        settings_rect = settings_btn.get_rect(center=(center_x, center_y + 80))
        quit_rect = quit_btn.get_rect(center=(center_x, center_y + 160))

        screen.blit(title, (center_x - title.get_width() // 2, center_y - 100))
        screen.blit(start_btn, start_rect)
        screen.blit(settings_btn, settings_rect)
        screen.blit(quit_btn, quit_rect)
        p.display.flip()
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if start_rect.collidepoint(mx, my):
                    menu_running = False
                elif settings_rect.collidepoint(mx, my):
                    settings_menu()
                elif quit_rect.collidepoint(mx, my):
                    p.quit()
                    sys.exit()

main_menu()
# Start with a note in each lane
notes.clear()
for i in range(LANES):
    y = -50 * (i+1)
    speed = random.randint(4, 8)
    frames_to_hit = (hit_line - y) / speed
    hit_time = time.time() + frames_to_hit / 144
    notes.append([i, y, speed, hit_time])

while running:
    screen.fill((30, 30, 30))
    now = time.time()
    print(notes)
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False
        if event.type == p.KEYDOWN:
            if event.key == p.K_ESCAPE:
                action = pause_menu()
                if action == "retry":
                    notes.clear()
                    score = 0
                    for i in range(LANES):
                        y = -50 * (i+1)
                        speed = random.randint(4, 8)
                        frames_to_hit = (hit_line - y) / speed
                        hit_time = time.time() + frames_to_hit / 144
                        notes.append([i, y, speed, hit_time])
                elif action == "menu":
                    main_menu()
                    notes.clear()
                    score = 0
                    for i in range(LANES):
                        y = -50 * (i+1)
                        speed = random.randint(4, 8)
                        frames_to_hit = (hit_line - y) / speed
                        hit_time = time.time() + frames_to_hit / 144
                        notes.append([i, y, speed, hit_time])
            for idx, key in enumerate(KEYS):
                if event.key == key:
                    for note in notes:
                        if note[0] == idx:
                            timing_error = abs(now - note[3])
                            if timing_error <= 0.255:
                                if timing_error <= 0.07:
                                    judgment = "Perfect"
                                    score += 300
                                    sound_perfect.play()
                                    combo += 1
                                elif timing_error <= 0.105:
                                    judgment = "Great"
                                    score += 200
                                    sound_great.play()
                                    combo += 1
                                elif timing_error <= 0.140:
                                    judgment = "Good"
                                    score += 100
                                    sound_good.play()
                                    combo += 1
                                elif timing_error <= 0.155:
                                    judgment = "Bad"
                                    score += 50
                                    sound_bad.play()
                                    combo += 1
                                else:
                                    judgment = "Miss"
                                    judgment_time = now
                                    pending_miss_sounds.append(time.time())
                                    if combo > max_combo:
                                        max_combo = combo
                                    combo = 0
                                judgment_time = now
                                notes.remove(note)
                                spawn_note()
                                break
    for t in pending_miss_sounds[:]:
        if now - t >= MISS_SOUND_DELAY:
            sound_miss.play()
            pending_miss_sounds.remove(t)


    # Draw hit line
    p.draw.line(screen, (0, 255, 0), (PLAY_AREA_X, hit_line), (PLAY_AREA_X + PLAY_AREA_WIDTH, hit_line), 4)
    # Draw lanes
    for i in range(1, LANES):
        p.draw.line(screen, (80, 80, 80), (PLAY_AREA_X + i * LANE_WIDTH, 0), (PLAY_AREA_X + i * LANE_WIDTH, HEIGHT), 2)    # Draw notes
    for note in notes:
        x = PLAY_AREA_X + note[0] * LANE_WIDTH + LANE_WIDTH // 2
        p.draw.circle(screen, (255, 0, 0), (x, int(note[1])), 30)
        note[1] += note[2]
    # Remove notes that missed and spawn new ones
    for note in notes[:]:
        if note[1] > HEIGHT + 30:
            judgment = "Miss"
            judgment_time = now
            pending_miss_sounds.append(time.time())
            if combo > max_combo:
                max_combo = combo
            combo = 0
            notes.remove(note)
            spawn_note()

    # Draw score just above the play area
    score_img = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_img, (20, 20))
    # Draw judgment
    if judgment and now - judgment_time < 1.0:
        color = {
            "Perfect": (255, 255, 0),
            "Great": (0, 255, 255),
            "Good": (0, 200, 0),
            "Bad": (255, 128, 0),
            "Miss": (255, 0, 0)
        }[judgment]
        judge_img = font.render(judgment, True, color)
        screen.blit(judge_img, (WIDTH // 2 - judge_img.get_width() // 2, HEIGHT // 2 - 200))
    # Draw combo
    combo_img = font.render(f"Combo: {combo}", True, (255, 255, 0))
    screen.blit(combo_img, (20, 80))
    # Draw max combo
    max_combo_img = font.render(f"Max Combo: {max_combo}", True, (255, 128, 0))
    screen.blit(max_combo_img, (20, 140))
    p.display.flip()
    clock.tick(144) #FPS

p.quit()
sys.exit()