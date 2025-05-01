from __future__ import annotations

from savematter.utils.support import (
    import_anim_states,
    import_audio,
    import_font,
    import_frames,
    import_image,
    import_image_dict,
    import_tmx,
)
from savematter.utils.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font
    from pygame.mixer import Sound
    from pytmx.pytmx import TiledMap

    from savematter.utils.typing import AnimationDict, FrameList


class AssetManager:
    def __init__(self) -> None:
        self.level_frames: dict[
            str,
            Surface | FrameList | dict[str, Surface] | AnimationDict,
        ] = {}
        self.fonts: dict[str, Font] = {}
        self.ui_frames: dict[
            str,
            Surface | FrameList | dict[str, Surface] | AnimationDict,
        ] = {}
        self.overworld_frames: dict[
            str,
            Surface | FrameList | dict[str, Surface] | AnimationDict,
        ] = {}
        self.audio_files: dict[str, Sound] = {}
        self.music_files: dict[str, Sound] = {}
        self.tmx_files: dict[str, dict[int, TiledMap] | TiledMap] = {}
        self.load_assets()

    def load_assets(self) -> None:
        self.level_frames = {
            "flag": import_frames("graphics", "level", "flag"),
            "saw": import_frames("graphics", "enemies", "saw", "animation"),
            "floor_spike": import_frames("graphics", "enemies", "floor_spikes"),
            "palms": import_anim_states("graphics", "level", "palms"),
            "candle": import_frames("graphics", "level", "candle"),
            "window": import_frames("graphics", "level", "window"),
            "big_chain": import_frames("graphics", "level", "big_chains"),
            "small_chain": import_frames("graphics", "level", "small_chains"),
            "candle_light": import_frames("graphics", "level", "candle light"),
            "player": import_anim_states("graphics", "player"),
            "saw_chain": import_image("graphics", "enemies", "saw", "saw_chain"),
            "helicopter": import_frames("graphics", "level", "helicopter"),
            "boat": import_frames("graphics", "objects", "boat"),
            "spike": import_image("graphics", "enemies", "spike_ball", "Spiked Ball"),
            "spike_chain": import_image(
                "graphics", "enemies", "spike_ball", "spiked_chain"
            ),
            "tooth": import_frames("graphics", "enemies", "tooth", "run"),
            "shell": import_anim_states("graphics", "enemies", "shell"),
            "pearl": import_image("graphics", "enemies", "bullets", "pearl"),
            "items": import_anim_states("graphics", "items"),
            "particle": import_frames("graphics", "effects", "particle"),
            "water_top": import_frames("graphics", "level", "water", "top"),
            "water_body": import_image("graphics", "level", "water", "body"),
            "bg_tiles": import_image_dict("graphics", "level", "bg", "tiles"),
            "cloud_small": import_frames("graphics", "level", "clouds", "small"),
            "cloud_large": import_image("graphics", "level", "clouds", "large_cloud"),
        }

        self.fonts = {"main": import_font("runescape_uf", size=40)}

        self.ui_frames = {
            "heart": import_frames("graphics", "ui", "heart"),
            "coin": import_image("graphics", "ui", "coin"),
        }

        self.overworld_frames = {
            "palms": import_frames("graphics", "overworld", "palm"),
            "water": import_frames("graphics", "overworld", "water"),
            "path": import_image_dict("graphics", "overworld", "path"),
            "icon": import_anim_states("graphics", "overworld", "icon"),
        }

        self.audio_files = {
            "coin": import_audio("effects", "coin"),
            "attack": import_audio("effects", "attack"),
            "jump": import_audio("effects", "jump"),
            "damage": import_audio("effects", "damage"),
            "pearl": import_audio("effects", "pearl"),
        }
        self.music_files = {"bg": import_audio("music", "starlight_city", suffix="mp3")}
        self.music_files["bg"].set_volume(0.5)

        tmx_maps: dict[int, TiledMap] = {
            0: import_tmx("data", "levels", "omni"),
            1: import_tmx("data", "levels", "1"),
            2: import_tmx("data", "levels", "2"),
            3: import_tmx("data", "levels", "3"),
            4: import_tmx("data", "levels", "4"),
            5: import_tmx("data", "levels", "5"),
            6: import_tmx("data", "levels", "6"),
        }

        tmx_overworld = import_tmx("data", "overworld", "overworld")

        self.tmx_files["maps"] = tmx_maps
        self.tmx_files["overworld"] = tmx_overworld
