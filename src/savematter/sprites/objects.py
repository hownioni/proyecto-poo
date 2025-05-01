from __future__ import annotations

from math import cos, radians, sin
from random import randint

import pygame

from savematter.sprites.sprites import AnimatedSprite, Sprite
from savematter.utils.settings import TILE_SIZE, Z_LAYERS
from savematter.utils.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.sprite import Group


class Spike(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface,
        radius: float,
        speed: float,
        start_angle: float,
        end_angle: float,
        *groups: Group,
        z: int = Z_LAYERS["main"],
    ) -> None:
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        super().__init__(self.calc_pos(), surf, *groups, z=z)

    def calc_pos(self) -> tuple[float, float]:
        # Trig
        y = self.center[1] + self.radius * sin(radians(self.angle))
        x = self.center[0] + self.radius * cos(radians(self.angle))
        return x, y

    def update(self, dt: float) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle < self.start_angle:
                self.direction = 1
        self.rect.center = self.calc_pos()


class FloorSpike(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[Surface],
        inverted: bool,
        *groups: Group,
    ) -> None:
        super().__init__(pos, frames, *groups)
        if self.rect is None:
            raise TypeError("Rect is empty")

        self.hitbox = self.rect.inflate(0, -32)
        self.hitbox.topleft = pos

        if inverted:
            self.frames = [
                pygame.transform.flip(frame, False, True) for frame in frames
            ]
        else:
            self.hitbox.move_ip(0, 32)

        self.old_rect = self.hitbox.copy()


class Cloud(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface = pygame.Surface((TILE_SIZE, TILE_SIZE)),
        *groups: Group,
    ) -> None:
        super().__init__(pos, surf, *groups, z=Z_LAYERS["clouds"])

        self.speed = randint(50, 120)
        self.direction = -1

    def update(self, dt: float) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.x += self.direction * self.speed * dt

        if self.rect.right <= 0:
            self.kill()
