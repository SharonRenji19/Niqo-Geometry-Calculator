"""Union of two shapes: the single region covered by either one of them."""

import math
import random

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
    """

    # Monte Carlo sampling is only used for the one pair of shapes with no
    # simple closed-form overlap formula here: Circle vs Rectangle.
    _MC_SAMPLES = 200_000
    _MC_SEED = 1729  # fixed seed -> deterministic, repeatable results

    def __init__(self, shape_a: Shape, shape_b: Shape):
        if not isinstance(shape_a, Shape) or not isinstance(shape_b, Shape):
            raise TypeError("Union requires two Shape instances")
        self.shape_a = shape_a
        self.shape_b = shape_b

    # ---- Shape interface ------------------------------------------------

    def area(self) -> float:
        # Inclusion-exclusion: |A union B| = |A| + |B| - |A intersect B|
        return self.shape_a.area() + self.shape_b.area() - self._intersection_area()

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

    # ---- intersection-area helpers ---------------------------------------

    def _touches_or_overlaps(self) -> bool:
        # distance() between the two members is already exact (no sampling)
        # for every pair this project supports, so reuse it as a cheap,
        # exact overlap test instead of re-deriving one.
        return self.shape_a.distance(self.shape_b) <= 1e-9

    def _intersection_area(self) -> float:
        a, b = self.shape_a, self.shape_b

        # A Point or Line has zero area, so it can never contribute area to
        # an intersection (the overlap can't be bigger than either operand).
        # This also means Union involving a Point/Line never needs sampling.
        if a.area() == 0.0 or b.area() == 0.0:
            return 0.0

        if isinstance(a, Circle) and isinstance(b, Circle):
            return self._circle_circle_intersection_area(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Rectangle):
            return self._rectangle_rectangle_intersection_area(a, b)
        if isinstance(a, Circle) and isinstance(b, Rectangle):
            return self._circle_rectangle_intersection_area(a, b)
        if isinstance(a, Rectangle) and isinstance(b, Circle):
            return self._circle_rectangle_intersection_area(b, a)

        raise TypeError(
            f"Union.area() doesn't know how to intersect "
            f"{type(a).__name__} and {type(b).__name__}"
        )

    @staticmethod
    def _circle_circle_intersection_area(c1: Circle, c2: Circle) -> float:
        """Exact closed-form area of overlap between two circles."""
        d = c1.center.distance(c2.center)
        r1, r2 = c1.radius, c2.radius

        if d >= r1 + r2:
            return 0.0  # too far apart to touch
        if d <= abs(r1 - r2):
            return math.pi * min(r1, r2) ** 2  # one circle fully inside the other

        # Standard "sum of two circular segments" formula.
        d1 = (d * d - r2 * r2 + r1 * r1) / (2 * d)
        d2 = d - d1
        a1 = math.acos(max(-1.0, min(1.0, d1 / r1)))
        a2 = math.acos(max(-1.0, min(1.0, d2 / r2)))
        return (
            r1 * r1 * a1 - d1 * math.sqrt(max(0.0, r1 * r1 - d1 * d1))
            + r2 * r2 * a2 - d2 * math.sqrt(max(0.0, r2 * r2 - d2 * d2))
        )

    @staticmethod
    def _rectangle_rectangle_intersection_area(r1: Rectangle, r2: Rectangle) -> float:
        """Exact area of overlap between two axis-aligned rectangles."""
        overlap_w = min(r1.max_x, r2.max_x) - max(r1.min_x, r2.min_x)
        overlap_h = min(r1.max_y, r2.max_y) - max(r1.min_y, r2.min_y)
        if overlap_w <= 0 or overlap_h <= 0:
            return 0.0
        return overlap_w * overlap_h

    def _circle_rectangle_intersection_area(self, circle: Circle, rect: Rectangle) -> float:
        """Approximate area of overlap between a circle and a rectangle.

        There's no simple closed-form formula for this pair (it requires
        clipping a circle by up to 4 straight edges, with several cases
        depending on how many corners/arcs are involved). Rather than
        pull in a geometry library — which the assignment explicitly
        disallows for core calculator logic — this estimates the overlap
        with Monte Carlo sampling: draw many random points inside the
        smallest box that could possibly contain the overlap, and see
        what fraction land inside *both* shapes.

        This is an approximation (typically well within ~0.5% of the true
        area at `_MC_SAMPLES` = 200,000), not an exact value, and is
        deterministic because it's driven by a fixed random seed.
        """
        min_x = max(circle.center.x - circle.radius, rect.min_x)
        max_x = min(circle.center.x + circle.radius, rect.max_x)
        min_y = max(circle.center.y - circle.radius, rect.min_y)
        max_y = min(circle.center.y + circle.radius, rect.max_y)
        if max_x <= min_x or max_y <= min_y:
            return 0.0  # bounding boxes don't even overlap -> shapes can't either

        box_area = (max_x - min_x) * (max_y - min_y)
        rng = random.Random(self._MC_SEED)
        hits = 0
        for _ in range(self._MC_SAMPLES):
            x = rng.uniform(min_x, max_x)
            y = rng.uniform(min_y, max_y)
            if circle.contains(Point(x, y)):
                hits += 1
        return box_area * hits / self._MC_SAMPLES

    def __repr__(self) -> str:
        return f"Union({self.shape_a!r}, {self.shape_b!r})"
