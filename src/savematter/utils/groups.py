from __future__ import annotations

from random import choice, randint

import pygame

from savematter.sprites.objects import Cloud
from savematter.sprites.sprites import Sprite
from savematter.utils.settings import (
    TILE_SIZE,
    WINDOW_H,
    WINDOW_W,
    Z_LAYERS,
)
from savematter.utils.timer import Timer
from savematter.utils.typing import TYPE_CHECKING, Vector2, cast

if TYPE_CHECKING:
    from pygame import Surface

    from savematter.game.data import Data


class WorldSprites(pygame.sprite.Group):
    def __init__(self, data: Data) -> None:
        super().__init__()
        self.screen: Surface | None = pygame.display.get_surface()
        self.data = data
        self.offset = Vector2()

    def draw(self, target_pos: tuple[float, float], dt: float) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        self.offset.x = -(target_pos[0] - WINDOW_W / 2)
        self.offset.y = -(target_pos[1] - WINDOW_H / 2)

        # Background
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.rect is None or sprite.image is None:
                raise TypeError("Sprite rect or image are empty")

            if sprite.z < Z_LAYERS["main"]:
                if (
                    sprite.z == Z_LAYERS["path"]
                    and sprite.level > self.data.unlocked_level
                ):
                    pass
                else:
                    offset_pos = sprite.rect.topleft + self.offset
                    self.screen.blit(sprite.image, offset_pos)

        # Main
        for sprite in sorted(self, key=lambda sprite: sprite.rect.centery):
            if sprite.rect is None or sprite.image is None:
                raise TypeError("Sprite rect or image are empty")

            if sprite.z == Z_LAYERS["main"]:
                icon_offset = Vector2(0, -28) if hasattr(sprite, "icon") else Vector2()
                offset_pos = sprite.rect.topleft + self.offset + icon_offset
                self.screen.blit(sprite.image, offset_pos)


class AllSprites(pygame.sprite.Group):
    def __init__(
        self,
        level_width: int,
        level_height: int,
        clouds: dict[str, Surface | list[Surface]],
        bg_tile: Surface | None = None,
        top_limit: int = 0,
        horizon_line: int = 0,
    ) -> None:
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = Vector2(0, 0)
        self.level_pwidth, self.level_pheight = (
            level_width * TILE_SIZE,
            level_height * TILE_SIZE,
        )
        self.borders = {
            "left": 0,
            "right": -self.level_pwidth + WINDOW_W,
            "top": top_limit,
            "bottom": -self.level_pheight + WINDOW_H,
        }
        self.draw_sky = not bg_tile
        self.horizon_line = horizon_line

        if bg_tile:
            for col in range(level_width):
                for row in range(-int(top_limit / TILE_SIZE) - 1, level_height):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    Sprite((x, y), bg_tile, self, z=-1)
        else:  # Sky
            self.large_cloud = cast("Surface", clouds["large"])
            self.small_clouds = cast("list[Surface]", clouds["small"])
            self.cloud_direction = -1

            # Large cloud
            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.level_pwidth / self.large_cloud.width) + 2

            # Small clouds
            self.cloud_timer = Timer(2500, self.create_cloud, repeat=True)
            self.cloud_timer.activate()
            for cloud in range(20):
                pos = (
                    randint(0, self.level_pwidth),
                    randint(self.borders["top"], self.horizon_line),
                )
                surf = choice(self.small_clouds)
                Cloud(pos, surf, self)

    def constrain_camera(self):
        self.offset.x = (
            self.offset.x
            if self.offset.x < self.borders["left"]
            else self.borders["left"]
        )
        self.offset.x = (
            self.offset.x
            if self.offset.x > self.borders["right"]
            else self.borders["right"]
        )
        self.offset.y = (
            self.offset.y
            if self.offset.y < self.borders["top"]
            else self.borders["top"]
        )
        self.offset.y = (
            self.offset.y
            if self.offset.y > self.borders["bottom"]
            else self.borders["bottom"]
        )

    def create_cloud(self):
        pos = (
            randint(self.level_pwidth + 500, self.level_pwidth + 600),
            randint(self.borders["top"], self.horizon_line),
        )
        surf = choice(self.small_clouds)
        Cloud(pos, surf, self)

    def draw(self, target_pos: tuple[float, float], dt: float) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        self.offset.x = -(target_pos[0] - WINDOW_W / 2)
        self.offset.y = -(target_pos[1] - WINDOW_H / 2)
        self.constrain_camera()

        # Sky
        if self.draw_sky:
            self.cloud_timer.update()
            self.screen.fill("#ddc6a1")
            horizon_pos = self.horizon_line + self.offset.y

            # Horizon line
            pygame.draw.line(
                self.screen,
                "#f5f1de",
                (0, horizon_pos),
                (WINDOW_W, horizon_pos),
                4,
            )

            sea_rect = pygame.FRect(0, horizon_pos, WINDOW_W, WINDOW_H - horizon_pos)
            pygame.draw.rect(self.screen, "#92a9ce", sea_rect)

            # Large cloud
            self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * dt
            self.large_cloud_x = (
                0
                if self.large_cloud_x <= -self.large_cloud.width
                else self.large_cloud_x
            )
            for cloud in range(self.large_cloud_tiles):
                left = (
                    self.large_cloud_x + self.large_cloud.width * cloud + self.offset.x
                )
                top = self.horizon_line - self.large_cloud.height + self.offset.y
                self.screen.blit(self.large_cloud, (left, top))

        sprite: Sprite
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.rect is None or sprite.image is None:
                raise TypeError("Sprite rect or image are empty")

            offset_pos = sprite.rect.topleft + self.offset
            self.screen.blit(sprite.image, offset_pos)
