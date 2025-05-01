from enum import Enum, auto

WINDOW_W, WINDOW_H = 1280, 720
TILE_SIZE = 64
ANIM_SPEED = 6
FPS = 0

# Layers
Z_LAYERS = {
    "bg": 0,
    "clouds": 1,
    "bg tiles": 2,
    "path": 3,
    "bg details": 4,
    "main": 5,
    "water": 6,
    "fg": 7,
    "ui": 8,
}


class GameState(Enum):
    OVERWORLD = auto()
    LEVEL = auto()
