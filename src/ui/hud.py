import pyxel

from game.score import ScoreBoard
from game.constants import (
    SCREEN_W,
    HUD_Y,
    HUD_H,
    ENERGY_MAX,
    CHAR_W,
    COL_DARK_GREY,
    COL_WHITE,
    COL_LIME,
    COL_YELLOW,
    COL_RED,
)

# エネルギーゲージ配置
_GAUGE_LABEL_X = 2
_GAUGE_X = 10  # ラベル"E"の右から
_GAUGE_W = 116  # SCREEN_W - _GAUGE_X - 2
_GAUGE_INNER_W = 114  # _GAUGE_W - 2 (枠線分)


def draw_energy_gauge(energy: float) -> None:
    """画面上部(Y=0-7)にエネルギーゲージを描画する。"""
    pyxel.rect(0, 0, SCREEN_W, 8, COL_DARK_GREY)
    pyxel.text(_GAUGE_LABEL_X, 1, "E", COL_WHITE)

    # 外枠
    pyxel.rectb(_GAUGE_X, 1, _GAUGE_W, 6, COL_WHITE)

    # 充填量に応じて色変化
    ratio = energy / ENERGY_MAX
    fill_w = max(0, int(_GAUGE_INNER_W * ratio))
    if fill_w > 0:
        col = COL_LIME if ratio > 0.5 else (COL_YELLOW if ratio > 0.25 else COL_RED)
        pyxel.rect(_GAUGE_X + 1, 2, fill_w, 4, col)


def draw_hud(score: ScoreBoard, claimed_ratio: float) -> None:
    pyxel.rect(0, HUD_Y, SCREEN_W, HUD_H, COL_DARK_GREY)

    pyxel.text(2, HUD_Y + 2, f"SC:{score.score:06d}", COL_WHITE)

    center_text = f"S:{score.stage}"
    cx = (SCREEN_W - len(center_text) * CHAR_W) // 2
    pyxel.text(cx, HUD_Y + 2, center_text, COL_LIME)

    ratio_text = f"{claimed_ratio * 100:4.1f}%"
    rx = SCREEN_W - len(ratio_text) * CHAR_W - 2
    pyxel.text(rx, HUD_Y + 2, ratio_text, COL_YELLOW)
