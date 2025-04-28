from __future__ import annotations

from os import walk
from os.path import join

from settings import TYPE_CHECKING, pygame

if TYPE_CHECKING:
    from pygame import Surface


def import_image(*path: str, alpha: bool = True, format: str = "png") -> Surface:
    full_path: str = join(*path) + f".{format}"
    return (
        pygame.image.load(full_path).convert_alpha()
        if alpha
        else pygame.image.load(full_path).convert()
    )


def import_folder(*path: str) -> list[Surface]:
    frames: list[Surface] = []
    for folder_path, subfolders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key=lambda name: int(name.split(".")[0])):
            full_path = join(folder_path, image_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames


def import_folder_dict(*path: str) -> dict[str, Surface]:
    frame_dict: dict[str, Surface] = {}
    folder_path: str
    image_names: list[str]
    for folder_path, _, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surface = pygame.image.load(full_path).convert_alpha()
            frame_dict[image_name.split(".")[0]] = surface
    return frame_dict


def import_sub_folders(*path: str) -> dict[str, list[Surface]]:
    frame_dict: dict[str, list[Surface]] = {}
    sub_folders: list[str]
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frame_dict[sub_folder] = import_folder(*path, sub_folder)
    return frame_dict
