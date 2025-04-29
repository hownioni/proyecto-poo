from __future__ import annotations

from os.path import join

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
    pygame,
    sys,
)

if TYPE_CHECKING:
    pass


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Save the matter!")
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
        self.tmx_maps = {
            0: load_pygame(join("assets", "data", "levels", "omni.tmx")),
            1: load_pygame(join("assets", "data", "levels", "1.tmx")),
            2: load_pygame(join("assets", "data", "levels", "2.tmx")),
            3: load_pygame(join("assets", "data", "levels", "3.tmx")),
            4: load_pygame(join("assets", "data", "levels", "4.tmx")),
            5: load_pygame(join("assets", "data", "levels", "5.tmx")),
        }
        self.tmx_overworld = load_pygame(
            join("assets", "data", "overworld", "overworld.tmx")
        )
        self.current_stage = Level(
            self.tmx_maps[self.data.current_level],
            self.data,
            self.level_frames,
            self.audio_files,
            self.switch_stage,
        )

        self.music_files["bg"].play(-1)

    def switch_stage(self, target: str, unlock: int) -> None:
        if target == "level":
            self.current_stage = Level(
                self.tmx_maps[self.data.current_level],
                self.data,
                self.level_frames,
                self.audio_files,
                self.switch_stage,
            )
        else:  # Overworld
            if unlock > 0:
                self.data.unlocked_level = unlock
            else:
                self.data.health -= 1
            self.current_stage = Overworld(
                self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage
            )
            print(target)
            print(unlock)

    def check_game_over(self) -> None:
        if self.data.health <= 0:
            pygame.quit()
            sys.exit()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.check_game_over()
            self.current_stage.run(dt)

            self.ui.update(dt)
            # debug(self.data.coins, (30, 10))
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
