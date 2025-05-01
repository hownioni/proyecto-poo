from __future__ import annotations

from importlib.resources import files
from typing import Iterator

import pygame
from pytmx.util_pygame import load_pygame

from savematter.utils.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font
    from pygame.mixer import Sound
    from pytmx.pytmx import TiledMap

    from savematter.utils.typing import AnimationDict, FrameList


def _get_asset(*path_parts: str, suffix: str | None = None) -> str:
    """
    Get absolute path to an asset.

    Args:
        *path_parts: Path components (e.g., "graphics", "player", "idle").
        suffix: File extension (e.g., "png", "wav"). If None, it is assumed the extension is being written explicitly.

    Returns:
        Absolute path as a string.
    """
    path = files("savematter.assets").joinpath(*path_parts)
    path = str(path)
    if suffix:
        if "." in path_parts[-1]:
            path = path[: path.rfind(".")]
        path = f"{path}.{suffix}"

    return path


def _walk_assets(*path_parts: str) -> Iterator[tuple[str, list[str], list[str]]]:
    """
    Simulate os.walk() or Path.walk() for package assets.
    Yields (dir_path, subdirs, filenames) for each directory.
    """
    root = files("savematter.assets").joinpath(*path_parts)

    if not root.is_dir():
        raise NotADirectoryError(f"Asset path not found: {path_parts}")

    subdirs: list[str]
    filenames: list[str]
    subdirs, filenames = [], []
    for item in root.iterdir():
        if item.is_dir():
            subdirs.append(item.name)
        else:
            filenames.append(item.name)

    yield (str(root), subdirs, filenames)  # Current dir

    for subdir in subdirs:
        yield from _walk_assets(*path_parts, subdir)


def import_image(*path: str, alpha: bool = True, format: str = "png") -> Surface:
    full_path = _get_asset(*path, suffix=format)
    return (
        pygame.image.load(full_path).convert_alpha()
        if alpha
        else pygame.image.load(full_path).convert()
    )


def import_frames(*path: str, alpha: bool = True) -> FrameList:
    """
    Load all frames in an animation.

    Args:
        *path: The path (in parts) to a folder containing frames in an animation.
        alpha: Preserve transparency. True by default
    """
    frames: FrameList = []
    for folder_path, _, image_names in _walk_assets(*path):
        for image_name in sorted(image_names, key=lambda name: int(name.split(".")[0])):
            full_path = _get_asset(folder_path, image_name)
            frame = pygame.image.load(full_path)
            frames.append(frame.convert_alpha() if alpha else frame.convert())
    return frames


def import_image_dict(*path: str, alpha: bool = True) -> dict[str, Surface]:
    """
    Load all images inside a folder.

    Args:
        *path: The path (in parts) to a folder containing images.
        alpha: Preserve transparency. True by default
    """
    frame_dict: dict[str, Surface] = {}
    for folder_path, _, image_names in _walk_assets(*path):
        for image_name in image_names:
            full_path = _get_asset(folder_path, image_name)
            surface = pygame.image.load(full_path)
            frame_dict[image_name.split(".")[0]] = (
                surface.convert_alpha() if alpha else surface.convert()
            )
    return frame_dict


def import_anim_states(*path: str) -> AnimationDict:
    """
    Load all animations inside a folder.

    Args:
        *path: The path (in parts) to a folder containing animations (eg., "player/{jump, attack, walk})").
        alpha: Preserve transparency. True by default
    """
    frame_dict: AnimationDict = {}
    for _, sub_folders, __ in _walk_assets(*path):
        if sub_folders:
            for sub_folder in sub_folders:
                frame_dict[sub_folder] = import_frames(*path, sub_folder)
    return frame_dict


def import_font(*path: str, size: int = 20, suffix: str = "ttf") -> Font:
    """
    Import a single tmx file.

    Args:
        *path: The path (in parts) to the tmx file.
        size: Size of the font.
        suffix: File extension (e.g., "wav", "mp3").
    """
    full_path = _get_asset("graphics", "ui", "fonts", *path, suffix=suffix)
    return pygame.font.Font(full_path, size=size)


def import_tmx(*path: str) -> TiledMap:
    """
    Import a single tmx file.

    Args:
        *path: The path (in parts) to the tmx file.
    """
    full_path = _get_asset(*path, suffix="tmx")
    return load_pygame(full_path)


def import_audio(*path: str, suffix: str = "wav") -> Sound:
    """
    Import a single audio file.

    Args:
        *path: The path (in parts) to the audio file.
        suffix: File extension (e.g., "wav", "mp3").
    """

    full_path = _get_asset("audio", *path, suffix=suffix)
    return pygame.mixer.Sound(full_path)
