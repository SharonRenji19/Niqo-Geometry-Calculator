"""A circle defined by a center Point and a radius."""

import math

from .point import Point, _fmt
from .shape import Shape


class Circle(Shape):
    def __init__(self, center: Point, radius: float):
        if not isinstance(center, Point):
            raise TypeError("Circle requires a Point as its center")
        radius = float(radius)
        if radius <= 0:
            raise ValueError("Circle radius must be positive")
        self.center = center
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

    def distance(self, other: "Shape") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .line import Line
        from .rectangle import Rectangle

        if isinstance(other, Point):
            return self._distance_to_point(other)
        if isinstance(other, Circle):
            return self._distance_to_circle(other)
        if isinstance(other, Line):
            return self._distance_to_line(other)
        if isinstance(other, Rectangle):
            # Rectangle implements the Circle case explicitly, so this
            # delegation is safe and won't bounce back and forth.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Circle and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point) -> float:
        center_dist = self.center.distance(point)
        # 0 whenever the point is inside or on the circle, not negative.
        return max(0.0, center_dist - self.radius)

    def _distance_to_circle(self, other: "Circle") -> float:
        center_dist = self.center.distance(other.center)
        # 0 if the circles touch or overlap (including one fully inside the other).
        return max(0.0, center_dist - self.radius - other.radius)

    def _distance_to_line(self, line) -> float:
        # Line already computes point-to-segment distance; reuse it for the
        # center, then subtract the radius (clamped at 0 if they overlap).
        center_dist = line._distance_to_point(self.center)
        return max(0.0, center_dist - self.radius)

    def __repr__(self) -> str:
        return f"(center={self.center!r}, r={_fmt(self.radius)})"
