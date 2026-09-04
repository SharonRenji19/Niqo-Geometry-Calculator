"""Unit tests for shapes/rectangle.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point import Point
from shapes.line import Line
from shapes.circle import Circle
from shapes.rectangle import Rectangle


class TestRectangle(unittest.TestCase):
    def test_rejects_zero_width_or_height(self):
        with self.assertRaises(ValueError):
            Rectangle(Point(0, 0), Point(0, 5))
        with self.assertRaises(ValueError):
            Rectangle(Point(0, 0), Point(5, 0))

    def test_normalizes_corner_order(self):
        # top-right, bottom-left order should give the same box as bottom-left, top-right.
        r1 = Rectangle(Point(10, 10), Point(0, 0))
        r2 = Rectangle(Point(0, 0), Point(10, 10))
        self.assertEqual(
            (r1.min_x, r1.min_y, r1.max_x, r1.max_y),
            (r2.min_x, r2.min_y, r2.max_x, r2.max_y),
        )

    def test_area_and_perimeter(self):
        r = Rectangle(Point(0, 0), Point(4, 3))
        self.assertAlmostEqual(r.area(), 12.0)
        self.assertAlmostEqual(r.perimeter(), 14.0)

    def test_contains(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        self.assertTrue(r.contains(Point(5, 5)))
        self.assertFalse(r.contains(Point(15, 5)))

    def test_distance_to_point_inside_is_zero(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        self.assertAlmostEqual(r.distance(Point(5, 5)), 0.0)

    def test_distance_to_point_outside(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        self.assertAlmostEqual(r.distance(Point(20, 5)), 10.0)

    def test_point_distance_to_rectangle_is_symmetric(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        p = Point(20, 5)
        self.assertAlmostEqual(p.distance(r), r.distance(p))

    def test_distance_between_separate_rectangles(self):
        r1 = Rectangle(Point(0, 0), Point(10, 10))
        r2 = Rectangle(Point(20, 0), Point(30, 10))
        self.assertAlmostEqual(r1.distance(r2), 10.0)

    def test_distance_between_overlapping_rectangles_is_zero(self):
        r1 = Rectangle(Point(0, 0), Point(5, 5))
        r2 = Rectangle(Point(2, 2), Point(3, 3))
        self.assertAlmostEqual(r1.distance(r2), 0.0)

    def test_distance_between_rectangle_and_circle(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        c = Circle(Point(20, 5), 3)
        self.assertAlmostEqual(r.distance(c), 7.0)

    def test_rectangle_circle_distance_is_symmetric(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        c = Circle(Point(20, 5), 3)
        self.assertAlmostEqual(r.distance(c), c.distance(r))

    def test_distance_between_rectangle_and_intersecting_line(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        line = Line(Point(-5, 5), Point(5, 5))
        self.assertAlmostEqual(r.distance(line), 0.0)

    def test_distance_between_rectangle_and_separate_line(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        line = Line(Point(20, -5), Point(20, 15))
        self.assertAlmostEqual(r.distance(line), 10.0)

    def test_rectangle_line_distance_is_symmetric(self):
        r = Rectangle(Point(0, 0), Point(10, 10))
        line = Line(Point(20, -5), Point(20, 15))
        self.assertAlmostEqual(r.distance(line), line.distance(r))


if __name__ == "__main__":
    unittest.main()
