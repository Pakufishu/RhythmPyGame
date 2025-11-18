import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Smooth Looping Scrolling Selection")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Font
font = pygame.font.Font(None, 40)

# List of items
items = [f"Item {i + 1}" for i in range(2)]

# Selection variables
selected_index = 0
scroll_offset = 0
item_height = 100  # Height of each item
visible_items = screen_height // item_height + 2  # Number of items visible on screen

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y * 20  # Increased scroll speed for smoother feel

    # Handle keyboard input for continuous scrolling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        scroll_offset -= 200 * dt  # Scroll up
    if keys[pygame.K_DOWN]:
        scroll_offset += 200 * dt  # Scroll down

    # Apply smooth looping to scroll_offset
    total_height = len(items) * item_height
    scroll_offset = scroll_offset % total_height  # This creates the looping effect

    # Calculate selected index
    selected_index = int(scroll_offset // item_height) % len(items)

    # Clear screen
    screen.fill(BLACK)

    # Render visible items with smooth looping
    for i in range(-1, visible_items + 1):
        # Calculate the actual item index with looping
        list_index = (int(scroll_offset // item_height) + i) % len(items)

        # Calculate y position with smooth scrolling
        base_y = i * item_height - (scroll_offset % item_height)
        y_pos = base_y + 200  # Center the list vertically

        # Only render if visible on screen
        if -item_height < y_pos < screen_height:
            # Calculate alpha for fade effect at edges (optional)
            distance_from_center = abs(y_pos - screen_height // 2)
            max_distance = screen_height // 2
            alpha = max(0, 255 - (distance_from_center / max_distance) * 128)

            text_color = BLUE if list_index == selected_index else WHITE
            text_surface = font.render(items[list_index], True, text_color)

            # Optional: Apply fade effect
            if alpha < 255:
                fade_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                fade_surface.fill((255, 255, 255, alpha))
                text_surface.blit(fade_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(text_surface, (screen_width - 100 - text_surface.get_width() // 2, y_pos))

    pygame.display.flip()

pygame.quit()