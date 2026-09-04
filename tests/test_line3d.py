"""Unit tests for shapes/line3d.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point3d import Point3D
from shapes.line3d import Line3D


class TestLine3D(unittest.TestCase):
    def test_rejects_identical_points(self):
        with self.assertRaises(ValueError):
            Line3D(Point3D(1, 1, 1), Point3D(1, 1, 1))

    def test_rejects_non_point3d_args(self):
        with self.assertRaises(TypeError):
            Line3D(Point3D(0, 0, 0), (1, 1, 1))

    def test_length_matches_point_distance(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(3, 4, 12))
        self.assertAlmostEqual(line.length(), 13.0)
        self.assertEqual(line.area(), 0.0)
        self.assertEqual(line.volume(), 0.0)

    def test_distance_from_point_perpendicular(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
        # Point offset (0, 3, 4) from the line -> perpendicular distance 5.
        self.assertAlmostEqual(line.distance(Point3D(5, 3, 4)), 5.0)

    def test_distance_from_point_beyond_endpoint_uses_endpoint(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
        self.assertAlmostEqual(line.distance(Point3D(15, 0, 0)), 5.0)

    def test_point_distance_to_line_is_symmetric(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
        p = Point3D(5, 3, 4)
        self.assertAlmostEqual(p.distance(line), line.distance(p))

    def test_skew_segments_perpendicular_offset(self):
        # Segment A along the x-axis, segment B along the y-axis at x=5, z=3.
        # These never meet and aren't parallel (skew) -> closest points
        # (5,0,0) and (5,0,3), distance 3.
        a = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
        b = Line3D(Point3D(5, -5, 3), Point3D(5, 5, 3))
        self.assertAlmostEqual(a.distance(b), 3.0)

    def test_parallel_segments_overlapping_range(self):
        a = Line3D(Point3D(0, 0, 0), Point3D(0, 0, 10))
        b = Line3D(Point3D(5, 0, -5), Point3D(5, 0, 5))
        self.assertAlmostEqual(a.distance(b), 5.0)

    def test_intersecting_3d_segments_have_zero_distance(self):
        a = Line3D(Point3D(0, 0, 0), Point3D(10, 10, 10))
        b = Line3D(Point3D(0, 10, 0), Point3D(10, 0, 10))
        self.assertAlmostEqual(a.distance(b), 0.0)

    def test_distance_to_unsupported_type_raises(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
        with self.assertRaises(TypeError):
            line.distance(42)

    def test_contains_endpoint_and_midpoint(self):
        line = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
        self.assertTrue(line.contains(Point3D(0, 0, 0)))
        self.assertTrue(line.contains(Point3D(5, 0, 0)))
        self.assertFalse(line.contains(Point3D(5, 1, 0)))


if __name__ == "__main__":
    unittest.main()
