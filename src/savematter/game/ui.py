from __future__ import annotations

import pygame

from savematter.sprites.sprites import AnimatedSprite
from savematter.utils.settings import ZLayers
from savematter.utils.timer import Timer
from savematter.utils.typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font

    from savematter.sprites.sprites import Sprite
    from savematter.utils.typing import AnimationDict, FrameList


class UI:
    def __init__(
        self,
        fonts: dict[str, Font],
        frames: dict[str, Surface | FrameList | dict[str, Surface] | AnimationDict],
    ) -> None:
        self.screen = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.fonts = fonts

        # Health / Hearts
        self.heart_frames = cast("FrameList", frames["heart"])
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 5

        # Coins
        self.coin_surf = cast("Surface", frames["coin"])
        self.coin_timer = Timer(1000)
        self.coin_amount = 0

    # Hearts
    def create_hearts(self, amount: int) -> None:
        sprite: Sprite
        for sprite in self.sprites:
            sprite.kill()
        for heart in range(amount):
            x = 10 + heart * (self.heart_surf_width + self.heart_padding)
            y = 10
            Heart((x, y), self.heart_frames, self.sprites)

    # Coins
    def display_text(self) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        if self.coin_timer.active:
            text_surf = self.fonts["main"].render(
                str(self.coin_amount), False, "#33323d"
            )
            text_rect = text_surf.get_frect(topleft=(16, 34))
            self.screen.blit(text_surf, text_rect)

            coin_rect = self.coin_surf.get_frect(center=text_rect.bottomleft).move(
                0, -6
            )
            self.screen.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount: int) -> None:
        self.coin_amount = amount
        self.coin_timer.activate()

    def update(self, dt: float) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        self.coin_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.screen)
        self.display_text()


class Heart(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: FrameList,
        *groups: pygame.sprite.Group,
        z: int = ZLayers.UI,
    ) -> None:
        super().__init__(pos, frames, *groups, z=z)
        self.timers = {"heart_anim_block": Timer(2000, random=True, lower_bound=500)}
        self.animating = False

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.animating = False
            self.frame_index = 0
            self.timers["heart_anim_block"].activate()

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def update(self, dt: float) -> None:
        self.update_timers()
        if self.animating:
            super().update(dt)
        else:
            if not self.timers["heart_anim_block"].active:
                self.animating = True
