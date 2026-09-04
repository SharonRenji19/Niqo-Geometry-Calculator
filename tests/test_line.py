"""Unit tests for shapes/line.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point import Point
from shapes.line import Line


class TestLine(unittest.TestCase):
    def test_rejects_identical_points(self):
        with self.assertRaises(ValueError):
            Line(Point(1, 1), Point(1, 1))

    def test_rejects_non_point_args(self):
        with self.assertRaises(TypeError):
            Line(Point(0, 0), (1, 1))

    def test_length_matches_point_distance(self):
        line = Line(Point(0, 0), Point(3, 4))
        self.assertAlmostEqual(line.length(), 5.0)
        self.assertAlmostEqual(line.perimeter(), line.length())

    def test_area_is_zero(self):
        self.assertEqual(Line(Point(0, 0), Point(1, 1)).area(), 0.0)

    def test_distance_from_point_on_segment_is_zero(self):
        line = Line(Point(0, 0), Point(10, 0))
        self.assertAlmostEqual(line.distance(Point(5, 0)), 0.0)

    def test_distance_from_point_off_segment_is_perpendicular(self):
        line = Line(Point(0, 0), Point(10, 0))
        self.assertAlmostEqual(line.distance(Point(5, 3)), 3.0)

    def test_distance_from_point_beyond_endpoint_uses_endpoint(self):
        # Closest point on the *segment* is the endpoint, not the infinite line.
        line = Line(Point(0, 0), Point(10, 0))
        self.assertAlmostEqual(line.distance(Point(15, 0)), 5.0)

    def test_point_distance_to_line_is_symmetric(self):
        line = Line(Point(0, 0), Point(10, 0))
        p = Point(5, 3)
        self.assertAlmostEqual(p.distance(line), line.distance(p))

    def test_intersecting_segments_have_zero_distance(self):
        l1 = Line(Point(0, 0), Point(10, 10))
        l2 = Line(Point(0, 10), Point(10, 0))
        self.assertAlmostEqual(l1.distance(l2), 0.0)

    def test_parallel_segments_distance(self):
        l1 = Line(Point(0, 0), Point(10, 0))
        l2 = Line(Point(0, 5), Point(10, 5))
        self.assertAlmostEqual(l1.distance(l2), 5.0)

    def test_distance_to_unsupported_type_raises(self):
        line = Line(Point(0, 0), Point(1, 1))
        with self.assertRaises(TypeError):
            line.distance(42)

    def test_contains_endpoint_and_midpoint(self):
        line = Line(Point(0, 0), Point(10, 0))
        self.assertTrue(line.contains(Point(0, 0)))
        self.assertTrue(line.contains(Point(5, 0)))
        self.assertFalse(line.contains(Point(5, 1)))


if __name__ == "__main__":
    unittest.main()
