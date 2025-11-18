import pygame

def gradientRect(window, bottom_colour, top_colour, target_rect):
    colour_rect = pygame.Surface((2, 2),pygame.SRCALPHA)
    pygame.draw.line(colour_rect, bottom_colour, (0, 1), (1, 1))
    pygame.draw.line(colour_rect, top_colour, (0, 0), (1, 0))
    colour_surf = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))
    colour_surf = colour_surf.convert_alpha()
    window.blit(colour_surf, target_rect)

def blur_surface(surface, passes=3, scale_factor=0.25):
    if scale_factor <= 0 or scale_factor >= 1:
        return surface.copy()
    result = surface.copy()
    for _ in range(passes):
        w = max(2, int(result.get_width() * scale_factor))
        h = max(2, int(result.get_height() * scale_factor))
        try:
            small = pygame.transform.smoothscale(result, (w, h))
            result = pygame.transform.smoothscale(small, surface.get_size())
        except Exception:
            return surface.copy()
    return result

def draw_double_text(surface, text, font_top, font_bottom, color_top, color_bottom, pos, offset=(4, 4), center=True):
    surf_bottom = font_bottom.render(text, True, color_bottom)
    rect_bottom = surf_bottom.get_rect(center=pos if center else pos)
    rect_bottom.move_ip(offset)
    surface.blit(surf_bottom, rect_bottom)
    surf_top = font_top.render(text, True, color_top)
    rect_top = surf_top.get_rect(center=pos if center else pos)
    surface.blit(surf_top, rect_top)
    return rect_top

def draw_trapezoid(surface, color, x, y, w, h, slant):
    p1 = (x, y)
    p2 = (x + w, y)
    p3 = (x + w - slant, y + h)
    p4 = (x, y + h)
    pygame.draw.polygon(surface, color, [p1, p2, p3, p4])

def draw_rounded_rect(surface, color, rect, radius, scale):
    pygame.draw.rect(surface, color, rect, border_radius=int(radius * scale))
