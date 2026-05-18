import pyxel

from game.score import ScoreBoard
from game.constants import (
    COL_BLACK,
    COL_WHITE,
    COL_BLUE,
    COL_RED,
    SCREEN_W,
    SCREEN_H,
    CHAR_W,
    TITLE,
)


def draw_title_screen() -> None:
    pyxel.cls(COL_BLACK)

    title = " ".join(TITLE)
    _draw_centered(title, SCREEN_H // 2 - 20, COL_BLUE)

    if (pyxel.frame_count // 15) % 2 == 0:
        _draw_centered("PRESS Z TO START", SCREEN_H // 2 + 16, COL_WHITE)


def draw_game_over_screen(score: ScoreBoard) -> None:
    pyxel.cls(COL_BLACK)
    _draw_centered("GAME OVER", SCREEN_H // 2 - 20, COL_RED)
    _draw_centered(f"SCORE: {score.score:06d}", SCREEN_H // 2 - 4, COL_WHITE)
    if (pyxel.frame_count // 15) % 2 == 0:
        _draw_centered("PRESS Z", SCREEN_H // 2 + 16, COL_WHITE)


def _draw_centered(text: str, y: int, col: int) -> None:
    x = (SCREEN_W - len(text) * CHAR_W) // 2
    pyxel.text(x, y, text, col)
