from __future__ import annotations

from random import randint

import pygame

from savematter.sprites.overworld import Node, PlayerIcon, WalkPath
from savematter.sprites.sprites import AnimatedSprite, Sprite
from savematter.utils.groups import WorldSprites
from savematter.utils.settings import (
    TILE_SIZE,
    GameState,
    ZLayers,
)
from savematter.utils.typing import TYPE_CHECKING, Vector2, cast

if TYPE_CHECKING:
    from pygame import Surface
    from pytmx.pytmx import TiledMap, TiledObject
    from pytmx.pytmx import TiledObjectGroup as TiledObjectGroup

    from savematter.game.data import Data
    from savematter.utils.typing import AnimationDict, FrameList, SwitchState


class Overworld:
    def __init__(
        self,
        tmx_map: TiledMap,
        data: Data,
        overworld_frames: dict[
            str, Surface | FrameList | dict[str, Surface] | AnimationDict
        ],
        switch_state: SwitchState,
    ) -> None:
        self.screen = pygame.display.get_surface()
        self.data = data
        self.switch_state = switch_state

        # Groups
        self.all_sprites = WorldSprites(self.data)
        self.node_sprites = pygame.sprite.Group()

        self.setup(tmx_map, overworld_frames)

        self.current_node: Node = [
            node for node in self.node_sprites if node.level == 0
        ][0]

        self.path_surfs = cast("dict[str, Surface]", overworld_frames["path"])
        self.create_path_sprites()

    def setup(
        self,
        tmx_map: TiledMap,
        overworld_frames: dict[
            str,
            Surface | FrameList | dict[str, Surface] | AnimationDict,
        ],
    ) -> None:
        # Tiles
        for layer in ["main", "top"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    self.all_sprites,
                    z=ZLayers.BG_TILES,
                )

        # Water
        for col in range(tmx_map.width):
            for row in range(tmx_map.height):
                AnimatedSprite(
                    (col * TILE_SIZE, row * TILE_SIZE),
                    cast("FrameList", overworld_frames["water"]),
                    self.all_sprites,
                    z=ZLayers.BG,
                )

        # Objects
        obj: TiledObject
        for obj in cast("TiledObjectGroup", tmx_map.get_layer_by_name("Objects")):
            if obj.name is None:
                raise TypeError("Object name is empty")

            match obj.name:
                case "palm":
                    AnimatedSprite(
                        (obj.x, obj.y),
                        cast("FrameList", overworld_frames["palms"]),
                        self.all_sprites,
                        z=ZLayers.MAIN,
                        anim_speed=randint(4, 6),
                    )
                case _:
                    if obj.image is None:
                        raise TypeError("Object image is empty")

                    z = ZLayers.BG_DETAILS if obj.name == "grass" else ZLayers.BG_TILES
                    Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=z)

        # Paths
        self.paths = {}
        for obj in cast("TiledObjectGroup", tmx_map.get_layer_by_name("Paths")):
            pos = [
                (point.x + TILE_SIZE / 2, point.y + TILE_SIZE / 2)
                for point in obj.points
            ]
            start: int = obj.properties["start"]
            end: int = obj.properties["end"]
            self.paths[end] = {"pos": pos, "start": start}

        # Nodes & Player
        for obj in cast("TiledObjectGroup", tmx_map.get_layer_by_name("Nodes")):
            match obj.name:
                case "Node":
                    if obj.properties["stage"] == self.data.current_level:
                        self.player_icon = PlayerIcon(
                            (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2),
                            "idle",
                            cast("AnimationDict", overworld_frames["icon"]),
                            self.all_sprites,
                        )
                    avail_dirs: dict[str, str] = {
                        dir: v
                        for dir, v in obj.properties.items()
                        if dir in ("left", "right", "up", "down")
                    }
                    Node(
                        (obj.x, obj.y),
                        cast("dict[str, Surface]", overworld_frames["path"])["node"],
                        obj.properties["stage"],
                        self.data,
                        avail_dirs,
                        *(self.all_sprites, self.node_sprites),
                    )

    def create_path_sprites(self):
        # Get tiles from path
        nodes = {node.level: Vector2(node.grid_pos) for node in self.node_sprites}
        path_tiles: dict[int, list[Vector2]] = {}

        for path_id, data in self.paths.items():
            path = data["pos"]
            start_node, end_node = nodes[data["start"]], nodes[path_id]
            path_tiles[path_id] = [start_node]

            for idx, points in enumerate(path):
                if idx < len(path) - 1:
                    start, end = Vector2(points), Vector2(path[idx + 1])
                    path_dir = (end - start) / TILE_SIZE
                    start_tile = Vector2(
                        int(start[0] / TILE_SIZE), int(start[1] / TILE_SIZE)
                    )

                    if path_dir.y:
                        dir_y = 1 if path_dir.y > 0 else -1
                        for y in range(dir_y, int(path_dir.y) + dir_y, dir_y):
                            path_tiles[path_id].append(start_tile + Vector2(0, y))

                    if path_dir.x:
                        dir_x = 1 if path_dir.x > 0 else -1
                        for x in range(dir_x, int(path_dir.x) + dir_x, dir_x):
                            path_tiles[path_id].append(start_tile + Vector2(x, 0))

            path_tiles[path_id].append(end_node)

        # Create sprites
        for key, path in path_tiles.items():
            for idx, tile in enumerate(path):
                if idx > 0 and idx < len(path) - 1:
                    prev_tile = path[idx - 1] - tile
                    next_tile = path[idx + 1] - tile

                    if prev_tile.x == next_tile.x:
                        surf = self.path_surfs["vertical"]
                    elif prev_tile.y == next_tile.y:
                        surf = self.path_surfs["horizontal"]
                    elif (
                        prev_tile.x == -1
                        and next_tile.y == -1
                        or prev_tile.y == -1
                        and next_tile.x == -1
                    ):
                        surf = self.path_surfs["tl"]
                    elif (
                        prev_tile.x == 1
                        and next_tile.y == 1
                        or prev_tile.y == 1
                        and next_tile.x == 1
                    ):
                        surf = self.path_surfs["br"]
                    elif (
                        prev_tile.x == -1
                        and next_tile.y == 1
                        or prev_tile.y == 1
                        and next_tile.x == -1
                    ):
                        surf = self.path_surfs["bl"]
                    elif (
                        prev_tile.x == 1
                        and next_tile.y == -1
                        or prev_tile.y == -1
                        and next_tile.x == 1
                    ):
                        surf = self.path_surfs["tr"]
                    else:
                        surf = self.path_surfs["horizontal"]

                    WalkPath(
                        (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                        surf,
                        key,
                        self.all_sprites,
                    )

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        if self.current_node and not self.player_icon.path:
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.current_node.can_move(
                "down"
            ):
                self.move("down")
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.current_node.can_move(
                "up"
            ):
                self.move("up")
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.current_node.can_move(
                "left"
            ):
                self.move("left")
            if (
                keys[pygame.K_RIGHT] or keys[pygame.K_d]
            ) and self.current_node.can_move("right"):
                self.move("right")
            if keys[pygame.K_z] or keys[pygame.K_RETURN]:
                self.data.current_level = self.current_node.level
                self.switch_state(GameState.LEVEL)

    def move(self, dir: str) -> None:
        dir_key = int(self.current_node.dirs[dir][0])
        dir_reverse = True if self.current_node.dirs[dir][-1] == "r" else False
        path = (
            self.paths[dir_key]["pos"][:]
            if not dir_reverse
            else self.paths[dir_key]["pos"][::-1]
        )
        self.player_icon.start_moving(path)

    def get_curr_node(self):
        nodes = pygame.sprite.spritecollide(self.player_icon, self.node_sprites, False)
        if nodes:
            self.current_node = nodes[0]

    def run(self, dt: float) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        if self.player_icon.rect is None:
            raise TypeError("Player icon rect is empty")

        self.input()
        self.get_curr_node()
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player_icon.rect.center, dt)
