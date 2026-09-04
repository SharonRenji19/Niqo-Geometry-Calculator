"""Union of two shapes: the single region covered by either one of them."""

from . import _overlap
from .circle import Circle
from .point import Point
from .rectangle import Rectangle
from .shape import Shape


class Union(Shape):
    """The shape formed by combining two shapes into one region ("A or B").

    A ``Union`` is itself a ``Shape``, so it supports the same
    ``area()`` / ``perimeter()`` / ``distance(other)`` interface as
    ``Point``/``Line``/``Circle``/``Rectangle`` — and, because of that, a
    ``Union`` can be nested inside another ``Union`` to combine more than
    two shapes: ``Union(Union(a, b), c)``.

    See ``shapes/_overlap.py`` for how the overlap area/perimeter between
    the two members is actually computed (exact for most shape pairs,
    Monte Carlo approximated for Circle-Rectangle area).
    """

    def __init__(self, shape_a: Shape, shape_b: Shape):
        if not isinstance(shape_a, Shape) or not isinstance(shape_b, Shape):
            raise TypeError("Union requires two Shape instances")
        self.shape_a = shape_a
        self.shape_b = shape_b

    # ---- Shape interface ------------------------------------------------

    def area(self) -> float:
        # Inclusion-exclusion: |A union B| = |A| + |B| - |A intersect B|
        return (
            self.shape_a.area()
            + self.shape_b.area()
            - _overlap.intersection_area(self.shape_a, self.shape_b)
        )

    def perimeter(self) -> float:
        a, b = self.shape_a, self.shape_b

        # Full containment is cheap and exact for every shape-pair combo
        # (no arc-clipping needed): the union is simply the bigger shape.
        if _overlap.fully_contains(a, b):
            return a.perimeter()
        if _overlap.fully_contains(b, a):
            return b.perimeter()

        if _overlap.intersection_area(a, b) == 0.0:
            # No shared *area* -- even if the two shapes touch at a single
            # point or along an edge, that contributes zero boundary
            # length, so a plain sum is still exact.
            return a.perimeter() + b.perimeter()
        if isinstance(a, Circle) and isinstance(b, Circle):
            return _overlap.circle_circle_union_perimeter(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Rectangle):
            return _overlap.rectangle_rectangle_union_perimeter(a, b)
        if isinstance(a, Circle) and isinstance(b, Rectangle):
            return _overlap.circle_rectangle_union_perimeter(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Circle):
            return _overlap.circle_rectangle_union_perimeter(b, a)

        raise NotImplementedError(
            f"Union.perimeter() doesn't know how to combine "
            f"{type(a).__name__} and {type(b).__name__}"
        )

    def distance(self, other: "Shape") -> float:
        # The union's closest point to `other` is whichever member shape is closer.
        return min(self.shape_a.distance(other), self.shape_b.distance(other))

    def contains(self, point: Point) -> bool:
        return self.shape_a.contains(point) or self.shape_b.contains(point)

    def __repr__(self) -> str:
        return f"Union({self.shape_a!r}, {self.shape_b!r})"
