from __future__ import annotations

import logging
import sys

import pygame

from savematter.game.data import Data
from savematter.game.level import Level
from savematter.game.overworld import Overworld
from savematter.game.ui import UI
from savematter.utils.assets import AssetManager
from savematter.utils.settings import (
    FPS,
    WINDOW_H,
    WINDOW_W,
    GameState,
)
from savematter.utils.typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pytmx.pytmx import TiledMap as TiledMap


class Game:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Save the Matter!")
        self.clock = pygame.time.Clock()

        # Asset loading
        self.assets = AssetManager()
        self.level_frames = self.assets.level_frames
        self.fonts = self.assets.fonts
        self.ui_frames = self.assets.ui_frames
        self.overworld_frames = self.assets.overworld_frames
        self.audio_files = self.assets.audio_files
        self.music_files = self.assets.music_files
        self.tmx_maps = cast("dict[int, TiledMap]", self.assets.tmx_files["maps"])
        self.tmx_overworld = cast("TiledMap", self.assets.tmx_files["overworld"])

        self.ui = UI(self.fonts, self.ui_frames)
        self.data = Data(self.ui)

        self.setup_states()

        self.music_files["bg"].play(-1)

    def setup_states(self) -> None:
        self.current_state = Level(
            self.tmx_maps[self.data.current_level],
            self.data,
            self.level_frames,
            self.audio_files,
            self.switch_state,
        )

    def switch_state(self, target: GameState, unlock: int | None = None) -> None:
        """
        Switch between game states.

        Args:
            target: The target state.
            unlock: If transitioning to OVERWORLD, unlock the specified level.
                    If 'None', no level is unlocked.
                    If '-1', penalize the player (e.g., health loss).
        """
        if unlock is not None:
            unlock = unlock if unlock >= self.data.unlocked_level else None

        logging.debug(f"Switching to {target}, unlock={unlock}")
        match target:
            case GameState.LEVEL:
                self.current_state = Level(
                    self.tmx_maps[self.data.current_level],
                    self.data,
                    self.level_frames,
                    self.audio_files,
                    self.switch_state,
                )
            case GameState.OVERWORLD:
                if unlock == -1:
                    self.data.health -= 1
                elif unlock is not None:
                    self.data.unlocked_level = unlock
                self.current_state = Overworld(
                    self.tmx_overworld,
                    self.data,
                    self.overworld_frames,
                    self.switch_state,
                )

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000
            max_dt = 0.1
            dt = min(dt, max_dt)
            self.handle_events()

            self.check_game_over()
            self.update(dt)
            self.render()

    def check_game_over(self) -> None:
        if self.data.health <= 0:
            pygame.quit()
            sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt: float) -> None:
        self.current_state.run(dt)
        self.ui.update(dt)

    def render(self) -> None:
        pygame.display.update()


def main():
    game = Game()
    game.run()
