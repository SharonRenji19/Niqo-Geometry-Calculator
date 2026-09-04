"""A sphere defined by a center Point3D and a radius."""

import math

from .point3d import Point3D, _fmt
from .shape3d import Shape3D


class Sphere(Shape3D):
    def __init__(self, center: Point3D, radius: float):
        if not isinstance(center, Point3D):
            raise TypeError("Sphere requires a Point3D as its center")
        radius = float(radius)
        if radius <= 0:
            raise ValueError("Sphere radius must be positive")
        self.center = center
        self.radius = radius

    def area(self) -> float:
        # Surface area.
        return 4 * math.pi * self.radius ** 2

    def volume(self) -> float:
        return (4 / 3) * math.pi * self.radius ** 3

    def distance(self, other: "Shape3D") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .line3d import Line3D
        from .box import Box

        if isinstance(other, Point3D):
            return self._distance_to_point(other)
        if isinstance(other, Sphere):
            return self._distance_to_sphere(other)
        if isinstance(other, Line3D):
            return self._distance_to_line(other)
        if isinstance(other, Box):
            # Box implements the Sphere case explicitly, so delegating here
            # is safe and won't bounce back and forth.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Sphere and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point3D) -> float:
        return max(0.0, self.center.distance(point) - self.radius)

    def _distance_to_sphere(self, other: "Sphere") -> float:
        center_dist = self.center.distance(other.center)
        return max(0.0, center_dist - self.radius - other.radius)

    def _distance_to_line(self, line) -> float:
        center_dist = line._distance_to_point(self.center)
        return max(0.0, center_dist - self.radius)

    def contains(self, point: Point3D) -> bool:
        return self.center.distance(point) <= self.radius + 1e-9

    def __repr__(self) -> str:
        return f"(center={self.center!r}, r={_fmt(self.radius)})"
