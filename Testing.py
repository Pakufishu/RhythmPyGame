import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Scrolling Selection")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Font
font = pygame.font.Font(None, 40)

# List of items
items = [f"Item {i+1}" for i in range(20)]

# Selection variables
selected_index = 0
scroll_offset = 0
item_height = 100  # Height of each item

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y*4

    # Clear screen
    screen.fill(BLACK)

    # Render visible items
    for i, item_text in enumerate(items):
        y_pos = (i * item_height) - scroll_offset + 200
        if -item_height < y_pos < screen_height:  # Check if item is visible
            text_color = BLUE if i == selected_index else WHITE
            text_surface = font.render(item_text, True, text_color)
            screen.blit(text_surface, (50, y_pos))

    selected_index = scroll_offset//100

    pygame.display.flip()
pygame.quit()