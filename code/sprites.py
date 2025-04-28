from __future__ import annotations

from abc import ABC, abstractmethod

from settings import ANIM_SPEED, TILE_SIZE, TYPE_CHECKING, Z_LAYERS, Vector2, pygame

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.sprite import Group

    from g_data import Data


class Sprite(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface = pygame.Surface((TILE_SIZE, TILE_SIZE)),
        *groups: Group,
        z: int = Z_LAYERS["main"],
    ) -> None:
        super().__init__(*groups)
        self.image = surf

        # Rects
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z


class AnimatedSprite(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[Surface],
        *groups: Group,
        z: int = Z_LAYERS["main"],
        anim_speed: float = ANIM_SPEED,
    ) -> None:
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], *groups, z=z)
        self.anim_speed = anim_speed

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt: float) -> None:
        self.animate(dt)


class StateAnimatedSprite(AnimatedSprite, ABC):
    def __init__(
        self,
        pos: tuple[float, float],
        default_state: str,
        frames: dict[str, list[Surface]],
        *groups: Group,
        z: int = Z_LAYERS["main"],
        anim_speed: float = ANIM_SPEED,
    ) -> None:
        self.state = default_state
        super().__init__(pos, frames[self.state], *groups, z=z, anim_speed=anim_speed)
        self.frames, self.frame_index = frames, 0

    @abstractmethod
    def get_anim_state(self) -> None:
        pass

    @abstractmethod
    def animate(self, dt: float) -> None:
        pass

    def update(self, dt: float) -> None:
        self.get_anim_state()
        super().update(dt)


class Item(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[Surface],
        item_type: str,
        data: Data,
        *groups: Group,
    ) -> None:
        super().__init__(pos, frames, *groups)
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.center = pos
        self.item_type = item_type
        self.data = data

    def activate(self) -> None:
        if self.item_type == "silver":
            self.data.coins += 1
        if self.item_type == "gold":
            self.data.coins += 5
        if self.item_type == "diamond":
            self.data.coins += 20
        if self.item_type == "skull":
            self.data.coins += 50
        if self.item_type == "potion":
            self.data.health += 1


class ParticleEffectSprite(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[Surface],
        *groups: Group,
    ) -> None:
        super().__init__(pos, frames, *groups)
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.center = pos
        self.z = Z_LAYERS["fg"]

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


class MovingSprite(AnimatedSprite):
    def __init__(
        self,
        frames: list[Surface],
        start_pos: tuple[float, float],
        end_pos: tuple[float, float],
        move_dir: str,
        speed: int,
        *groups: Group,
        z: int = Z_LAYERS["main"],
        flip: bool = False,
    ) -> None:
        super().__init__(start_pos, frames, *groups)
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        if move_dir == "x":
            self.rect.midleft = start_pos
        elif move_dir == "y":
            self.rect.midtop = start_pos
        else:
            raise ValueError("move_dir must be either x or y")

        self.start_pos = start_pos
        self.end_pos = end_pos

        # Movement
        self.moving = True
        self.speed = speed
        self.direction = Vector2(1, 0) if move_dir == "x" else Vector2(0, 1)
        self.move_dir = move_dir

        self.flip = flip
        self.reverse = {"x": False, "y": False}

    def check_border(self) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        if self.move_dir == "x":
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            self.reverse["x"] = True if self.direction.x < 0 else False
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            self.reverse["y"] = True if self.direction.y > 0 else False

    def update(self, dt: float) -> None:
        if self.rect is None or self.image is None:
            raise TypeError("Sprite rect or image are empty")

        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()
        super().update(dt)
        if self.flip:
            self.image = pygame.transform.flip(
                self.image, self.reverse["x"], self.reverse["y"]
            )
