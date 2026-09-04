"""Unit tests for shapes/circle.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point import Point
from shapes.line import Line
from shapes.circle import Circle


class TestCircle(unittest.TestCase):
    def test_rejects_non_positive_radius(self):
        with self.assertRaises(ValueError):
            Circle(Point(0, 0), 0)
        with self.assertRaises(ValueError):
            Circle(Point(0, 0), -5)

    def test_area_and_perimeter(self):
        c = Circle(Point(0, 0), 5)
        self.assertAlmostEqual(c.area(), math.pi * 25)
        self.assertAlmostEqual(c.perimeter(), math.pi * 10)

    def test_distance_from_point_outside_circle(self):
        c = Circle(Point(0, 0), 5)
        self.assertAlmostEqual(c.distance(Point(10, 0)), 5.0)

    def test_distance_from_point_inside_circle_is_zero(self):
        c = Circle(Point(0, 0), 5)
        self.assertAlmostEqual(c.distance(Point(1, 1)), 0.0)

    def test_point_distance_to_circle_is_symmetric(self):
        c = Circle(Point(0, 0), 5)
        p = Point(10, 0)
        self.assertAlmostEqual(p.distance(c), c.distance(p))

    def test_distance_between_separate_circles(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(20, 0), 3)
        self.assertAlmostEqual(c1.distance(c2), 12.0)

    def test_distance_between_overlapping_circles_is_zero(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(1, 0), 5)
        self.assertAlmostEqual(c1.distance(c2), 0.0)

    def test_distance_from_circle_to_line(self):
        c = Circle(Point(0, 0), 5)
        line = Line(Point(10, -10), Point(10, 10))
        self.assertAlmostEqual(c.distance(line), 5.0)

    def test_circle_line_distance_is_symmetric(self):
        c = Circle(Point(0, 0), 5)
        line = Line(Point(10, -10), Point(10, 10))
        self.assertAlmostEqual(c.distance(line), line.distance(c))

    def test_contains_center_and_edge_and_outside(self):
        c = Circle(Point(0, 0), 5)
        self.assertTrue(c.contains(Point(0, 0)))
        self.assertTrue(c.contains(Point(5, 0)))  # on the boundary
        self.assertFalse(c.contains(Point(6, 0)))


if __name__ == "__main__":
    unittest.main()
