from collections import deque
from typing import TypeVar

T = TypeVar("T")


def flood_fill(
    grid: list[list[T]],
    start_x: int,
    start_y: int,
    target_value: T,
    width: int,
    height: int,
) -> list[tuple[int, int]]:
    """BFS flood fill。start から target_value に一致する連結成分を返す。"""
    if grid[start_y][start_x] != target_value:
        return []
    visited: list[tuple[int, int]] = []
    queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
    seen: set[tuple[int, int]] = {(start_x, start_y)}
    while queue:
        x, y = queue.popleft()
        visited.append((x, y))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and (nx, ny) not in seen
                and grid[ny][nx] == target_value
            ):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return visited


def segments_intersect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    p4: tuple[float, float],
) -> bool:
    """2線分(p1-p2 と p3-p4)の交差判定。端点接触・重複も交差とみなす。

    アルゴリズム: 外積(クロス積)による符号判定
      cross(o, a, b) はベクトル(o→a)と(o→b)の外積を返す。
      正なら b は (o→a) の左側、負なら右側、0なら同一直線上にある。

      d1 = p1 が直線p3-p4に対してどちら側か
      d2 = p2 が直線p3-p4に対してどちら側か
      d3 = p3 が直線p1-p2に対してどちら側か
      d4 = p4 が直線p1-p2に対してどちら側か

      d1とd2の符号が逆 → p1とp2が直線p3-p4を挟んでいる
      d3とd4の符号が逆 → p3とp4が直線p1-p2を挟んでいる
      両方成立すれば2線分は交差している。
    """
    def cross(o: tuple, a: tuple, b: tuple) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def on_segment(p: tuple, a: tuple, b: tuple) -> bool:
        return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and
                min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))

    # p1,p2 それぞれが直線p3-p4のどちら側にあるか
    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    # p3,p4 それぞれが直線p1-p2のどちら側にあるか
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    # 通常交差: 両線分が互いに相手の直線を挟んでいる
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # 端点が相手の線分上にある場合(外積=0は同一直線上)
    if d1 == 0 and on_segment(p1, p3, p4):
        return True
    if d2 == 0 and on_segment(p2, p3, p4):
        return True
    if d3 == 0 and on_segment(p3, p1, p2):
        return True
    if d4 == 0 and on_segment(p4, p1, p2):
        return True

    return False
