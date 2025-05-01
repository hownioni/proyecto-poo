from __future__ import annotations

from collections.abc import Callable as Callable
from typing import TYPE_CHECKING, Protocol
from typing import cast as cast

from pygame import Surface
from pygame.math import Vector2 as Vector2

if TYPE_CHECKING:
    from savematter.utils.settings import GameState


class SwitchState(Protocol):
    def __call__(self, target: GameState, unlock: int | None = None, /) -> None: ...


FrameList = list[Surface]
AnimationDict = dict[str, FrameList]
