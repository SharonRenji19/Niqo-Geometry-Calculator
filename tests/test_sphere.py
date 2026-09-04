"""Unit tests for shapes/sphere.py.

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


class TestSphere(unittest.TestCase):
    def test_rejects_non_positive_radius(self):
        with self.assertRaises(ValueError):
            Sphere(Point3D(0, 0, 0), 0)
        with self.assertRaises(ValueError):
            Sphere(Point3D(0, 0, 0), -5)

    def test_surface_area_and_volume(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        self.assertAlmostEqual(s.area(), 4 * math.pi * 25)
        self.assertAlmostEqual(s.volume(), (4 / 3) * math.pi * 125)

    def test_distance_from_point_outside(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        self.assertAlmostEqual(s.distance(Point3D(10, 0, 0)), 5.0)

    def test_distance_from_point_inside_is_zero(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        self.assertAlmostEqual(s.distance(Point3D(1, 1, 1)), 0.0)

    def test_point_distance_to_sphere_is_symmetric(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        p = Point3D(10, 0, 0)
        self.assertAlmostEqual(p.distance(s), s.distance(p))

    def test_distance_between_separate_spheres(self):
        s1 = Sphere(Point3D(0, 0, 0), 5)
        s2 = Sphere(Point3D(20, 0, 0), 3)
        self.assertAlmostEqual(s1.distance(s2), 12.0)

    def test_distance_between_overlapping_spheres_is_zero(self):
        s1 = Sphere(Point3D(0, 0, 0), 5)
        s2 = Sphere(Point3D(1, 0, 0), 5)
        self.assertAlmostEqual(s1.distance(s2), 0.0)

    def test_distance_from_sphere_to_line(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        line = Line3D(Point3D(10, -10, 0), Point3D(10, 10, 0))
        self.assertAlmostEqual(s.distance(line), 5.0)

    def test_sphere_line_distance_is_symmetric(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        line = Line3D(Point3D(10, -10, 0), Point3D(10, 10, 0))
        self.assertAlmostEqual(s.distance(line), line.distance(s))

    def test_contains_center_boundary_and_outside(self):
        s = Sphere(Point3D(0, 0, 0), 5)
        self.assertTrue(s.contains(Point3D(0, 0, 0)))
        self.assertTrue(s.contains(Point3D(5, 0, 0)))  # on the boundary
        self.assertFalse(s.contains(Point3D(6, 0, 0)))


if __name__ == "__main__":
    unittest.main()
