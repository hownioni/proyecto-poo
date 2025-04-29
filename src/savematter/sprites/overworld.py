from __future__ import annotations

from typing import TYPE_CHECKING

from savematter.sprites.sprites import Sprite, StateAnimatedSprite
from savematter.utils.settings import TILE_SIZE, Z_LAYERS, Vector2

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.sprite import Group

    from savematter.game.data import Data


class Node(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface,
        level: int,
        data: Data,
        dirs: dict[str, str],
        *groups: Group,
    ) -> None:
        super().__init__(pos, surf, *groups, z=Z_LAYERS["path"])
        if self.rect is None or self.image is None:
            raise TypeError("Sprite rect or image are empty")

        self.rect.center = (pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2)

        self.level = level
        self.data = data
        self.dirs = dirs
        self.grid_pos = (int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE))

    def can_move(self, dir: str) -> bool:
        return (
            True
            if dir in list(self.dirs.keys())
            and int(self.dirs[dir][0]) <= self.data.unlocked_level
            else False
        )


class PlayerIcon(StateAnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        default_state: str,
        frames: dict[str, list[Surface]],
        *groups: Group,
    ) -> None:
        super().__init__(pos, default_state, frames, *groups, z=Z_LAYERS["main"])
        if self.rect is None or self.image is None:
            raise TypeError("Sprite rect or image are empty")

        self.icon = True
        self.path = None
        self.direction = Vector2()
        self.speed = 400

        # Rect
        self.rect.center = pos

    def get_anim_state(self) -> None:
        self.state = "idle"
        if self.direction == Vector2(1, 0):
            self.state = "right"
        if self.direction == Vector2(-1, 0):
            self.state = "left"
        if self.direction == Vector2(0, 1):
            self.state = "down"
        if self.direction == Vector2(0, -1):
            self.state = "up"

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        self.image = self.frames[self.state][
            int(self.frame_index % len(self.frames[self.state]))
        ]

    def start_moving(self, path: list[tuple[float, float]]) -> None:
        if self.rect is None:
            raise TypeError("Player icon rect is empty")

        self.rect.center = path[0]
        self.path = path[1:]
        self.find_dir()

    def find_dir(self) -> None:
        if self.rect is None:
            raise TypeError("Player icon rect is empty")

        if self.path:
            if self.rect.centerx == self.path[0][0]:  # Vertical enabled
                self.direction = Vector2(
                    0, 1 if self.path[0][1] > self.rect.centery else -1
                )
            else:  # Horizontal enabled
                self.direction = Vector2(
                    1 if self.path[0][0] > self.rect.centerx else -1, 0
                )
        else:
            self.direction = Vector2()

    def point_collision(self) -> None:
        if self.rect is None:
            raise TypeError("Player icon rect is empty")
        if self.path is None:
            raise TypeError("Path is empty")

        # Vertical
        if (
            self.direction.y == 1
            and self.rect.centery >= self.path[0][1]
            or self.direction.y == -1
            and self.rect.centery <= self.path[0][1]
        ):
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_dir()

        # Horizontal
        if (
            self.direction.x == 1
            and self.rect.centerx >= self.path[0][0]
            or self.direction.x == -1
            and self.rect.centerx <= self.path[0][0]
        ):
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_dir()

    def update(self, dt: float) -> None:
        if self.rect is None:
            raise TypeError("Player icon rect is empty")

        if self.path:
            self.point_collision()
            self.rect.center += self.direction * self.speed * dt
        super().update(dt)


class Path(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface,
        level: int,
        *groups: Group,
    ) -> None:
        super().__init__(pos, surf, *groups, z=Z_LAYERS["path"])
        self.level = level
