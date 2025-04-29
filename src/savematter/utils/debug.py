from __future__ import annotations

from typing import Any

import pygame

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info: Any, pos: tuple[float, float] = (10, 10)) -> None:
    display_surf = pygame.display.get_surface()
    if display_surf is None:
        raise TypeError("Display surface is empty")

    debug_surf = font.render(str(info), True, "White")
    debug_rect = debug_surf.get_rect(topleft=pos)
    pygame.draw.rect(display_surf, "Black", debug_rect)
    display_surf.blit(debug_surf, debug_rect)
