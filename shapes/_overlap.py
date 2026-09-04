"""Shared "how much do these two shapes overlap" math.

Both shapes/union.py and shapes/intersection.py need the same overlap-area
(and, for a couple of pairs, overlap-perimeter) calculations, so they live
here once instead of being duplicated in both classes.
"""

import math
import random

from .circle import Circle
from .point import Point
from .rectangle import Rectangle

# Monte Carlo sampling is only used for the one pair with no simple
# closed-form overlap formula in this project: Circle vs Rectangle.
MC_SAMPLES = 200_000
MC_SEED = 1729  # fixed seed -> deterministic, repeatable results


def intersection_area(a, b) -> float:
    """Exact (or, for one pair, approximate) area shared by shapes a and b."""
    # A Point or Line has zero area, so it can never contribute area to an
    # intersection (the overlap can't be bigger than either operand). This
    # also means a Point/Line operand never needs Monte Carlo sampling.
    if a.area() == 0.0 or b.area() == 0.0:
        return 0.0

    if isinstance(a, Circle) and isinstance(b, Circle):
        return circle_circle_intersection_area(a, b)
    if isinstance(a, Rectangle) and isinstance(b, Rectangle):
        return rectangle_rectangle_intersection_area(a, b)
    if isinstance(a, Circle) and isinstance(b, Rectangle):
        return circle_rectangle_intersection_area(a, b)
    if isinstance(a, Rectangle) and isinstance(b, Circle):
        return circle_rectangle_intersection_area(b, a)

    raise TypeError(
        f"Don't know how to intersect {type(a).__name__} and {type(b).__name__}"
    )


def circle_circle_intersection_area(c1: Circle, c2: Circle) -> float:
    """Exact closed-form area of overlap between two circles."""
    d = c1.center.distance(c2.center)
    r1, r2 = c1.radius, c2.radius

    if d >= r1 + r2:
        return 0.0  # too far apart to touch
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2  # one circle fully inside the other

    d1, d2, a1, a2 = _circle_circle_overlap_geometry(c1, c2, d)
    return (
        r1 * r1 * a1 - d1 * math.sqrt(max(0.0, r1 * r1 - d1 * d1))
        + r2 * r2 * a2 - d2 * math.sqrt(max(0.0, r2 * r2 - d2 * d2))
    )


def circle_circle_intersection_perimeter(c1: Circle, c2: Circle) -> float:
    """Exact boundary length of the lens-shaped overlap of two circles.

    The lens's boundary is made of one arc from each circle, between the
    two points where the circles cross; each arc's length is r * theta,
    where theta is the angle it subtends at that circle's own center.
    """
    d = c1.center.distance(c2.center)
    r1, r2 = c1.radius, c2.radius

    if d >= r1 + r2:
        return 0.0  # disjoint -> no lens, no boundary
    if d <= abs(r1 - r2):
        return 2 * math.pi * min(r1, r2)  # fully-inside circle's own perimeter

    d1, d2, a1, a2 = _circle_circle_overlap_geometry(c1, c2, d)
    theta1, theta2 = 2 * a1, 2 * a2
    return r1 * theta1 + r2 * theta2


def _circle_circle_overlap_geometry(c1: Circle, c2: Circle, d: float):
    """Shared trig for the two functions above (only valid for a proper,
    partial overlap — callers handle the "disjoint" / "one inside the
    other" cases themselves before reaching here)."""
    r1, r2 = c1.radius, c2.radius
    d1 = (d * d - r2 * r2 + r1 * r1) / (2 * d)
    d2 = d - d1
    a1 = math.acos(max(-1.0, min(1.0, d1 / r1)))
    a2 = math.acos(max(-1.0, min(1.0, d2 / r2)))
    return d1, d2, a1, a2


def rectangle_rectangle_intersection_area(r1: Rectangle, r2: Rectangle) -> float:
    """Exact area of overlap between two axis-aligned rectangles."""
    overlap_w, overlap_h = _rectangle_overlap_dims(r1, r2)
    if overlap_w <= 0 or overlap_h <= 0:
        return 0.0
    return overlap_w * overlap_h


def rectangle_rectangle_intersection_perimeter(r1: Rectangle, r2: Rectangle) -> float:
    """Exact perimeter of the (rectangular) overlap of two rectangles."""
    overlap_w, overlap_h = _rectangle_overlap_dims(r1, r2)
    if overlap_w <= 0 or overlap_h <= 0:
        return 0.0
    return 2 * (overlap_w + overlap_h)


def _rectangle_overlap_dims(r1: Rectangle, r2: Rectangle):
    overlap_w = min(r1.max_x, r2.max_x) - max(r1.min_x, r2.min_x)
    overlap_h = min(r1.max_y, r2.max_y) - max(r1.min_y, r2.min_y)
    return overlap_w, overlap_h


def circle_rectangle_intersection_area(circle: Circle, rect: Rectangle) -> float:
    """Approximate area of overlap between a circle and a rectangle.

    There's no simple closed-form formula for this pair (it requires
    clipping a circle by up to 4 straight edges, with several cases
    depending on how many corners/arcs are involved). Rather than pull in
    a geometry library — which the assignment explicitly disallows for
    core calculator logic — this estimates the overlap with Monte Carlo
    sampling: draw many random points inside the smallest box that could
    possibly contain the overlap, and see what fraction land inside
    *both* shapes.

    This is an approximation (typically well within ~0.5% of the true
    area at `MC_SAMPLES` = 200,000), not an exact value, and is
    deterministic because it's driven by a fixed random seed.
    """
    min_x = max(circle.center.x - circle.radius, rect.min_x)
    max_x = min(circle.center.x + circle.radius, rect.max_x)
    min_y = max(circle.center.y - circle.radius, rect.min_y)
    max_y = min(circle.center.y + circle.radius, rect.max_y)
    if max_x <= min_x or max_y <= min_y:
        return 0.0  # bounding boxes don't even overlap -> shapes can't either

    box_area = (max_x - min_x) * (max_y - min_y)
    rng = random.Random(MC_SEED)
    hits = 0
    for _ in range(MC_SAMPLES):
        x = rng.uniform(min_x, max_x)
        y = rng.uniform(min_y, max_y)
        if circle.contains(Point(x, y)):
            hits += 1
    return box_area * hits / MC_SAMPLES
