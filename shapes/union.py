"""Union of two shapes: the single region covered by either one of them."""

from . import _overlap
from .point import Point
from .shape import Shape


class Union(Shape):
    """The shape formed by combining two shapes into one region ("A or B").

    A ``Union`` is itself a ``Shape``, so it supports the same
    ``area()`` / ``perimeter()`` / ``distance(other)`` interface as
    ``Point``/``Line``/``Circle``/``Rectangle`` — and, because of that, a
    ``Union`` can be nested inside another ``Union`` to combine more than
    two shapes: ``Union(Union(a, b), c)``.

    See ``shapes/_overlap.py`` for how the overlap area between the two
    members is actually computed (exact for most shape pairs, Monte Carlo
    approximated for Circle-Rectangle).
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
        if self._touches_or_overlaps():
            raise NotImplementedError(
                "Union.perimeter() is only supported for two shapes that "
                "don't touch or overlap. The exact outer boundary length of "
                "two merged, overlapping shapes needs polygon-clipping / "
                "boundary-tracing machinery that's out of scope here — see "
                "the README's 'Known issues' section."
            )
        return self.shape_a.perimeter() + self.shape_b.perimeter()

    def distance(self, other: "Shape") -> float:
        # The union's closest point to `other` is whichever member shape is closer.
        return min(self.shape_a.distance(other), self.shape_b.distance(other))

    def contains(self, point: Point) -> bool:
        return self.shape_a.contains(point) or self.shape_b.contains(point)

    # ---- helpers ----------------------------------------------------------

    def _touches_or_overlaps(self) -> bool:
        # distance() between the two members is already exact (no sampling)
        # for every pair this project supports, so reuse it as a cheap,
        # exact overlap test instead of re-deriving one.
        return self.shape_a.distance(self.shape_b) <= 1e-9

    def __repr__(self) -> str:
        return f"Union({self.shape_a!r}, {self.shape_b!r})"
