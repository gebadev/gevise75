from game.constants import (
    ENERGY_MAX, ENERGY_DECAY, ENERGY_MISS_PENALTY, ENERGY_CLEAR_BONUS,
    ENERGY_DECAY_STAGE_SCALE, ENERGY_DECAY_DRAWING_MULT,
)


class ScoreBoard:
    def __init__(self) -> None:
        self.score: int = 0
        self.energy: float = ENERGY_MAX
        self.stage: int = 1

    def add_claimed(self, cells: int, drift_side: bool = False) -> None:
        multiplier = 2 if drift_side else 1
        self.score += cells * multiplier

    def decay_energy(self, stage: int = 1, is_drawing: bool = False) -> bool:
        """毎フレーム自然減少。エネルギー切れで False を返す。"""
        decay = ENERGY_DECAY * (1 + (stage - 1) * ENERGY_DECAY_STAGE_SCALE)
        if is_drawing:
            decay *= ENERGY_DECAY_DRAWING_MULT
        self.energy = max(0.0, self.energy - decay)
        return self.energy > 0

    def take_hit(self) -> None:
        """衝突ペナルティ。"""
        self.energy = max(0.0, self.energy - ENERGY_MISS_PENALTY)

    def restore_energy(self, amount: float) -> None:
        self.energy = min(ENERGY_MAX, self.energy + amount)

    def next_stage(self) -> None:
        """ステージを進める。クリアボーナスを加算してエネルギーを引き継ぐ。"""
        self.stage += 1
        self.restore_energy(ENERGY_CLEAR_BONUS)
