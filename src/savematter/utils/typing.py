from __future__ import annotations

from collections.abc import Callable as Callable
from typing import TYPE_CHECKING, Protocol, TypeIs
from typing import cast as cast

from pygame import Surface
from pygame.math import Vector2 as Vector2

if TYPE_CHECKING:
    from savematter.utils.settings import GameState


class SwitchState(Protocol):
    def __call__(self, target: GameState, unlock: int | None = None, /) -> None: ...


FrameList = list[Surface]
AnimationDict = dict[str, FrameList]
SurfCollection = Surface | FrameList | dict[str, Surface] | AnimationDict


def is_surf(x: SurfCollection) -> TypeIs[Surface]:
    return isinstance(x, Surface)


def is_frame_list(x: SurfCollection) -> TypeIs[FrameList]:
    return isinstance(x, list) and all(isinstance(item, Surface) for item in x)


def is_surf_dict(x: SurfCollection) -> TypeIs[dict[str, Surface]]:
    return isinstance(x, dict) and all(
        isinstance(k, str) and (v, Surface) for k, v in x.items()
    )


def is_anim_dict(x: SurfCollection) -> TypeIs[AnimationDict]:
    return isinstance(x, dict) and all(
        isinstance(k, str) and is_frame_list(v) for k, v in x.items()
    )
