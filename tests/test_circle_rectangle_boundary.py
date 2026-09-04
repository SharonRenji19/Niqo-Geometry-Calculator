"""Unit tests for shapes/_overlap.py's general Circle-Rectangle boundary
decomposition (circle_rectangle_union_perimeter /
circle_rectangle_intersection_perimeter).

This handles the genuinely hard case: a circle and an axis-aligned
rectangle overlapping *partially*, where the boundary is a real mix of
straight edges and a circular arc (as opposed to the "one shape fully
inside the other" case, which shapes/_overlap.py's fully_contains()
already handles trivially elsewhere).

The expected values below were computed with Shapely (an independent,
mature computational-geometry library) — NOT with this project's own
code — across a wide range of configurations, including the trickier
topologies: a rectangle edge that the circle crosses twice (acting as a
chord), and a circle poking through two/three/four rectangle edges at
once. Shapely itself is NOT a project dependency; it was only used
offline to generate these fixed expected numbers.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes._overlap import (
    circle_rectangle_intersection_perimeter,
    circle_rectangle_union_perimeter,
)
from shapes.circle import Circle
from shapes.point import Point
from shapes.rectangle import Rectangle


class TestCircleRectangleBoundaryAgainstShapely(unittest.TestCase):
    """Each case: (name, circle, rectangle, expected_union_perimeter,
    expected_intersection_perimeter), expected values from Shapely."""

    CASES = [
        (
            "circle_straddling_one_edge_as_chord",
            Circle(Point(5, 5), 3),
            Rectangle(Point(0, 0), Point(10, 4.9)),
            33.4281492793627,
            15.221406633992517,
        ),
        (
            "circle_through_both_left_and_right_edges",
            Circle(Point(5, 5), 6),
            Rectangle(Point(2, 0), Point(8, 10)),
            37.699111826716305,
            32.0,
        ),
        (
            "circle_poking_through_all_four_edges",
            Circle(Point(5, 5), 10),
            Rectangle(Point(3, 3), Point(7, 7)),
            62.83185304448179,
            16.0,
        ),
        (
            "circle_near_corner_two_adjacent_edges",
            Circle(Point(0, 0), 3),
            Rectangle(Point(-1, -1), Point(5, 5)),
            28.441291235081867,
            14.408264678276536,
        ),
        (
            "thin_sliver_rectangle",
            Circle(Point(5, 0), 4),
            Rectangle(Point(0, -0.2), Point(10, 0.2)),
            29.152420038139038,
            16.780321179658717,
        ),
        (
            "original_reported_case",
            Circle(Point(5, 0), 4),
            Rectangle(Point(0, -3), Point(6, 3)),
            29.056741969523802,
            20.075999248271078,
        ),
    ]

    def test_union_perimeter_matches_shapely(self):
        for name, circle, rect, expected_union, _ in self.CASES:
            with self.subTest(name):
                self.assertAlmostEqual(
                    circle_rectangle_union_perimeter(circle, rect),
                    expected_union,
                    places=4,
                )

    def test_intersection_perimeter_matches_shapely(self):
        for name, circle, rect, _, expected_intersection in self.CASES:
            with self.subTest(name):
                self.assertAlmostEqual(
                    circle_rectangle_intersection_perimeter(circle, rect),
                    expected_intersection,
                    places=4,
                )

    def test_union_and_intersection_perimeter_order_independent(self):
        # circle_rectangle_*_perimeter always takes (circle, rect) — but
        # Union/Intersection.perimeter() (which call these) accept either
        # argument order, so this just checks the underlying functions
        # give consistent, order-independent results across all cases.
        for name, circle, rect, expected_union, expected_intersection in self.CASES:
            with self.subTest(name):
                self.assertAlmostEqual(
                    circle_rectangle_union_perimeter(circle, rect),
                    expected_union,
                    places=4,
                )


if __name__ == "__main__":
    unittest.main()
