"""Unit tests for shapes/point3d.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point import Point
from shapes.point3d import Point3D


class TestPoint3D(unittest.TestCase):
    def test_area_and_volume_are_zero(self):
        p = Point3D(1, 2, 3)
        self.assertEqual(p.area(), 0.0)
        self.assertEqual(p.volume(), 0.0)

    def test_distance_3_4_12_triangle(self):
        # 3-4-12-13 is the 3D analogue of the classic 3-4-5 right triangle:
        # sqrt(3^2 + 4^2 + 12^2) = sqrt(169) = 13.
        self.assertAlmostEqual(Point3D(0, 0, 0).distance(Point3D(3, 4, 12)), 13.0)

    def test_distance_is_symmetric(self):
        p1, p2 = Point3D(1, 1, 1), Point3D(4, 5, 6)
        self.assertAlmostEqual(p1.distance(p2), p2.distance(p1))

    def test_distance_to_self_is_zero(self):
        self.assertAlmostEqual(Point3D(7, 7, 7).distance(Point3D(7, 7, 7)), 0.0)

    def test_distance_to_2d_point_raises(self):
        # Mixing 2D and 3D shapes is not supported and should fail clearly.
        with self.assertRaises(TypeError):
            Point3D(0, 0, 0).distance(Point(0, 0))

    def test_contains_only_true_for_itself(self):
        p = Point3D(2, 2, 2)
        self.assertTrue(p.contains(Point3D(2, 2, 2)))
        self.assertFalse(p.contains(Point3D(2, 2, 3)))

    def test_repr(self):
        self.assertEqual(repr(Point3D(10, 10, 10)), "(10, 10, 10)")


if __name__ == "__main__":
    unittest.main()
