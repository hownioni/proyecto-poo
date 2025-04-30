from __future__ import annotations

from os.path import join

from savematter.utils.settings import TYPE_CHECKING, pygame
from savematter.utils.support import (
    import_folder,
    import_folder_dict,
    import_image,
    import_sub_folders,
)

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font
    from pygame.mixer import Sound


class AssetManager:
    def __init__(self) -> None:
        self.level_frames: dict[
            str,
            Surface | list[Surface] | dict[str, Surface] | dict[str, list[Surface]],
        ] = {}
        self.fonts: dict[str, Font] = {}
        self.ui_frames: dict[
            str,
            Surface | list[Surface] | dict[str, Surface] | dict[str, list[Surface]],
        ] = {}
        self.overworld_frames: dict[
            str,
            Surface | list[Surface] | dict[str, Surface] | dict[str, list[Surface]],
        ] = {}
        self.audio_files: dict[str, Sound] = {}
        self.music_files: dict[str, Sound] = {}
        self.load_assets()

    def load_assets(self) -> None:
        self.level_frames = {
            "flag": import_folder("assets", "graphics", "level", "flag"),
            "saw": import_folder("assets", "graphics", "enemies", "saw", "animation"),
            "floor_spike": import_folder(
                "assets", "graphics", "enemies", "floor_spikes"
            ),
            "palms": import_sub_folders("assets", "graphics", "level", "palms"),
            "candle": import_folder("assets", "graphics", "level", "candle"),
            "window": import_folder("assets", "graphics", "level", "window"),
            "big_chain": import_folder("assets", "graphics", "level", "big_chains"),
            "small_chain": import_folder("assets", "graphics", "level", "small_chains"),
            "candle_light": import_folder(
                "assets", "graphics", "level", "candle light"
            ),
            "player": import_sub_folders("assets", "graphics", "player"),
            "saw_chain": import_image(
                "assets", "graphics", "enemies", "saw", "saw_chain"
            ),
            "helicopter": import_folder("assets", "graphics", "level", "helicopter"),
            "boat": import_folder("assets", "graphics", "objects", "boat"),
            "spike": import_image(
                "assets", "graphics", "enemies", "spike_ball", "Spiked Ball"
            ),
            "spike_chain": import_image(
                "assets", "graphics", "enemies", "spike_ball", "spiked_chain"
            ),
            "tooth": import_folder("assets", "graphics", "enemies", "tooth", "run"),
            "shell": import_sub_folders("assets", "graphics", "enemies", "shell"),
            "pearl": import_image("assets", "graphics", "enemies", "bullets", "pearl"),
            "items": import_sub_folders("assets", "graphics", "items"),
            "particle": import_folder("assets", "graphics", "effects", "particle"),
            "water_top": import_folder("assets", "graphics", "level", "water", "top"),
            "water_body": import_image("assets", "graphics", "level", "water", "body"),
            "bg_tiles": import_folder_dict(
                "assets", "graphics", "level", "bg", "tiles"
            ),
            "cloud_small": import_folder(
                "assets", "graphics", "level", "clouds", "small"
            ),
            "cloud_large": import_image(
                "assets", "graphics", "level", "clouds", "large_cloud"
            ),
        }

        self.fonts = {
            "main": pygame.font.Font(
                join("assets", "graphics", "ui", "runescape_uf.ttf"), 40
            )
        }

        self.ui_frames = {
            "heart": import_folder("assets", "graphics", "ui", "heart"),
            "coin": import_image("assets", "graphics", "ui", "coin"),
        }

        self.overworld_frames = {
            "palms": import_folder("assets", "graphics", "overworld", "palm"),
            "water": import_folder("assets", "graphics", "overworld", "water"),
            "path": import_folder_dict("assets", "graphics", "overworld", "path"),
            "icon": import_sub_folders("assets", "graphics", "overworld", "icon"),
        }

        self.audio_files = {
            "coin": pygame.mixer.Sound(join("assets", "audio", "coin.wav")),
            "attack": pygame.mixer.Sound(join("assets", "audio", "attack.wav")),
            "jump": pygame.mixer.Sound(join("assets", "audio", "jump.wav")),
            "damage": pygame.mixer.Sound(join("assets", "audio", "damage.wav")),
            "pearl": pygame.mixer.Sound(join("assets", "audio", "pearl.wav")),
        }
        self.music_files = {
            "bg": pygame.mixer.Sound(join("assets", "audio", "starlight_city.mp3"))
        }
        self.music_files["bg"].set_volume(0.5)
