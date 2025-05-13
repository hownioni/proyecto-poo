from __future__ import annotations

from savematter.utils.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from savematter.game.ui import UI


class Data:
    def __init__(self, ui: UI) -> None:
        self.ui = ui
        self._coins = 0
        self._health = 5
        self.ui.create_hearts(self._health)

        self.unlocked_level = 5
        self.current_level = 5
        self.unlocked_overworld = 0
        self.current_overworld = 0

    @property
    def health(self) -> int:
        return self._health

    @property
    def coins(self) -> int:
        return self._coins

    @health.setter
    def health(self, value: int) -> None:
        self._health = value
        self.ui.create_hearts(value)

    @coins.setter
    def coins(self, value: int) -> None:
        self._coins = value
        if self.coins >= 100:
            self.coins -= 100
            self.health += 1
        self.ui.show_coins(value)
