from enum import IntEnum

from game.constants import FIELD_W, FIELD_H
from utils.geometry import flood_fill


class CellType(IntEnum):
    UNCLAIMED = 0
    CLAIMED = 1
    BORDER = 2
    TRAIL = 3


class Field:
    def __init__(self, width: int = FIELD_W, height: int = FIELD_H) -> None:
        self.width = width
        self.height = height
        self.grid: list[list[CellType]] = self._init_grid()
        self.claimed_ratio: float = 0.0
        self._update_ratio()

    def _init_grid(self) -> list[list[CellType]]:
        grid: list[list[CellType]] = []
        for y in range(self.height):
            row: list[CellType] = []
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(CellType.BORDER)
                else:
                    row.append(CellType.UNCLAIMED)
            grid.append(row)
        return grid

    def is_border(self, x: int, y: int) -> bool:
        return self.grid[y][x] == CellType.BORDER

    def do_trail(self, x: int, y: int) -> None:
        self.grid[y][x] = CellType.TRAIL

    def complete_trail(
        self, drift_positions: list[tuple[float, float]]
    ) -> tuple[int, int, int]:
        """Trail完成処理。(通常確保セル数, Drift側セル数, Trail長) を返す。"""
        # 1. Trail長をカウントしてからBORDERに変換
        trail_length = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.TRAIL:
                    trail_length += 1
                    self.grid[y][x] = CellType.BORDER

        # 2. 全UNCLAIMED連結成分を列挙
        components: list[list[tuple[int, int]]] = []
        visited: set[tuple[int, int]] = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.UNCLAIMED and (x, y) not in visited:
                    comp = flood_fill(
                        self.grid, x, y, CellType.UNCLAIMED, self.width, self.height
                    )
                    visited.update(comp)
                    components.append(comp)

        if not components:
            self._update_ratio()
            return 0, 0, trail_length

        normal_cells = 0
        drift_side_cells = 0

        if drift_positions:
            cell_to_comp: dict[tuple[int, int], int] = {}
            for i, comp in enumerate(components):
                for cell in comp:
                    cell_to_comp[cell] = i

            drift_comp_indices: set[int] = set()
            for fx, fy in drift_positions:
                gx, gy = int(fx), int(fy)
                # float→int変換でBORDER/CLAIMEDにマップされる場合に備えて近傍8セルも探索
                idx = cell_to_comp.get((gx, gy))
                if idx is None:
                    for dx, dy in (
                        (1, 0),
                        (-1, 0),
                        (0, 1),
                        (0, -1),
                        (1, 1),
                        (-1, 1),
                        (1, -1),
                        (-1, -1),
                    ):
                        idx = cell_to_comp.get((gx + dx, gy + dy))
                        if idx is not None:
                            break
                if idx is not None:
                    drift_comp_indices.add(idx)

            for i, comp in enumerate(components):
                if i in drift_comp_indices:
                    drift_side_cells += len(comp)
                else:
                    normal_cells += len(comp)
                    for cx, cy in comp:
                        self.grid[cy][cx] = CellType.CLAIMED
        else:
            # Drift がいないとき: Trail が領域を分断した場合、最大成分だけ残す。
            # 最大成分 = フィールド外周(BORDER)の外側とつながる「まだ確保していない広い領域」。
            # 小さい成分 = Trail で囲まれた内側の領域 → CLAIMED に変換して確保する。
            if len(components) >= 2:
                largest_idx = max(
                    range(len(components)), key=lambda i: len(components[i])
                )
                for i, comp in enumerate(components):
                    if i != largest_idx:
                        normal_cells += len(comp)
                        for cx, cy in comp:
                            self.grid[cy][cx] = CellType.CLAIMED

        self._update_ratio()
        return normal_cells, drift_side_cells, trail_length

    def cancel_trail(self) -> None:
        """ミス時にTrailをUNCLAIMEDに戻す。"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.TRAIL:
                    self.grid[y][x] = CellType.UNCLAIMED

    def _update_ratio(self) -> None:
        total = self.width * self.height
        claimed = sum(
            1
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] in (CellType.CLAIMED, CellType.BORDER)
        )
        self.claimed_ratio = claimed / total
