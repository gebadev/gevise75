import pyxel

from game.field import Field, CellType
from game.player import Player
from game.drift import Drift
from game.crawler import Crawler
from game.constants import (
    FIELD_OFFSET_X,
    FIELD_OFFSET_Y,
    COL_NAVY,
    COL_LIME,
    COL_YELLOW,
    COL_WHITE,
    COL_RED,
    COL_ORANGE,
)

_CELL_COLORS: dict[CellType, int] = {
    CellType.CLAIMED: COL_NAVY,
    CellType.BORDER: COL_LIME,
    CellType.TRAIL: COL_YELLOW,
}


def draw_field(field: Field) -> None:
    for y in range(field.height):
        for x in range(field.width):
            col = _CELL_COLORS.get(field.grid[y][x])
            if col is not None:
                pyxel.pset(FIELD_OFFSET_X + x, FIELD_OFFSET_Y + y, col)


def draw_player(player: Player, col: int = COL_WHITE) -> None:
    sx = FIELD_OFFSET_X + player.x
    sy = FIELD_OFFSET_Y + player.y
    pyxel.rect(sx - 1, sy - 1, 3, 3, col)


def draw_crawler(crawler: Crawler) -> None:
    sx = FIELD_OFFSET_X + crawler.x
    sy = FIELD_OFFSET_Y + crawler.y
    pyxel.rect(sx - 1, sy - 1, 3, 3, COL_ORANGE)


def draw_drift(drift: Drift) -> None:
    verts = drift.vertices()
    n = len(verts)
    for i in range(n):
        x1 = int(FIELD_OFFSET_X + verts[i][0])
        y1 = int(FIELD_OFFSET_Y + verts[i][1])
        x2 = int(FIELD_OFFSET_X + verts[(i + 1) % n][0])
        y2 = int(FIELD_OFFSET_Y + verts[(i + 1) % n][1])
        pyxel.line(x1, y1, x2, y2, COL_RED)
