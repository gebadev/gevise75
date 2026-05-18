from enum import Enum, auto

import pyxel

from game.field import Field, CellType
from game.constants import FIELD_W, FIELD_H


class PlayerState(Enum):
    ON_BORDER = auto()
    DRAWING = auto()


class PlayerResult(Enum):
    NONE = auto()
    MISS = auto()  # 自分のTrailへの衝突
    TRAIL_COMPLETE = auto()  # BORDERへの帰還 → complete_trail を呼ぶこと


class Player:
    def __init__(self) -> None:
        self.x: int = FIELD_W // 2
        self.y: int = FIELD_H - 1
        self.state: PlayerState = PlayerState.ON_BORDER
        self.trail: list[tuple[int, int]] = []

    def update(self, field: Field) -> PlayerResult:
        dx, dy = 0, 0
        if pyxel.btn(pyxel.KEY_LEFT):
            dx = -1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            dx = 1
        elif pyxel.btn(pyxel.KEY_UP):
            dy = -1
        elif pyxel.btn(pyxel.KEY_DOWN):
            dy = 1

        if dx == 0 and dy == 0:
            return PlayerResult.NONE

        nx, ny = self.x + dx, self.y + dy
        if not (0 <= nx < field.width and 0 <= ny < field.height):
            return PlayerResult.NONE

        cell = field.grid[ny][nx]

        if self.state == PlayerState.ON_BORDER:
            if cell == CellType.BORDER:
                self.x, self.y = nx, ny
            elif cell == CellType.UNCLAIMED:
                # BORDERを離れてTrail開始。trail[0] に出発BORDERを記録する
                self.state = PlayerState.DRAWING
                self.trail = [(self.x, self.y)]
                field.do_trail(nx, ny)
                self.trail.append((nx, ny))
                self.x, self.y = nx, ny

        else:  # DRAWING
            if cell == CellType.TRAIL:
                return PlayerResult.MISS
            elif cell == CellType.BORDER:
                # BORDERへ帰還 → Trail完成。フィールドのTrailはまだ残っているので
                # 呼び出し元が field.complete_trail() を実行すること
                self.x, self.y = nx, ny
                self.state = PlayerState.ON_BORDER
                self.trail = []
                return PlayerResult.TRAIL_COMPLETE
            elif cell == CellType.UNCLAIMED:
                field.do_trail(nx, ny)
                self.trail.append((nx, ny))
                self.x, self.y = nx, ny

        return PlayerResult.NONE

    def cancel_trail(self, field: Field) -> None:
        """ミス時の処理。Trailを消して出発BORDER位置へ戻る。"""
        if self.trail:
            self.x, self.y = self.trail[0]  # trail[0] は出発BORDERセル
        field.cancel_trail()
        self.trail = []
        self.state = PlayerState.ON_BORDER
