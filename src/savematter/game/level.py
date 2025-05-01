"""
Level scene manager for platformer gameplay.
Handles:
- Tilemap rendering (TMX)
- Physics/collisions
- Enemy/object spawning
- Player interactions
"""

from __future__ import annotations

from random import uniform

import pygame

from savematter.game.data import Data
from savematter.game.player import Player
from savematter.sprites.enemies import Pearl, Shell, Tooth
from savematter.sprites.objects import FloorSpike, Spike
from savematter.sprites.sprites import (
    AnimatedSprite,
    Item,
    MovingSprite,
    ParticleEffectSprite,
    Sprite,
)
from savematter.utils.groups import AllSprites
from savematter.utils.settings import (
    ANIM_SPEED,
    TILE_SIZE,
    GameState,
    LevelLayers,
    ZLayers,
)
from savematter.utils.typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.mixer import Sound
    from pytmx.pytmx import TiledMap, TiledObject
    from pytmx.pytmx import TiledObjectGroup as TiledObjectGroup

    from savematter.utils.typing import AnimationDict, FrameList, SwitchState


class Level:
    def __init__(
        self,
        tmx_map: TiledMap,
        data: Data,
        level_frames: dict[
            str, Surface | FrameList | dict[str, Surface] | AnimationDict
        ],
        audio_files: dict[str, Sound],
        switch_state: SwitchState,
    ) -> None:
        self.screen = pygame.display.get_surface()
        self.data = data
        self.switch_state = switch_state

        # Level data
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE
        tmx_level_properties = cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.DATA)
        )[0].properties
        self.level_unlock: int = tmx_level_properties["level_unlock"]
        bg_tile = (
            cast("dict[str, Surface]", level_frames["bg_tiles"])[
                tmx_level_properties["bg"]
            ]
            if tmx_level_properties["bg"]
            else None
        )

        # Groups
        self.all_sprites = AllSprites(
            tmx_map.width,
            tmx_map.height,
            {
                "large": cast("list[Surface]", level_frames["cloud_large"]),
                "small": cast("Surface", level_frames["cloud_small"]),
            },
            bg_tile,
            tmx_level_properties["top_limit"],
            tmx_level_properties["horizon_line"],
        )
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        # Frames
        self.pearl_surf = cast("Surface", level_frames["pearl"])
        self.particle_frames = cast("list[Surface]", level_frames["particle"])

        self.setup(tmx_map, level_frames, audio_files)

        # Audio
        self.coin_sound = audio_files["coin"]
        self.coin_sound.set_volume(0.4)
        self.damage_sound = audio_files["damage"]
        self.damage_sound.set_volume(0.5)
        self.pearl_sound = audio_files["pearl"]

    def setup(
        self,
        tmx_map: TiledMap,
        level_frames: dict[
            str, Surface | FrameList | dict[str, Surface] | AnimationDict
        ],
        audio_files: dict[str, Sound],
    ) -> None:
        # Tiles
        for layer in [
            LevelLayers.BG,
            LevelLayers.TERRAIN,
            LevelLayers.FG,
            LevelLayers.PLATFORMS,
        ]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = []
                groups.append(self.all_sprites)
                match layer:
                    case LevelLayers.TERRAIN:
                        groups.append(self.collision_sprites)
                    case LevelLayers.PLATFORMS:
                        groups.append(self.semi_collision_sprites)

                match layer:
                    case LevelLayers.BG | LevelLayers.FG:
                        z = ZLayers.BG_TILES
                    case _:
                        z = ZLayers.MAIN

                Sprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    *groups,
                    z=z,
                )

        obj: TiledObject
        # Static objects
        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.BG_DETAILS)
        ):
            if obj.name is None:
                raise TypeError("Object name is empty")

            match obj.name:
                case "static":
                    if obj.image is None:
                        raise TypeError("Object image is empty")

                    z = ZLayers.BG_TILES

                    Sprite(
                        (obj.x, obj.y),
                        obj.image,
                        self.all_sprites,
                        z=z,
                    )
                case _:
                    AnimatedSprite(
                        (obj.x, obj.y),
                        cast("FrameList", level_frames[obj.name]),
                        self.all_sprites,
                        z=z,
                    )
                    if obj.name == "candle":
                        AnimatedSprite(
                            (obj.x - 20, obj.y - 20),
                            cast("FrameList", level_frames["candle_light"]),
                            self.all_sprites,
                            z=z,
                        )

        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.OBJECTS)
        ):
            if obj.name is None:
                raise TypeError("Object name is empty")

            match obj.name:
                case "player":
                    if obj.image is None:
                        raise TypeError("Object image is empty")

                    self.player = Player(
                        (obj.x, obj.y),
                        cast("AnimationDict", level_frames["player"]),
                        self.data,
                        audio_files,
                        self.collision_sprites,
                        self.semi_collision_sprites,
                        self.all_sprites,
                    )
                case "barrel" | "crate":
                    if obj.image is None:
                        raise TypeError("Object image is empty")

                    Sprite(
                        (obj.x, obj.y),
                        obj.image,
                        *(self.all_sprites, self.collision_sprites),
                    )
                case "floor_spike":
                    FloorSpike(
                        (obj.x, obj.y),
                        cast("FrameList", level_frames["floor_spike"]),
                        obj.properties["inverted"],
                        *(self.all_sprites, self.damage_sprites),
                    )
                case _:
                    # Frames
                    frames = (
                        cast("FrameList", level_frames[obj.name])
                        if "palm" not in obj.name
                        else cast("AnimationDict", level_frames["palms"])[obj.name]
                    )

                    # Groups
                    groups = []
                    groups.append(self.all_sprites)
                    if obj.name in ("palm_small", "palm_large"):
                        groups.append(self.semi_collision_sprites)
                    if obj.name in ("saw"):
                        groups.append(self.damage_sprites)

                    # Z index
                    z = ZLayers.MAIN if "bg" not in obj.name else ZLayers.BG_DETAILS

                    # Anim speed
                    anim_speed = (
                        ANIM_SPEED
                        if "palm" not in obj.name
                        else ANIM_SPEED + uniform(-1, 1)
                    )

                    AnimatedSprite(
                        (obj.x, obj.y), frames, *groups, z=z, anim_speed=anim_speed
                    )

            if obj.name == "flag":
                self.level_finish_rect = pygame.FRect(
                    (obj.x, obj.y), (obj.width, obj.height)
                )

        # Moving objects
        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.MOVING_OBJS)
        ):
            if obj.name == "spike":
                Spike(
                    (obj.x + obj.width / 2, obj.y + obj.height / 2),
                    cast("Surface", level_frames["spike"]),
                    obj.properties["radius"],
                    obj.properties["speed"],
                    obj.properties["start_angle"],
                    obj.properties["end_angle"],
                    *(self.all_sprites, self.damage_sprites),
                )
                for radius in range(0, obj.properties["radius"], 20):
                    Spike(
                        (obj.x + obj.width / 2, obj.y + obj.height / 2),
                        cast("Surface", level_frames["spike_chain"]),
                        radius,
                        obj.properties["speed"],
                        obj.properties["start_angle"],
                        obj.properties["end_angle"],
                        self.all_sprites,
                        z=ZLayers.BG_DETAILS,
                    )
            else:
                if obj.name is None:
                    raise TypeError("Object name is empty")

                frames = cast("FrameList", level_frames[obj.name])
                groups = (
                    (self.all_sprites, self.semi_collision_sprites)
                    if obj.properties["platform"]
                    else [self.all_sprites, self.damage_sprites]
                )

                # X axis
                if obj.width > obj.height:
                    move_dir = "x"
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)

                # Y axis
                else:
                    move_dir = "y"
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)

                speed = obj.properties["speed"]

                MovingSprite(
                    frames,
                    start_pos,
                    end_pos,
                    move_dir,
                    speed,
                    *groups,
                    flip=obj.properties["flip"],
                )

                if obj.name == "saw":
                    if move_dir == "x":
                        y = (
                            start_pos[1]
                            - cast("Surface", level_frames["saw_chain"]).get_height()
                            / 2
                        )
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite(
                                (x, y),
                                cast("Surface", level_frames["saw_chain"]),
                                self.all_sprites,
                                z=ZLayers.BG_DETAILS,
                            )
                    else:
                        x = (
                            start_pos[0]
                            - cast("Surface", level_frames["saw_chain"]).get_width() / 2
                        )
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite(
                                (x, y),
                                cast("Surface", level_frames["saw_chain"]),
                                self.all_sprites,
                                z=ZLayers.BG_DETAILS,
                            )

        # Enemies
        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.ENEMIES)
        ):
            match obj.name:
                case "tooth":
                    Tooth(
                        (obj.x, obj.y),
                        cast("FrameList", level_frames["tooth"]),
                        self.collision_sprites,
                        *(self.all_sprites, self.damage_sprites, self.tooth_sprites),
                    )
                case "shell":
                    Shell(
                        (obj.x, obj.y),
                        cast("AnimationDict", level_frames["shell"]),
                        obj.properties["reverse"],
                        self.player,
                        self.create_perl,
                        *(self.all_sprites, self.collision_sprites),
                    )

        # Items
        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.ITEMS)
        ):
            if obj.name is None:
                raise TypeError("Object name is empty")

            Item(
                (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2),
                cast("AnimationDict", level_frames["items"])[obj.name],
                obj.name,
                self.data,
                *(self.all_sprites, self.item_sprites),
            )

        # Water
        for obj in cast(
            "TiledObjectGroup", tmx_map.get_layer_by_name(LevelLayers.WATER)
        ):
            rows = int(obj.height / TILE_SIZE)
            cols = int(obj.width / TILE_SIZE)

            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * TILE_SIZE
                    y = obj.y + row * TILE_SIZE

                    if row == 0:
                        AnimatedSprite(
                            (x, y),
                            cast("FrameList", level_frames["water_top"]),
                            self.all_sprites,
                            z=ZLayers.WATER,
                        )
                    else:
                        Sprite(
                            (x, y),
                            cast("Surface", level_frames["water_body"]),
                            self.all_sprites,
                            z=ZLayers.WATER,
                        )

    def create_perl(self, pos: tuple[float, float], direction: int) -> None:
        Pearl(
            pos,
            self.pearl_surf,
            direction,
            150,
            *(self.all_sprites, self.damage_sprites, self.pearl_sprites),
        )
        self.pearl_sound.play()

    def collisions(self) -> None:
        def hitbox_collide(sprite1: Player, sprite2: Sprite) -> bool:
            sprite1_rect = (
                sprite1.hitbox if hasattr(sprite1, "hitbox") else sprite1.rect  # pyright: ignore[reportAttributeAccessIssue]
            )
            sprite2_rect = (
                sprite2.hitbox if hasattr(sprite2, "hitbox") else sprite2.rect  # pyright: ignore[reportAttributeAccessIssue]
            )

            if sprite1_rect is None or sprite2_rect is None:
                raise TypeError("Sprite rect is empty")

            return sprite1_rect.colliderect(sprite2_rect)

        sprite: Sprite
        # Pearl
        for sprite in self.collision_sprites:
            sprites: list[Sprite] = pygame.sprite.spritecollide(
                sprite,
                self.pearl_sprites,
                True,
                hitbox_collide,  # pyright: ignore[reportArgumentType]
            )

            if sprites:
                if sprites[0].rect is None:
                    raise TypeError("Sprite rect is empty")

                ParticleEffectSprite(
                    (sprites[0].rect.center),
                    self.particle_frames,
                    self.all_sprites,
                )

        # Damage
        for sprite in self.damage_sprites:
            sprite_rect = sprite.hitbox if hasattr(sprite, "hitbox") else sprite.rect  # pyright: ignore[reportAttributeAccessIssue]

            if sprite_rect is None:
                raise TypeError("Sprite rect is empty")

            if sprite_rect.colliderect(self.player.hitbox):
                self.player.get_damage()
                self.damage_sound.play()

                if hasattr(sprite, "pearl"):
                    sprite.kill()
                    ParticleEffectSprite(
                        (sprite_rect.center),
                        self.particle_frames,
                        self.all_sprites,
                    )

        # Items
        if self.item_sprites:
            item_sprites: list[Item] = pygame.sprite.spritecollide(
                self.player,
                self.item_sprites,
                True,
                hitbox_collide,  # pyright: ignore[reportArgumentType]
            )
            if item_sprites:
                if item_sprites[0].rect is None:
                    raise TypeError("Sprite rect is empty")

                item_sprites[0].activate()
                ParticleEffectSprite(
                    (item_sprites[0].rect.center),
                    self.particle_frames,
                    self.all_sprites,
                )
                self.coin_sound.play()

        # Player attack
        targets: list[Tooth | Pearl] = (
            self.pearl_sprites.sprites() + self.tooth_sprites.sprites()
        )

        target: Tooth | Pearl
        for target in targets:
            target_rect = target.hitbox if hasattr(target, "hitbox") else target.rect  # pyright: ignore[reportAttributeAccessIssue]

            if self.player.rect is None or target_rect is None:
                raise TypeError("Player or target rect is empty")

            facing_target = (
                self.player.rect.centerx < target_rect.centerx
                and self.player.facing_right
                or self.player.rect.centerx > target_rect.centerx
                and not self.player.facing_right
            )

            if (
                target_rect.colliderect(self.player.rect)
                and self.player.attacking
                and facing_target
            ):
                target.reverse()

        ## Borders
        # Horizontal
        if self.player.hitbox.left <= 0:
            self.player.hitbox.left = 0
        elif self.player.hitbox.right >= self.level_width:
            self.player.hitbox.right = self.level_width

        # Bottom
        if self.player.hitbox.bottom > self.level_height:
            self.switch_state(GameState.OVERWORLD, -1)

        # Flag
        if self.player.hitbox.colliderect(self.level_finish_rect):
            self.switch_state(GameState.OVERWORLD, self.level_unlock)

    def run(self, dt: float) -> None:
        if self.screen is None:
            raise TypeError("Display surface is empty")

        self.screen.fill("black")

        self.all_sprites.update(dt)
        self.collisions()

        self.all_sprites.draw(self.player.hitbox.center, dt)
