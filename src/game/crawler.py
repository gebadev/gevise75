import random

from game.field import Field, CellType

# 時計回りに並べた4方向。インデックスで方向を管理する。
# dir_idx を +1 すると右折、+2 で反転、+3(=-1) で左折になる。
_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # R, D, L, U


class Crawler:
    def __init__(self, x: int, y: int, dir_idx: int, speed_interval: int) -> None:
        self.x = x
        self.y = y
        self.dir_idx = dir_idx
        self.speed_interval = speed_interval
        self._frame: int = 0

    @classmethod
    def create(
        cls,
        fld: Field,
        speed_interval_range: tuple[int, int] = (5, 8),
        avoid_pos: tuple[int, int] | None = None,
        min_dist: int = 30,
    ) -> "Crawler":
        """BORDERセル上のランダム位置に Crawler を生成して返す。

        @classmethod にしているのは、生成に field の情報が必要で、
        コンストラクタ(__init__)に複雑なロジックを書くのを避けるため。
        """
        border_cells = [
            (x, y)
            for y in range(fld.height)
            for x in range(fld.width)
            if fld.grid[y][x] == CellType.BORDER
        ]
        if avoid_pos is not None:
            px, py = avoid_pos
            far = [(x, y) for x, y in border_cells if abs(x - px) + abs(y - py) >= min_dist]
            if far:
                border_cells = far
        x, y = random.choice(border_cells)
        interval = random.randint(*speed_interval_range)
        return cls(x=x, y=y, dir_idx=random.randint(0, 3), speed_interval=interval)

    def update(self, field: Field) -> None:
        self._frame += 1
        if self._frame < self.speed_interval:
            return
        self._frame = 0
        self._step(field)

    def _step(self, field: Field) -> None:
        # +2 は _DIRS 配列で半周分ずらすと真逆の方向になる（例: R(0) → L(2)）
        reverse_dir = (self.dir_idx + 2) % 4
        candidates = []
        # turn=0: 直進(+0), turn=1: 右折(+1), turn=3: 左折(+3 ≡ -1 mod 4)
        for turn in [0, 1, 3]:  # straight, right, left
            new_dir = (self.dir_idx + turn) % 4
            dx, dy = _DIRS[new_dir]
            nx, ny = self.x + dx, self.y + dy
            if (0 <= nx < field.width and 0 <= ny < field.height
                    and field.grid[ny][nx] == CellType.BORDER):
                candidates.append((nx, ny, new_dir))

        if candidates:
            # 分岐点（2方向以上）ではランダム選択、一本道では直進
            nx, ny, new_dir = candidates[0] if len(candidates) == 1 \
                else random.choice(candidates)
            self.x, self.y = nx, ny
            self.dir_idx = new_dir
            return

        # 行き止まり: 反転
        dx, dy = _DIRS[reverse_dir]
        nx, ny = self.x + dx, self.y + dy
        if (0 <= nx < field.width and 0 <= ny < field.height
                and field.grid[ny][nx] == CellType.BORDER):
            self.x, self.y = nx, ny
            self.dir_idx = reverse_dir

    def collides_with_player(self, px: int, py: int) -> bool:
        return self.x == px and self.y == py
