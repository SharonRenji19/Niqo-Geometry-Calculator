"""Intersection of two shapes: the single region covered by both of them."""

import math

from . import _overlap
from .circle import Circle
from .point import Point
from .rectangle import Rectangle
from .shape import Shape


class Intersection(Shape):
    """The shape formed by the overlap of two shapes ("A and B").

    An ``Intersection`` is itself a ``Shape``, so it supports the same
    ``area()`` / ``perimeter()`` / ``distance(other)`` interface as every
    other shape, and — because of that — can be nested inside a ``Union``
    or another ``Intersection`` just like any other shape.

    See ``shapes/_overlap.py`` for how the overlap area/perimeter is
    actually computed (exact for most shape pairs, Monte Carlo
    approximated for Circle-Rectangle area).
    """

    def __init__(self, shape_a: Shape, shape_b: Shape):
        if not isinstance(shape_a, Shape) or not isinstance(shape_b, Shape):
            raise TypeError("Intersection requires two Shape instances")
        self.shape_a = shape_a
        self.shape_b = shape_b

    # ---- Shape interface ------------------------------------------------

    def area(self) -> float:
        return _overlap.intersection_area(self.shape_a, self.shape_b)

    def perimeter(self) -> float:
        a, b = self.shape_a, self.shape_b

        # Full containment is cheap and exact for every shape-pair combo:
        # the intersection is simply the smaller (fully-swallowed) shape.
        if _overlap.fully_contains(a, b):
            return b.perimeter()
        if _overlap.fully_contains(b, a):
            return a.perimeter()

        if self.area() == 0.0:
            # No overlap (or the overlap is a zero-area Point/Line/edge
            # touch) -> an empty or degenerate region has no boundary.
            return 0.0
        if isinstance(a, Circle) and isinstance(b, Circle):
            return _overlap.circle_circle_intersection_perimeter(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Rectangle):
            return _overlap.rectangle_rectangle_intersection_perimeter(a, b)
        if isinstance(a, Circle) and isinstance(b, Rectangle):
            return _overlap.circle_rectangle_intersection_perimeter(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Circle):
            return _overlap.circle_rectangle_intersection_perimeter(b, a)

        raise NotImplementedError(
            f"Intersection.perimeter() doesn't know how to overlap "
            f"{type(a).__name__} and {type(b).__name__}"
        )

    def distance(self, other: "Shape") -> float:
        a, b = self.shape_a, self.shape_b

        # Full containment -> the intersection *is* the smaller shape, so
        # its distance to a third shape is just that shape's own distance.
        if _overlap.fully_contains(a, b):
            return b.distance(other)
        if _overlap.fully_contains(b, a):
            return a.distance(other)

        if self.area() == 0.0 and not self._touches():
            # The two shapes don't even meet, so their intersection is the
            # empty set. Distance from an empty region is conventionally
            # taken as infinite (there's no point in it to measure from).
            return math.inf

        raise NotImplementedError(
            "Intersection.distance(other) isn't supported for a *partial*, "
            "non-empty overlap: finding the closest point of an arbitrary "
            "overlap region to a third shape needs the region's actual "
            "clipped boundary, which this project doesn't construct (see "
            "shapes/_overlap.py — it only computes area/perimeter totals, "
            "not the boundary geometry itself). See the README's 'Known "
            "issues' section."
        )

    def contains(self, point: Point) -> bool:
        return self.shape_a.contains(point) and self.shape_b.contains(point)

    # ---- helpers ----------------------------------------------------------

    def _touches(self) -> bool:
        # Same exact, no-sampling test Union uses for its overlap check.
        return self.shape_a.distance(self.shape_b) <= 1e-9

    def __repr__(self) -> str:
        return f"Intersection({self.shape_a!r}, {self.shape_b!r})"
