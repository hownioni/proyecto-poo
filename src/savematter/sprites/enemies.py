from __future__ import annotations

from collections.abc import Callable
from random import choice

from savematter.game.player import Player
from savematter.sprites.sprites import AnimatedSprite, Sprite, StateAnimatedSprite
from savematter.utils.settings import TYPE_CHECKING, Vector2, pygame
from savematter.utils.timer import Timer

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.sprite import Group


class Tooth(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[Surface],
        collision_sprites: Group,
        *groups: Group,
    ) -> None:
        super().__init__(pos, frames, *groups)

        # Collision
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        # Movement
        self.direction = choice((-1, 1))
        self.speed = 200

        self.reverse_timer = Timer(250)

    def move(self, dt: float):
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.x += self.direction * self.speed * dt

    def collision(self):
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        floor_rect_right = pygame.FRect(self.rect.bottomright, (1, 1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, 1))
        wall_rect = pygame.FRect(
            self.rect.topleft + Vector2(-1, 0), (self.rect.width + 2, 1)
        )

        if (
            floor_rect_right.collidelist(self.collision_rects) < 0
            and self.direction > 0
            or floor_rect_left.collidelist(self.collision_rects) < 0
            and self.direction < 0
            or wall_rect.collidelist(self.collision_rects) != -1
        ):
            self.direction *= -1

    def reverse(self):
        if not self.reverse_timer.active:
            self.direction *= -1
            self.reverse_timer.activate()

    def update(self, dt: float) -> None:
        self.reverse_timer.update()

        super().update(dt)
        if self.image is None:
            raise TypeError("Sprite image is empty")

        self.image = (
            pygame.transform.flip(self.image, True, False)
            if self.direction < 0
            else self.image
        )

        self.move(dt)
        self.collision()


class Shell(StateAnimatedSprite):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: dict[str, list[Surface]],
        reverse: bool,
        player: Player,
        create_pearl: Callable[[tuple[float, float], int], None],
        *groups: Group,
    ) -> None:
        super().__init__(pos, "idle", frames, *groups)

        if reverse:
            self.frames = {}
            for key, surfs in frames.items():
                self.frames[key] = [
                    pygame.transform.flip(surf, True, False) for surf in surfs
                ]
            self.bullet_direction = -1
        else:
            self.frames = frames
            self.bullet_direction = 1

        self.player = player
        self.shoot_timer = Timer(3000)
        self.has_fired = False
        self.create_pearl = create_pearl

    def get_anim_state(self) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        player_pos, shell_pos = (
            Vector2(self.player.hitbox.center),
            Vector2(self.rect.center),
        )

        player_near = shell_pos.distance_to(player_pos) < 500
        player_front = (
            shell_pos.x < player_pos.x
            if self.bullet_direction > 0
            else shell_pos.x > player_pos.x
        )
        player_level = abs(shell_pos.y - player_pos.y) < 30

        if (
            player_near
            and player_front
            and player_level
            and not self.shoot_timer.active
        ):
            self.state = "fire"
            self.frame_index = 0
            self.shoot_timer.activate()

    def attack(self) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        if self.state == "fire" and int(self.frame_index) == 3 and not self.has_fired:
            self.create_pearl(self.rect.center, self.bullet_direction)
            self.has_fired = True

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_speed * dt
        if self.image is None:
            raise TypeError("Sprite image is empty")

        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]
            self.attack()
        else:
            self.frame_index = 0
            if self.state == "fire":
                self.state = "idle"
                self.has_fired = False

    def update(self, dt: float) -> None:
        self.shoot_timer.update()
        super().update(dt)


class Pearl(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: Surface,
        direction: int,
        speed: float,
        *groups: Group,
    ) -> None:
        self.pearl = True
        super().__init__(pos, surf, *groups)

        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.center = pos + Vector2(50 * direction, 0)

        self.direction = direction
        self.speed = speed

        self.timers = {
            "lifetime": Timer(5000, self.kill),
            "reverse": Timer(250),
        }
        self.timers["lifetime"].activate()

    def move(self, dt: float) -> None:
        if self.rect is None:
            raise TypeError("Sprite rect is empty")

        self.rect.x += self.direction * self.speed * dt

    def reverse(self):
        if not self.timers["reverse"].active:
            self.direction *= -1
            self.timers["reverse"].activate()

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def update(self, dt: float) -> None:
        self.update_timers()
        self.move(dt)
