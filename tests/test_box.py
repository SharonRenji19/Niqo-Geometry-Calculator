"""Unit tests for shapes/box.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point3d import Point3D
from shapes.line3d import Line3D
from shapes.sphere import Sphere
from shapes.box import Box


class TestBox(unittest.TestCase):
    def test_rejects_zero_width_height_or_depth(self):
        with self.assertRaises(ValueError):
            Box(Point3D(0, 0, 0), Point3D(0, 5, 5))
        with self.assertRaises(ValueError):
            Box(Point3D(0, 0, 0), Point3D(5, 0, 5))
        with self.assertRaises(ValueError):
            Box(Point3D(0, 0, 0), Point3D(5, 5, 0))

    def test_normalizes_corner_order(self):
        b1 = Box(Point3D(10, 10, 10), Point3D(0, 0, 0))
        b2 = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        self.assertEqual(
            (b1.min_x, b1.min_y, b1.min_z, b1.max_x, b1.max_y, b1.max_z),
            (b2.min_x, b2.min_y, b2.min_z, b2.max_x, b2.max_y, b2.max_z),
        )

    def test_volume_and_surface_area(self):
        b = Box(Point3D(0, 0, 0), Point3D(4, 3, 2))
        self.assertAlmostEqual(b.volume(), 24.0)
        self.assertAlmostEqual(b.area(), 2 * (4 * 3 + 4 * 2 + 3 * 2))

    def test_contains(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        self.assertTrue(b.contains(Point3D(5, 5, 5)))
        self.assertFalse(b.contains(Point3D(15, 5, 5)))

    def test_distance_to_point_inside_is_zero(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        self.assertAlmostEqual(b.distance(Point3D(5, 5, 5)), 0.0)

    def test_distance_to_point_beyond_a_corner(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        self.assertAlmostEqual(b.distance(Point3D(20, 20, 20)), math.sqrt(3 * 100))

    def test_distance_to_point_beyond_a_face(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        self.assertAlmostEqual(b.distance(Point3D(15, 5, 5)), 5.0)

    def test_point_distance_to_box_is_symmetric(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        p = Point3D(15, 5, 5)
        self.assertAlmostEqual(p.distance(b), b.distance(p))

    def test_distance_between_separate_boxes(self):
        b1 = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        b2 = Box(Point3D(20, 0, 0), Point3D(30, 10, 10))
        self.assertAlmostEqual(b1.distance(b2), 10.0)

    def test_distance_between_nested_boxes_is_zero(self):
        b1 = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        b2 = Box(Point3D(5, 5, 5), Point3D(6, 6, 6))
        self.assertAlmostEqual(b1.distance(b2), 0.0)

    def test_distance_between_box_and_sphere(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        s = Sphere(Point3D(20, 5, 5), 3)
        self.assertAlmostEqual(b.distance(s), 7.0)

    def test_box_sphere_distance_is_symmetric(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        s = Sphere(Point3D(20, 5, 5), 3)
        self.assertAlmostEqual(b.distance(s), s.distance(b))

    def test_distance_to_line_hovering_over_face_interior(self):
        # The critical case: nearest box point is (5, 5, 10), the *middle*
        # of the top face -- not on any edge. An edges-only approach (the
        # 2D Rectangle-Line trick) would report a distance that's too large
        # here, since it would never consider face-interior points.
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        line = Line3D(Point3D(5, 5, 15), Point3D(5, 5, 20))
        self.assertAlmostEqual(b.distance(line), 5.0)

    def test_distance_to_line_passing_through_box_is_zero(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        line = Line3D(Point3D(5, 5, -10), Point3D(5, 5, 20))
        self.assertAlmostEqual(b.distance(line), 0.0)

    def test_distance_to_line_touching_corner_is_zero(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        line = Line3D(Point3D(10, 10, 10), Point3D(20, 20, 20))
        self.assertAlmostEqual(b.distance(line), 0.0)

    def test_distance_to_line_near_edge_minimizes_at_interior_t(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        line = Line3D(Point3D(13, 13, 5), Point3D(13, 13, -5))
        self.assertAlmostEqual(b.distance(line), math.sqrt(18))

    def test_box_line_distance_is_symmetric(self):
        b = Box(Point3D(0, 0, 0), Point3D(10, 10, 10))
        line = Line3D(Point3D(5, 5, 15), Point3D(5, 5, 20))
        self.assertAlmostEqual(b.distance(line), line.distance(b))


if __name__ == "__main__":
    unittest.main()
