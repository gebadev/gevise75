import math
import random

from game.field import Field, CellType
from utils.geometry import segments_intersect

_VERTEX_COUNT = 5
_DRAW_RADIUS = 5


class Drift:
    def __init__(self, x: float, y: float, vx: float, vy: float, speed: float) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self._phase: float = random.uniform(0, math.pi * 2)
        self._prev_x: float = x
        self._prev_y: float = y

    @classmethod
    def create(cls, field: Field, speed: float = 1.5) -> "Drift":
        """UNCLAIMEDエリアのランダム位置に Drift を生成して返す。

        @classmethod にしているのは、生成に field の情報が必要で、
        コンストラクタ(__init__)に複雑なロジックを書くのを避けるため。
        cls(...) は self.__class__(...) と同義で、インスタンスを返す。
        """
        for _ in range(1000):
            cx = random.randint(20, field.width - 20)
            cy = random.randint(20, field.height - 20)
            if field.grid[cy][cx] == CellType.UNCLAIMED:
                x, y = cx, cy
                break
        else:
            # ランダム探索が外れた場合、全UNCLAIMED セルから直接選択
            unclaimed = [
                (cx, cy)
                for cy in range(field.height)
                for cx in range(field.width)
                if field.grid[cy][cx] == CellType.UNCLAIMED
            ]
            x, y = random.choice(unclaimed) if unclaimed else (field.width // 2, field.height // 2)
        angle = random.uniform(0, math.pi * 2)
        return cls(
            x=float(x),
            y=float(y),
            vx=math.cos(angle),
            vy=math.sin(angle),
            speed=speed,
        )

    def update(self, field: Field) -> None:
        self._prev_x = self.x
        self._prev_y = self.y
        # サブステップ: speed が 1px を超えると1フレームで複数セルを飛び越し
        # 壁をすり抜ける「トンネリング」が起きる。1サブステップを1px以下に
        # 分割することで、毎ステップ確実に衝突判定できるようにする。
        steps = math.ceil(self.speed)
        sub_speed = self.speed / steps
        for _ in range(steps):
            nx = self.x + self.vx * sub_speed
            ny = self.y + self.vy * sub_speed

            # x方向の反射: x だけ動かしたとき壁に入るか確認する。
            # y は self.y(現在値)を使い、x方向の衝突のみを独立して判定する。
            gx = int(nx)
            gy = int(self.y)
            if (not (0 <= gx < field.width and 0 <= gy < field.height)
                    or field.grid[gy][gx] in (CellType.BORDER, CellType.CLAIMED)):
                self.vx = -self.vx
                nx = self.x + self.vx * sub_speed

            # y方向の反射: x方向の結果(nx)を踏まえて y の衝突を判定する。
            # x と y を独立して処理することでコーナーでも安定して反射できる。
            gx2 = int(nx)
            gy2 = int(ny)
            if (not (0 <= gx2 < field.width and 0 <= gy2 < field.height)
                    or field.grid[gy2][gx2] in (CellType.BORDER, CellType.CLAIMED)):
                self.vy = -self.vy
                ny = self.y + self.vy * sub_speed

            self.x = nx
            self.y = ny
        self._phase += 0.08

    def collides_with_trail(self, trail: list[tuple[int, int]]) -> bool:
        """Driftの移動線分とTrailセグメントの交差判定。"""
        if len(trail) < 2:
            return False
        p1 = (self._prev_x, self._prev_y)
        p2 = (self.x, self.y)
        for i in range(len(trail) - 1):
            p3 = (float(trail[i][0]), float(trail[i][1]))
            p4 = (float(trail[i + 1][0]), float(trail[i + 1][1]))
            if segments_intersect(p1, p2, p3, p4):
                return True
        return False

    def vertices(self) -> list[tuple[float, float]]:
        """描画用ポリゴン頂点リストを返す。"""
        pts: list[tuple[float, float]] = []
        for i in range(_VERTEX_COUNT):
            a = self._phase + i * (math.pi * 2 / _VERTEX_COUNT)
            pts.append((self.x + math.cos(a) * _DRAW_RADIUS,
                        self.y + math.sin(a) * _DRAW_RADIUS))
        return pts
