"""A single (x, y) location in 2D space."""

import math

from .shape import Shape


class Point(Shape):
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def area(self) -> float:
        # A point encloses no area.
        return 0.0

    def perimeter(self) -> float:
        # A point has no boundary length.
        return 0.0

    def distance(self, other: "Shape") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .line import Line
        from .circle import Circle

        if isinstance(other, Point):
            return math.hypot(self.x - other.x, self.y - other.y)
        if isinstance(other, (Line, Circle)):
            # Line and Circle already know how to measure distance to a
            # point; reuse that logic instead of duplicating it here.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Point and {type(other).__name__}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __repr__(self) -> str:
        return f"({_fmt(self.x)}, {_fmt(self.y)})"


def _fmt(value: float) -> str:
    """Print '10' instead of '10.0', but keep decimals when they matter."""
    if value == int(value):
        return str(int(value))
    return f"{value:.10g}"
