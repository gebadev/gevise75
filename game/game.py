from enum import Enum, auto

import pyxel

from game.audio import (
    play_bgm,
    play_game_over_sfx,
    play_miss_sfx,
    play_stage_clear_sfx,
    play_trail_success_sfx,
    stop_bgm,
)
from game.field import Field
from game.player import Player, PlayerResult, PlayerState
from game.drift import Drift
from game.crawler import Crawler
from game.score import ScoreBoard
from game.constants import (
    CLEAR_RATIO,
    INITIAL_CRAWLERS,
    ENERGY_TRAIL_K,
    ENERGY_TRAIL_N,
    DRIFT_COUNT_MAX,
    DRIFT_COUNT_STAGE_INTERVAL,
    DRIFT_SPEED_BASE,
    DRIFT_SPEED_MAX,
    DRIFT_SPEED_STAGE_INC,
    CRAWLER_INTERVAL_MIN_BASE,
    CRAWLER_INTERVAL_MAX_BASE,
    CRAWLER_INTERVAL_MIN_FLOOR,
    CRAWLER_INTERVAL_MAX_FLOOR,
    COL_BLACK,
    COL_PEACH,
    COL_RED,
    COL_WHITE,
    COL_YELLOW,
)
from ui.renderer import draw_field, draw_player, draw_drift, draw_crawler
from ui.hud import draw_hud, draw_energy_gauge
from ui.screens import draw_title_screen, draw_game_over_screen

_MISS_DURATION = 15       # 0.5秒（30FPS）
_INVINCIBLE_DURATION = 60  # 2秒（ミス後無敵）
_START_BLINK_DURATION = 60  # 2秒（ゲーム開始時白黒ブリンク）


class GameState(Enum):
    TITLE = auto()
    PLAYING = auto()
    MISS = auto()
    STAGE_CLEAR = auto()
    GAME_OVER = auto()


class Game:
    def __init__(self) -> None:
        self.current_state = GameState.TITLE
        self._field = Field()
        self._player = Player()
        self._score = ScoreBoard()
        self._drifts: list[Drift] = []
        self._crawlers: list[Crawler] = []
        self._miss_timer: int = 0
        self._invincible_timer: int = 0
        self._start_blink_timer: int = 0

    def _setup_stage(self) -> None:
        """現在のステージ番号に基づいてフィールド・プレイヤー・敵を初期化する。"""
        self._field = Field()
        self._player = Player()
        stage = self._score.stage
        drift_count = min(
            DRIFT_COUNT_MAX,
            1 + (stage - 1) // DRIFT_COUNT_STAGE_INTERVAL,
        )
        drift_speed = min(
            DRIFT_SPEED_MAX,
            DRIFT_SPEED_BASE + (stage - 1) * DRIFT_SPEED_STAGE_INC,
        )
        self._drifts = [
            Drift.create(self._field, speed=drift_speed)
            for _ in range(drift_count)
        ]
        crawler_count = INITIAL_CRAWLERS + (stage - 1)
        min_interval = max(CRAWLER_INTERVAL_MIN_FLOOR, CRAWLER_INTERVAL_MIN_BASE - (stage - 1))
        max_interval = max(CRAWLER_INTERVAL_MAX_FLOOR, CRAWLER_INTERVAL_MAX_BASE - (stage - 1))
        player_pos = (self._player.x, self._player.y)
        self._crawlers = [
            Crawler.create(
                self._field,
                speed_interval_range=(min_interval, max_interval),
                avoid_pos=player_pos,
            )
            for _ in range(crawler_count)
        ]
        self._start_blink_timer = _START_BLINK_DURATION

    def update(self) -> None:
        if self.current_state == GameState.TITLE:
            self._update_title()
        elif self.current_state == GameState.PLAYING:
            self._update_playing()
        elif self.current_state == GameState.MISS:
            self._update_miss()
        elif self.current_state == GameState.STAGE_CLEAR:
            self._update_stage_clear()
        elif self.current_state == GameState.GAME_OVER:
            self._update_game_over()

    def draw(self) -> None:
        if self.current_state == GameState.TITLE:
            draw_title_screen()
        elif self.current_state == GameState.PLAYING:
            self._draw_playing()
        elif self.current_state == GameState.MISS:
            self._draw_miss()
        elif self.current_state == GameState.STAGE_CLEAR:
            self._draw_stage_clear()
        elif self.current_state == GameState.GAME_OVER:
            draw_game_over_screen(self._score)

    def _update_title(self) -> None:
        if pyxel.btnp(pyxel.KEY_Z):
            self._score = ScoreBoard()
            self._setup_stage()
            self.current_state = GameState.PLAYING

    def _update_playing(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            self.current_state = GameState.TITLE
            return

        if self._start_blink_timer > 0:
            moving = (
                pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_RIGHT)
                or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_DOWN)
            )
            if moving:
                self._start_blink_timer = 0
            else:
                self._start_blink_timer -= 1

        # エネルギー自然減少（0になったら即ゲームオーバー）
        is_drawing = self._player.state == PlayerState.DRAWING
        if not self._score.decay_energy(self._score.stage, is_drawing):
            self._enter_game_over()
            return

        if self._invincible_timer > 0:
            self._invincible_timer -= 1

        # Drift更新と Trail 衝突判定（無敵中はスキップ）
        for drift in self._drifts:
            drift.update(self._field)
            if (
                self._invincible_timer == 0
                and self._player.state == PlayerState.DRAWING
                and drift.collides_with_trail(self._player.trail)
            ):
                self._enter_miss()
                return

        # Crawler更新と Player 衝突判定（無敵中はスキップ）
        for crawler in self._crawlers:
            crawler.update(self._field)
            if self._invincible_timer == 0 and crawler.collides_with_player(
                self._player.x, self._player.y
            ):
                self._enter_miss()
                return

        result = self._player.update(self._field)

        if result == PlayerResult.MISS:
            self._enter_miss()
            return

        # プレイヤー移動後にCrawlerの位置へ入ったケースの衝突判定
        if self._invincible_timer == 0:
            for crawler in self._crawlers:
                if crawler.collides_with_player(self._player.x, self._player.y):
                    self._enter_miss()
                    return

        if result == PlayerResult.TRAIL_COMPLETE:
            drift_positions = [(d.x, d.y) for d in self._drifts]
            normal_cells, _drift_cells, trail_len = self._field.complete_trail(
                drift_positions
            )
            play_trail_success_sfx()
            self._score.add_claimed(normal_cells, drift_side=False)

            if trail_len > 0:
                self._score.restore_energy(ENERGY_TRAIL_K * (trail_len**ENERGY_TRAIL_N))

            if self._field.claimed_ratio >= CLEAR_RATIO:
                play_stage_clear_sfx()
                self.current_state = GameState.STAGE_CLEAR

    def _enter_miss(self) -> None:
        """ミス演出開始。即座にエネルギーペナルティを適用する。"""
        play_miss_sfx()
        self._score.take_hit()
        self._miss_timer = _MISS_DURATION
        self.current_state = GameState.MISS

    def _update_miss(self) -> None:
        self._miss_timer -= 1
        if self._miss_timer <= 0:
            self._player.cancel_trail(self._field)
            if self._score.energy <= 0:
                self._enter_game_over()
            else:
                self._invincible_timer = _INVINCIBLE_DURATION
                self.current_state = GameState.PLAYING

    def _update_stage_clear(self) -> None:
        if pyxel.btnp(pyxel.KEY_Z):
            self._score.next_stage()  # エネルギーボーナス込み
            self._setup_stage()
            self.current_state = GameState.PLAYING

    def _update_game_over(self) -> None:
        if pyxel.btnp(pyxel.KEY_Z):
            self.current_state = GameState.TITLE
            play_bgm()

    def _enter_game_over(self) -> None:
        stop_bgm()
        play_game_over_sfx()
        self.current_state = GameState.GAME_OVER

    def _draw_game_scene(self) -> None:
        pyxel.cls(0)
        draw_energy_gauge(self._score.energy)
        draw_field(self._field)
        draw_hud(self._score, self._field.claimed_ratio)
        for drift in self._drifts:
            draw_drift(drift)
        for crawler in self._crawlers:
            draw_crawler(crawler)

    def _draw_playing(self) -> None:
        self._draw_game_scene()
        if self._start_blink_timer > 0:
            elapsed = _START_BLINK_DURATION - self._start_blink_timer
            # 点滅パターン: (経過フレーム // N) % 2 == 0 が True/False を交互に返す。
            # N を大きくするほどゆっくり点滅する。
            col = COL_WHITE if (elapsed // 3) % 2 == 0 else COL_BLACK
            draw_player(self._player, col)
        elif self._invincible_timer == 0 or (pyxel.frame_count // 4) % 2 == 0:
            # 無敵中は4フレーム周期で点滅(同じ点滅パターンを使用)
            draw_player(self._player)

    def _draw_stage_clear(self) -> None:
        self._draw_playing()
        cx = pyxel.width // 2
        if (pyxel.frame_count // 15) % 2 == 0:
            clear_text = f"STAGE {self._score.stage} CLEAR!"
            pyxel.text(cx - 27, 53, clear_text, COL_BLACK)
            pyxel.text(cx - 28, 52, clear_text, COL_PEACH)
        pyxel.text(cx - 26, 64, f"SCORE: {self._score.score:06d}", COL_WHITE)
        if (pyxel.frame_count // 15) % 2 == 0:
            press_text = "PRESS Z"
            pyxel.text(cx - len(press_text) * 2, 78, press_text, COL_YELLOW)

    def _draw_miss(self) -> None:
        self._draw_game_scene()
        # プレイヤーを4フレーム周期で点滅
        if (pyxel.frame_count // 4) % 2 == 0:
            draw_player(self._player)
