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
        if isinstance(other, Point):
            return self._distance_to_point(other)
        if isinstance(other, Circle):
            return self._distance_to_circle(other)
        # Line/Rectangle cases are added once those shapes exist; delegate
        # to the other shape's implementation if it knows how to handle us.
        if hasattr(other, "distance"):
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

    def __repr__(self) -> str:
        return f"(center={self.center!r}, r={_fmt(self.radius)})"
