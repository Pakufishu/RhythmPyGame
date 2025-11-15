import pygame

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pulsing Effect")

white = (255, 255, 255)
red = (255, 0, 0)

# Initial square properties
square_size = 50
max_size = 100
min_size = 80
pulse_speed = 2  # How fast the size changes
expanding = True

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update pulsing size
    if expanding:
        square_size += pulse_speed**2
        if square_size >= max_size:
            expanding = False
    else:
        square_size -= pulse_speed**2
        if square_size <= min_size:
            expanding = True

    # Drawing
    screen.fill(white)  # Clear the screen
    pygame.draw.rect(screen, red, (screen_width // 2 - square_size // 2,
                                   screen_height // 2 - square_size // 2,
                                   square_size, square_size))
    pygame.display.flip()  # Update the display

    clock.tick(60)  # Limit frame rate

pygame.quit()