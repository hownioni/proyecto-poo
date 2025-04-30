from __future__ import annotations

import logging
from pathlib import Path

from pytmx.util_pygame import load_pygame

from savematter.game.data import Data
from savematter.game.level import Level
from savematter.game.overworld import Overworld
from savematter.game.ui import UI
from savematter.utils.assets import AssetManager
from savematter.utils.settings import (
    FPS,
    TYPE_CHECKING,
    WINDOW_H,
    WINDOW_W,
    GameState,
    pygame,
    sys,
)

if TYPE_CHECKING:
    from pytmx.pytmx import TiledMap


class Game:
    def __init__(self) -> None:
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

        self.ui = UI(self.fonts, self.ui_frames)
        self.data = Data(self.ui)

        self.load_maps()
        self.setup_states()

        self.music_files["bg"].play(-1)

    def load_maps(self) -> None:
        """Load all TMX maps."""
        self.tmx_maps: dict[int, TiledMap] = {
            0: load_pygame(str(Path("assets/data/levels/omni.tmx"))),
            1: load_pygame(str(Path("assets/data/levels/1.tmx"))),
            2: load_pygame(str(Path("assets/data/levels/2.tmx"))),
            3: load_pygame(str(Path("assets/data/levels/3.tmx"))),
            4: load_pygame(str(Path("assets/data/levels/4.tmx"))),
            5: load_pygame(str(Path("assets/data/levels/5.tmx"))),
        }

        self.tmx_overworld = load_pygame(
            str(Path("assets/data/overworld/overworld.tmx"))
        )

    def setup_states(self) -> None:
        """Initialize game states."""
        self.current_stage = Level(
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
        logging.debug(f"Switching to {target}, unlock={unlock}")
        match target:
            case GameState.LEVEL:
                self.current_stage = Level(
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
                self.current_stage = Overworld(
                    self.tmx_overworld,
                    self.data,
                    self.overworld_frames,
                    self.switch_state,
                )

    def check_game_over(self) -> None:
        if self.data.health <= 0:
            pygame.quit()
            sys.exit()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()

            self.check_game_over()
            self.update(dt)
            self.render()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def render(self) -> None:
        pygame.display.update()

    def update(self, dt: float) -> None:
        self.current_stage.run(dt)
        self.ui.update(dt)


if __name__ == "__main__":
    game = Game()
    game.run()
