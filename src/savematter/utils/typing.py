from __future__ import annotations

from typing import Protocol

from savematter.utils.settings import TYPE_CHECKING

if TYPE_CHECKING:
    from savematter.utils.settings import GameState


class SwitchState(Protocol):
    def __call__(self, target: GameState, unlock: int | None = None, /) -> None: ...
