"""An axis-aligned rectangle, defined by two opposite corner Points."""

from .point import Point, _fmt
from .shape import Shape


class Rectangle(Shape):
    def __init__(self, corner1: Point, corner2: Point):
        if not isinstance(corner1, Point) or not isinstance(corner2, Point):
            raise TypeError("Rectangle requires two Point instances")
        if corner1.x == corner2.x or corner1.y == corner2.y:
            raise ValueError(
                "Rectangle corners must differ in both x and y (zero width/height)"
            )
        # Normalize so min_x/min_y is always the bottom-left corner, regardless
        # of which two opposite corners the caller passed in.
        self.min_x = min(corner1.x, corner2.x)
        self.max_x = max(corner1.x, corner2.x)
        self.min_y = min(corner1.y, corner2.y)
        self.max_y = max(corner1.y, corner2.y)

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def distance(self, other: "Shape") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .circle import Circle
        from .line import Line

        if isinstance(other, Point):
            return self._distance_to_point(other)
        if isinstance(other, Rectangle):
            return self._distance_to_rectangle(other)
        if isinstance(other, Circle):
            return self._distance_to_circle(other)
        if isinstance(other, Line):
            return self._distance_to_line(other)
        raise TypeError(
            f"Cannot compute distance between Rectangle and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point) -> float:
        # Clamp the point onto the rectangle's box; 0 if the point is inside.
        dx = max(self.min_x - point.x, 0.0, point.x - self.max_x)
        dy = max(self.min_y - point.y, 0.0, point.y - self.max_y)
        return (dx ** 2 + dy ** 2) ** 0.5

    def _distance_to_rectangle(self, other: "Rectangle") -> float:
        # Standard AABB-to-AABB distance: overlap in an axis contributes 0
        # to that axis's gap; otherwise it's the gap between the boxes.
        dx = max(self.min_x - other.max_x, other.min_x - self.max_x, 0.0)
        dy = max(self.min_y - other.max_y, other.min_y - self.max_y, 0.0)
        return (dx ** 2 + dy ** 2) ** 0.5

    def _distance_to_circle(self, circle) -> float:
        center_dist = self._distance_to_point(circle.center)
        return max(0.0, center_dist - circle.radius)

    def _distance_to_line(self, line) -> float:
        from .line import Line

        if self.contains(line.p1) or self.contains(line.p2):
            return 0.0

        corners = [
            Point(self.min_x, self.min_y),
            Point(self.max_x, self.min_y),
            Point(self.max_x, self.max_y),
            Point(self.min_x, self.max_y),
        ]
        edges = [Line(corners[i], corners[(i + 1) % 4]) for i in range(4)]

        if any(edge._segments_intersect(line) for edge in edges):
            return 0.0

        candidates = [edge._distance_to_point(line.p1) for edge in edges]
        candidates += [edge._distance_to_point(line.p2) for edge in edges]
        candidates += [line._distance_to_point(corner) for corner in corners]
        return min(candidates)

    def contains(self, point: Point) -> bool:
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def __repr__(self) -> str:
        return (
            f"(x: {_fmt(self.min_x)}..{_fmt(self.max_x)}, "
            f"y: {_fmt(self.min_y)}..{_fmt(self.max_y)})"
        )
