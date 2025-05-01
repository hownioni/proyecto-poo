from __future__ import annotations

from math import sin

import pygame

from savematter.game.data import Data
from savematter.sprites.sprites import StateAnimatedSprite
from savematter.utils.timer import Timer
from savematter.utils.typing import TYPE_CHECKING, Vector2

if TYPE_CHECKING:
    from pygame.mixer import Sound

    from savematter.sprites.sprites import MovingSprite, Sprite


class Player(StateAnimatedSprite):
    def __init__(
        self,
        pos: tuple[int, int],
        frames: dict[str, list[pygame.Surface]],
        data: Data,
        audio_files: dict[str, Sound],
        collision_sprites: pygame.sprite.Group,
        semi_collision_sprites: pygame.sprite.Group,
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(pos, "idle", frames, *groups)
        self.data = data

        # Image
        self.facing_right = True

        # Rects
        if self.rect is None:
            raise TypeError("Player rect is empty")

        self.hitbox = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox.copy()

        # Movement
        self.direction = Vector2()
        self.speed = 200
        self.gravity = 1300
        self.jump = False
        self.jump_height = 900
        self.attacking = False

        # Collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surf = {"floor": False, "left": False, "right": False}
        self.platform = None

        # Timer
        self.timers = {
            "wall_jump": Timer(400),
            "wall_slide_block": Timer(250),
            "platform_fall": Timer(100),
            "attack_block": Timer(500),
            "immunity_frames": Timer(650),
        }

        # Sounds
        self.attack_sound = audio_files["attack"]
        self.jump_sound = audio_files["jump"]

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        input_vector = Vector2(0, 0)

        if not self.timers["wall_jump"].active:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                input_vector.x += -1
                self.facing_right = False

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.timers["platform_fall"].activate()

            if keys[pygame.K_x]:
                self.attack()

            self.direction.x = (
                input_vector.normalize().x if input_vector else input_vector.x
            )

        if keys[pygame.K_SPACE]:
            self.jump = True

    def attack(self) -> None:
        if not self.timers["attack_block"].active:
            self.attacking = True
            self.frame_index = 0
            self.timers["attack_block"].activate()
            self.attack_sound.play()

    def move(self, dt: float) -> None:
        # X axis
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision("x")

        # Y axis
        on_wall = any((self.on_surf["left"], self.on_surf["right"]))
        if (
            not self.on_surf["floor"]
            and on_wall
            and not self.timers["wall_slide_block"].active
        ):
            self.direction.y = 0
            self.hitbox.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surf["floor"]:
                self.direction.y = -self.jump_height
                self.timers["wall_slide_block"].activate()
                self.hitbox.bottom -= 1
                self.jump_sound.play()
            elif on_wall and not self.timers["wall_slide_block"].active:
                self.timers["wall_jump"].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surf["left"] else -1
                self.jump_sound.play()
            self.jump = False

        self.collision("y")
        self.semi_collision()
        if self.rect is None:
            raise TypeError("Player rect is empty")

        self.rect.center = self.hitbox.center

        if self.platform:
            self.hitbox.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self) -> None:
        contact_thickness = 2
        floor_rect = pygame.Rect(
            self.hitbox.bottomleft, (self.hitbox.width, contact_thickness)
        )
        left_rect = pygame.Rect(
            self.hitbox.topleft + Vector2(-contact_thickness, self.hitbox.height / 4),
            (contact_thickness, self.hitbox.height / 2),
        )
        right_rect = pygame.Rect(
            self.hitbox.topright + Vector2(0, self.hitbox.height / 4),
            (contact_thickness, self.hitbox.height / 2),
        )

        collide_rects = [
            sprite.hitbox if hasattr(sprite, "hitbox") else sprite.rect
            for sprite in self.collision_sprites
        ]
        semi_collide_rects = [
            sprite.hitbox if hasattr(sprite, "hitbox") else sprite.rect
            for sprite in self.semi_collision_sprites
        ]

        # Collisions
        self.on_surf["floor"] = (
            True
            if floor_rect.collidelist(collide_rects) >= 0
            or floor_rect.collidelist(semi_collide_rects) >= 0
            and self.direction.y >= 0
            else False
        )
        self.on_surf["left"] = (
            True if left_rect.collidelist(collide_rects) >= 0 else False
        )
        self.on_surf["right"] = (
            True if right_rect.collidelist(collide_rects) >= 0 else False
        )

        self.platform = None
        sprite: MovingSprite
        sprites = (
            self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        )
        for sprite in [sprite for sprite in sprites if hasattr(sprite, "moving")]:
            if sprite.rect is None:
                raise TypeError("Sprite rect is empty")

            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis) -> None:
        sprite: Sprite
        for sprite in self.collision_sprites:
            sprite_rect = sprite.hitbox if hasattr(sprite, "hitbox") else sprite.rect  # pyright: ignore[reportAttributeAccessIssue]

            if sprite_rect is None:
                raise TypeError("Sprite rect is empty")

            if sprite_rect.colliderect(self.hitbox):
                if axis == "x":
                    # Left
                    if self.hitbox.left <= sprite_rect.right and int(
                        self.old_rect.left
                    ) >= int(sprite.old_rect.right):
                        self.hitbox.left = sprite_rect.right

                    # Right
                    if self.hitbox.right >= sprite_rect.left and int(
                        self.old_rect.right
                    ) <= int(sprite.old_rect.left):
                        self.hitbox.right = sprite_rect.left

                elif axis == "y":
                    # Top
                    if self.hitbox.top <= sprite_rect.bottom and int(
                        self.old_rect.top
                    ) >= int(sprite.old_rect.bottom):
                        self.hitbox.top = sprite_rect.bottom
                        if hasattr(sprite, "moving"):
                            self.hitbox.top += 6

                    # Bottom
                    if self.hitbox.bottom >= sprite_rect.top and int(
                        self.old_rect.bottom
                    ) <= int(sprite.old_rect.top):
                        self.hitbox.bottom = sprite_rect.top

                    self.direction.y = 0
                else:
                    raise ValueError("Value must be either x or y")

    def semi_collision(self) -> None:
        if not self.timers["platform_fall"].active:
            sprite: Sprite
            for sprite in self.semi_collision_sprites:
                if sprite.rect is None:
                    raise TypeError("Sprite rect is empty")

                if sprite.rect.colliderect(self.hitbox):
                    # Bottom
                    if (
                        self.hitbox.bottom >= sprite.rect.top
                        and int(self.old_rect.bottom) <= sprite.old_rect.top
                    ):
                        self.hitbox.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0

    def get_damage(self) -> None:
        if not self.timers["immunity_frames"].active:
            self.data.health -= 1
            self.timers["immunity_frames"].activate()

    def flicker(self) -> None:
        if self.timers["immunity_frames"].active and sin(pygame.time.get_ticks()) >= 0:
            if self.image is None:
                raise TypeError("Player image is empty")

            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey("black")
            self.image = white_surf

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def get_anim_state(self) -> None:
        if self.on_surf["floor"]:
            if self.attacking:
                self.state = "attack"
            else:
                self.state = "idle" if self.direction.x == 0 else "run"
        elif self.attacking:
            self.state = "air_attack"
        elif any((self.on_surf["left"], self.on_surf["right"])):
            self.state = "wall"
        else:
            self.state = "jump" if self.direction.y < 0 else "fall"

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        if self.state == "attack" and self.frame_index >= len(self.frames[self.state]):
            self.state = "idle"
        self.image = self.frames[self.state][
            int(self.frame_index) % len(self.frames[self.state])
        ]
        self.image = (
            self.image
            if self.facing_right
            else pygame.transform.flip(self.image, True, False)
        )

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def update(self, dt: float) -> None:
        self.old_rect = self.hitbox.copy()
        self.update_timers()
        self.input()
        self.move(dt)
        self.check_contact()
        super().update(dt)
        self.flicker()
