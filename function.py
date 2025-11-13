import pygame

def gradientRect(window, bottom_colour, top_colour, target_rect):
    colour_rect = pygame.Surface((2, 2),pygame.SRCALPHA)
    pygame.draw.line(colour_rect, bottom_colour, (0, 1), (1, 1))
    pygame.draw.line(colour_rect, top_colour, (0, 0), (1, 0))
    colour_surf = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))
    colour_surf = colour_surf.convert_alpha()
    window.blit(colour_surf, target_rect)