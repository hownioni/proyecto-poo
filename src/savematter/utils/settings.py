from enum import Enum, IntEnum, StrEnum, auto, unique

WINDOW_W, WINDOW_H = 1280, 720
TILE_SIZE = 64
ANIM_SPEED = 6
FPS = 0


# Layers
@unique
class ZLayers(IntEnum):
    BG = 0
    CLOUDS = 1
    BG_TILES = 2
    PATH = 3
    BG_DETAILS = 4
    MAIN = 5
    WATER = 6
    FG = 7
    UI = 8


class GameState(Enum):
    OVERWORLD = auto()
    LEVEL = auto()


class LevelLayers(StrEnum):
    DATA = "Data"
    WATER = "Water"
    ENEMIES = "Enemies"
    ITEMS = "Items"
    MOVING_OBJS = "Moving Objects"
    OBJECTS = "Objects"
    FG = "FG"
    PLATFORMS = "Platforms"
    TERRAIN = "Terrain"
    BG_DETAILS = "BG details"
    BG = "BG"
