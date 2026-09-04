"""A straight segment between two distinct Points."""

import math

from .point import Point, _fmt
from .shape import Shape


class Line(Shape):
    def __init__(self, p1: Point, p2: Point):
        if not isinstance(p1, Point) or not isinstance(p2, Point):
            raise TypeError("Line requires two Point instances")
        if p1 == p2:
            raise ValueError("Line requires two distinct points")
        self.p1 = p1
        self.p2 = p2

    def length(self) -> float:
        return self.p1.distance(self.p2)

    def area(self) -> float:
        # A line segment encloses no area.
        return 0.0

    def perimeter(self) -> float:
        # "Perimeter" of a segment is just its length.
        return self.length()

    def distance(self, other: "Shape") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .circle import Circle
        from .rectangle import Rectangle

        if isinstance(other, Point):
            return self._distance_to_point(other)
        if isinstance(other, Line):
            return self._distance_to_line(other)
        if isinstance(other, (Circle, Rectangle)):
            # Both Circle and Rectangle implement the Line case explicitly,
            # so delegating here is safe and won't bounce back.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Line and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point) -> float:
        """Shortest distance from `point` to this *segment* (not the infinite line)."""
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        px, py = point.x, point.y

        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy

        # Project the point onto the segment, then clamp t to [0, 1] so the
        # closest point is always on the segment itself, not the extended line.
        t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
        t = max(0.0, min(1.0, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(px - closest_x, py - closest_y)

    def _distance_to_line(self, other: "Line") -> float:
        if self._segments_intersect(other):
            return 0.0
        # For non-intersecting segments, the minimum distance is always between
        # one segment's endpoint and the other segment (a standard result for
        # convex shapes like segments), so checking all four endpoint cases
        # is sufficient without a full geometric case analysis.
        candidates = [
            self._distance_to_point(other.p1),
            self._distance_to_point(other.p2),
            other._distance_to_point(self.p1),
            other._distance_to_point(self.p2),
        ]
        return min(candidates)

    def _segments_intersect(self, other: "Line") -> bool:
        def orientation(a: Point, b: Point, c: Point) -> float:
            return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

        def on_segment(a: Point, b: Point, c: Point) -> bool:
            # Is c on segment a-b, given a, b, c are already known collinear?
            return min(a.x, b.x) <= c.x <= max(a.x, b.x) and min(a.y, b.y) <= c.y <= max(a.y, b.y)

        a, b, c, d = self.p1, self.p2, other.p1, other.p2
        o1, o2 = orientation(a, b, c), orientation(a, b, d)
        o3, o4 = orientation(c, d, a), orientation(c, d, b)

        if o1 * o2 < 0 and o3 * o4 < 0:
            return True

        # Collinear edge cases (overlapping / touching endpoints).
        if o1 == 0 and on_segment(a, b, c):
            return True
        if o2 == 0 and on_segment(a, b, d):
            return True
        if o3 == 0 and on_segment(c, d, a):
            return True
        if o4 == 0 and on_segment(c, d, b):
            return True
        return False

    def __repr__(self) -> str:
        return f"[{_fmt(self.p1.x)}, {_fmt(self.p1.y)} -> {_fmt(self.p2.x)}, {_fmt(self.p2.y)}]"
