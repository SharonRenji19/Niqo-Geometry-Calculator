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


def circle_circle_union_perimeter(c1: Circle, c2: Circle) -> float:
    """Exact boundary length of the outer outline of two overlapping circles.

    Each circle contributes its own circumference *minus* the arc that
    gets "swallowed" by sitting inside the other circle — the same
    swallowed angle used by the intersection lens above.
    """
    d = c1.center.distance(c2.center)
    r1, r2 = c1.radius, c2.radius

    if d <= abs(r1 - r2):
        return 2 * math.pi * max(r1, r2)  # smaller circle fully inside bigger

    d1, d2, a1, a2 = _circle_circle_overlap_geometry(c1, c2, d)
    theta1, theta2 = 2 * a1, 2 * a2
    return (2 * math.pi - theta1) * r1 + (2 * math.pi - theta2) * r2


def _circle_circle_overlap_geometry(c1: Circle, c2: Circle, d: float):
    """Shared trig for the functions above (only valid for a proper,
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


def rectangle_rectangle_union_perimeter(r1: Rectangle, r2: Rectangle) -> float:
    """Exact perimeter of the outer outline of two overlapping rectangles.

    perimeter(A union B) = perimeter(A) + perimeter(B) - perimeter(overlap),
    except when one rectangle fully contains the other, in which case the
    union *is* just the bigger rectangle.
    """
    r1_contains_r2 = (
        r1.min_x <= r2.min_x and r1.max_x >= r2.max_x
        and r1.min_y <= r2.min_y and r1.max_y >= r2.max_y
    )
    r2_contains_r1 = (
        r2.min_x <= r1.min_x and r2.max_x >= r1.max_x
        and r2.min_y <= r1.min_y and r2.max_y >= r1.max_y
    )
    if r1_contains_r2:
        return r1.perimeter()
    if r2_contains_r1:
        return r2.perimeter()

    overlap_w, overlap_h = _rectangle_overlap_dims(r1, r2)
    perimeter_overlap = 2 * (overlap_w + overlap_h)
    return r1.perimeter() + r2.perimeter() - perimeter_overlap


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

    (`perimeter`, below, does NOT need this approximation — the boundary
    is a 1-D curve, not a 2-D region, and can be decomposed exactly; see
    `circle_rectangle_union_perimeter`/`circle_rectangle_intersection_perimeter`.)
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


def _segment_circle_intersection_ts(p0, p1, circle: Circle):
    """Where (as t in the open interval (0,1)) does segment p0->p1 cross
    the circle's boundary? p0/p1 are (x, y) tuples."""
    x0, y0 = p0
    x1, y1 = p1
    cx, cy, r = circle.center.x, circle.center.y, circle.radius
    dx, dy = x1 - x0, y1 - y0
    fx, fy = x0 - cx, y0 - cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    sq = math.sqrt(disc)
    ts = [t for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)) if 0.0 < t < 1.0]
    return sorted(set(round(t, 12) for t in ts))


def _circle_rectangle_boundary_pieces(circle: Circle, rect: Rectangle):
    """Decompose the circle's and rectangle's boundaries into pieces split
    at every point where they cross, each tagged with whether it lies
    inside the *other* shape.

    Returns (rect_segments, arc_pieces):
      - rect_segments: list of (length, is_inside_circle) for each
        maximal sub-segment of the rectangle's 4 edges.
      - arc_pieces: list of (angle_width, is_inside_rect) for each
        maximal arc of the circle.

    This only classifies membership (needed for perimeter, where order
    doesn't matter) — it doesn't stitch the pieces into an ordered
    boundary loop, which would additionally be needed for an exact-area
    algorithm. (Only used for the genuine *partial*-overlap case; full
    containment and no-overlap are handled as separate shortcuts by the
    callers, so at least one crossing is always expected here.)
    """
    edges = [
        ((rect.min_x, rect.min_y), (rect.max_x, rect.min_y)),  # bottom
        ((rect.max_x, rect.min_y), (rect.max_x, rect.max_y)),  # right
        ((rect.max_x, rect.max_y), (rect.min_x, rect.max_y)),  # top
        ((rect.min_x, rect.max_y), (rect.min_x, rect.min_y)),  # left
    ]

    rect_segments = []
    crossing_thetas = set()
    for (a, b) in edges:
        ts = _segment_circle_intersection_ts(a, b, circle)
        for t in ts:
            px = a[0] + t * (b[0] - a[0])
            py = a[1] + t * (b[1] - a[1])
            theta = math.atan2(py - circle.center.y, px - circle.center.x) % (2 * math.pi)
            crossing_thetas.add(round(theta, 12))

        boundaries = [0.0] + ts + [1.0]
        for i in range(len(boundaries) - 1):
            t0, t1 = boundaries[i], boundaries[i + 1]
            p0 = (a[0] + t0 * (b[0] - a[0]), a[1] + t0 * (b[1] - a[1]))
            p1 = (a[0] + t1 * (b[0] - a[0]), a[1] + t1 * (b[1] - a[1]))
            length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if length < 1e-12:
                continue
            mid = Point((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            rect_segments.append((length, circle.contains(mid)))

    arc_pieces = []
    if not crossing_thetas:
        # No crossings at all -> the whole circle is uniformly inside or
        # outside the rectangle (any one sample point tells us which).
        test_point = Point(circle.center.x + circle.radius, circle.center.y)
        arc_pieces.append((2 * math.pi, rect.contains(test_point)))
    else:
        thetas = sorted(crossing_thetas)
        thetas.append(thetas[0] + 2 * math.pi)  # wrap the last arc around
        for i in range(len(thetas) - 1):
            width = thetas[i + 1] - thetas[i]
            if width < 1e-12:
                continue
            mid_theta = (thetas[i] + thetas[i + 1]) / 2
            mid = Point(
                circle.center.x + circle.radius * math.cos(mid_theta),
                circle.center.y + circle.radius * math.sin(mid_theta),
            )
            arc_pieces.append((width, rect.contains(mid)))

    return rect_segments, arc_pieces


def circle_rectangle_union_perimeter(circle: Circle, rect: Rectangle) -> float:
    """Exact boundary length of the outer outline of a Circle/Rectangle
    *partial* overlap (full containment is handled separately by callers
    via `fully_contains`).

    Splits each rectangle edge at every point the circle crosses it, and
    the circle at every point a rectangle edge crosses it, then sums the
    rectangle sub-segments that lie *outside* the circle plus the circle
    arcs that lie *outside* the rectangle. Verified against Shapely
    (an independent, mature geometry library) across thousands of random
    configurations, including edges the circle crosses twice (acting as
    a chord) and circles poking through multiple/adjacent/opposite edges
    at once — see tests/test_circle_rectangle_boundary.py.
    """
    rect_segments, arc_pieces = _circle_rectangle_boundary_pieces(circle, rect)
    total = sum(length for length, inside_circle in rect_segments if not inside_circle)
    total += sum(circle.radius * width for width, inside_rect in arc_pieces if not inside_rect)
    return total


def circle_rectangle_intersection_perimeter(circle: Circle, rect: Rectangle) -> float:
    """Exact boundary length of a Circle/Rectangle *partial* overlap
    region (full containment is handled separately by callers via
    `fully_contains`). See `circle_rectangle_union_perimeter` for the
    method and validation."""
    rect_segments, arc_pieces = _circle_rectangle_boundary_pieces(circle, rect)
    total = sum(length for length, inside_circle in rect_segments if inside_circle)
    total += sum(circle.radius * width for width, inside_rect in arc_pieces if inside_rect)
    return total


def fully_contains(outer, inner) -> bool:
    """Exact test: is `inner` entirely inside (or equal to) `outer`?

    Covers all four Circle/Rectangle combinations directly with cheap
    geometric checks (corner-in-circle, bounding-box comparisons) — no
    Monte Carlo needed, even for Circle-Rectangle, since "does A fully
    swallow B" is a much easier question than "what's the exact overlap
    area/boundary". Used to shortcut perimeter (and could shortcut area)
    for full containment, where the union is simply the bigger shape and
    the intersection is simply the smaller one.
    """
    if isinstance(outer, Circle) and isinstance(inner, Rectangle):
        corners = [
            Point(inner.min_x, inner.min_y),
            Point(inner.max_x, inner.min_y),
            Point(inner.max_x, inner.max_y),
            Point(inner.min_x, inner.max_y),
        ]
        return all(outer.contains(corner) for corner in corners)
    if isinstance(outer, Rectangle) and isinstance(inner, Circle):
        return (
            outer.min_x <= inner.center.x - inner.radius
            and outer.max_x >= inner.center.x + inner.radius
            and outer.min_y <= inner.center.y - inner.radius
            and outer.max_y >= inner.center.y + inner.radius
        )
    if isinstance(outer, Circle) and isinstance(inner, Circle):
        return outer.center.distance(inner.center) + inner.radius <= outer.radius + 1e-9
    if isinstance(outer, Rectangle) and isinstance(inner, Rectangle):
        return (
            outer.min_x <= inner.min_x and outer.max_x >= inner.max_x
            and outer.min_y <= inner.min_y and outer.max_y >= inner.max_y
        )
    return False
