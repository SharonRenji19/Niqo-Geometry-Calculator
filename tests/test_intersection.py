"""Unit tests for shapes/intersection.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.circle import Circle
from shapes.intersection import Intersection
from shapes.line import Line
from shapes.point import Point
from shapes.rectangle import Rectangle


class TestIntersectionDisjointShapes(unittest.TestCase):
    def test_area_is_zero_when_disjoint(self):
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(10, 10), 1)
        self.assertEqual(Intersection(c1, c2).area(), 0.0)

    def test_perimeter_is_zero_when_disjoint(self):
        r1 = Rectangle(Point(0, 0), Point(2, 2))
        r2 = Rectangle(Point(10, 10), Point(12, 12))
        self.assertEqual(Intersection(r1, r2).perimeter(), 0.0)

    def test_distance_is_infinite_when_disjoint(self):
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(10, 10), 1)
        self.assertEqual(Intersection(c1, c2).distance(Point(0, 0)), math.inf)


class TestIntersectionCircleCircle(unittest.TestCase):
    def test_two_unit_circles_one_apart_matches_known_formula(self):
        # Classic "vesica piscis" case: closed-form area is well known,
        # so this checks the implementation against an independent formula.
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(1, 0), 1)
        r, d = 1, 1
        expected_area = 2 * r * r * math.acos(d / (2 * r)) - (d / 2) * math.sqrt(4 * r * r - d * d)
        self.assertAlmostEqual(Intersection(c1, c2).area(), expected_area, places=9)

    def test_identical_circles_intersection_equals_full_circle(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(0, 0), 5)
        i = Intersection(c1, c2)
        self.assertAlmostEqual(i.area(), c1.area(), places=6)
        self.assertAlmostEqual(i.perimeter(), c1.perimeter(), places=6)

    def test_one_circle_fully_inside_another(self):
        big = Circle(Point(0, 0), 10)
        small = Circle(Point(0, 0), 3)
        i = Intersection(big, small)
        self.assertAlmostEqual(i.area(), small.area(), places=6)
        self.assertAlmostEqual(i.perimeter(), small.perimeter(), places=6)


class TestIntersectionRectangleRectangle(unittest.TestCase):
    def test_overlap_area_and_perimeter(self):
        r1 = Rectangle(Point(0, 0), Point(10, 10))
        r2 = Rectangle(Point(5, 5), Point(15, 15))
        i = Intersection(r1, r2)
        self.assertAlmostEqual(i.area(), 25.0)      # 5x5 overlap square
        self.assertAlmostEqual(i.perimeter(), 20.0)  # 2*(5+5)


class TestIntersectionCircleRectangle(unittest.TestCase):
    def test_circle_fully_inside_rectangle_area_matches_circle(self):
        c = Circle(Point(5, 5), 2)
        r = Rectangle(Point(0, 0), Point(10, 10))
        i = Intersection(c, r)
        self.assertAlmostEqual(i.area(), c.area(), delta=0.01 * c.area())

    def test_order_does_not_matter(self):
        c = Circle(Point(5, 0), 4)
        r = Rectangle(Point(0, -3), Point(6, 3))
        self.assertAlmostEqual(
            Intersection(c, r).area(), Intersection(r, c).area(), delta=0.5
        )

    def test_perimeter_raises_not_implemented(self):
        c = Circle(Point(5, 0), 4)
        r = Rectangle(Point(0, -3), Point(6, 3))
        with self.assertRaises(NotImplementedError):
            Intersection(c, r).perimeter()

    def test_distance_raises_not_implemented_when_overlapping(self):
        c = Circle(Point(5, 0), 4)
        r = Rectangle(Point(0, -3), Point(6, 3))
        with self.assertRaises(NotImplementedError):
            Intersection(c, r).distance(Point(100, 100))

    def test_full_containment_gives_exact_perimeter_not_an_error(self):
        # Circle entirely inside Rectangle -> intersection *is* the circle,
        # so perimeter/distance should work exactly, not raise.
        c = Circle(Point(5, 5), 2)
        r = Rectangle(Point(0, 0), Point(10, 10))
        i = Intersection(c, r)
        self.assertAlmostEqual(i.perimeter(), c.perimeter())
        self.assertAlmostEqual(i.distance(Point(100, 100)), c.distance(Point(100, 100)))

    def test_rectangle_fully_inside_circle_gives_exact_perimeter(self):
        r = Rectangle(Point(-1, -1), Point(1, 1))
        c = Circle(Point(0, 0), 10)
        i = Intersection(r, c)
        self.assertAlmostEqual(i.perimeter(), r.perimeter())


class TestIntersectionWithZeroAreaShapes(unittest.TestCase):
    def test_point_inside_circle_has_zero_area_but_is_contained(self):
        c = Circle(Point(0, 0), 3)
        p = Point(0, 0)
        i = Intersection(c, p)
        self.assertEqual(i.area(), 0.0)
        self.assertTrue(i.contains(p))

    def test_line_fully_inside_rectangle_has_zero_area(self):
        r = Rectangle(Point(0, 0), Point(5, 5))
        line = Line(Point(1, 1), Point(4, 4))
        self.assertEqual(Intersection(r, line).area(), 0.0)


class TestIntersectionContains(unittest.TestCase):
    def test_contains_requires_membership_in_both_shapes(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(3, 0), 5)
        i = Intersection(c1, c2)
        self.assertTrue(i.contains(Point(1, 0)))    # inside both
        self.assertFalse(i.contains(Point(-4, 0)))  # inside c1 only


class TestIntersectionValidation(unittest.TestCase):
    def test_rejects_non_shape_arguments(self):
        with self.assertRaises(TypeError):
            Intersection(Point(0, 0), 5)


if __name__ == "__main__":
    unittest.main()
