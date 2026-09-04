"""A single (x, y, z) location in 3D space."""

import math

from .shape3d import Shape3D


class Point3D(Shape3D):
    def __init__(self, x: float, y: float, z: float):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def area(self) -> float:
        return 0.0

    def volume(self) -> float:
        return 0.0

    def distance(self, other: "Shape3D") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .line3d import Line3D
        from .sphere import Sphere
        from .box import Box

        if isinstance(other, Point3D):
            return math.hypot(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, (Line3D, Sphere, Box)):
            # These shapes already know how to measure distance to a point;
            # reuse that logic instead of duplicating it here.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Point3D and {type(other).__name__}"
        )

    def contains(self, point: "Point3D") -> bool:
        return isinstance(point, Point3D) and self == point

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point3D):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y) and math.isclose(self.z, other.z)

    def __repr__(self) -> str:
        return f"({_fmt(self.x)}, {_fmt(self.y)}, {_fmt(self.z)})"


def _fmt(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.10g}"
