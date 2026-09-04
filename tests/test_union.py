"""Unit tests for shapes/union.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.circle import Circle
from shapes.line import Line
from shapes.point import Point
from shapes.rectangle import Rectangle
from shapes.union import Union


class TestUnionDisjointShapes(unittest.TestCase):
    def test_area_is_additive_when_disjoint(self):
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(10, 10), 1)
        self.assertAlmostEqual(Union(c1, c2).area(), c1.area() + c2.area())

    def test_perimeter_is_additive_when_disjoint(self):
        r1 = Rectangle(Point(0, 0), Point(2, 2))
        r2 = Rectangle(Point(10, 10), Point(12, 12))
        self.assertAlmostEqual(Union(r1, r2).perimeter(), r1.perimeter() + r2.perimeter())

    def test_distance_to_a_third_shape_is_the_closer_members_distance(self):
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(100, 100), 1)
        target = Point(0, 5)
        u = Union(c1, c2)
        self.assertAlmostEqual(u.distance(target), c1.distance(target))


class TestUnionOverlappingShapes(unittest.TestCase):
    def test_two_identical_circles_collapse_to_one_circles_area(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(0, 0), 5)
        self.assertAlmostEqual(Union(c1, c2).area(), c1.area(), places=6)

    def test_two_disjoint_circles_have_zero_overlap_contribution(self):
        c1 = Circle(Point(0, 0), 1)
        c2 = Circle(Point(5, 5), 1)
        self.assertAlmostEqual(Union(c1, c2).area(), c1.area() + c2.area())

    def test_overlapping_rectangles_subtract_the_shared_square(self):
        r1 = Rectangle(Point(0, 0), Point(10, 10))   # area 100
        r2 = Rectangle(Point(5, 5), Point(15, 15))   # area 100, overlap 5x5=25
        self.assertAlmostEqual(Union(r1, r2).area(), 100 + 100 - 25)

    def test_overlapping_rectangles_perimeter_matches_hand_traced_shape(self):
        # A = [0,10]x[0,10], B = [3,7]x[5,15] -> B pokes up out of A's top
        # like a chimney. Hand-tracing that outline gives a perimeter of 50.
        a = Rectangle(Point(0, 0), Point(10, 10))
        b = Rectangle(Point(3, 5), Point(7, 15))
        self.assertAlmostEqual(Union(a, b).perimeter(), 50.0)

    def test_rectangle_fully_inside_another_perimeter_is_the_bigger_ones(self):
        big = Rectangle(Point(0, 0), Point(10, 10))
        small = Rectangle(Point(3, 3), Point(7, 7))
        self.assertAlmostEqual(Union(big, small).perimeter(), big.perimeter())

    def test_overlapping_circles_perimeter_excludes_the_swallowed_arcs(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(6, 0), 5)
        u = Union(c1, c2)
        # The union's outer boundary must be shorter than simply adding the
        # two full circumferences (some of each circle's arc is "inside"
        # the other one and shouldn't count), but still positive.
        self.assertLess(u.perimeter(), c1.perimeter() + c2.perimeter())
        self.assertGreater(u.perimeter(), 0.0)

    def test_identical_circles_perimeter_is_one_circles_circumference(self):
        c1 = Circle(Point(0, 0), 5)
        c2 = Circle(Point(0, 0), 5)
        self.assertAlmostEqual(Union(c1, c2).perimeter(), c1.perimeter(), places=6)

    def test_circle_rectangle_overlap_perimeter_raises_not_implemented(self):
        c = Circle(Point(5, 0), 4)
        r = Rectangle(Point(0, -3), Point(6, 3))
        with self.assertRaises(NotImplementedError):
            Union(c, r).perimeter()

    def test_circle_fully_inside_rectangle_area_matches_rectangle(self):
        # Exact answer: intersection == the circle's whole area, so the
        # union's area should equal the rectangle's area.
        c = Circle(Point(5, 5), 2)
        r = Rectangle(Point(0, 0), Point(10, 10))
        area = Union(c, r).area()
        self.assertAlmostEqual(area, r.area(), delta=0.01 * r.area())

    def test_circle_rectangle_order_does_not_matter(self):
        c = Circle(Point(5, 5), 3)
        r = Rectangle(Point(0, 0), Point(8, 8))
        self.assertAlmostEqual(Union(c, r).area(), Union(r, c).area(), delta=0.5)


class TestUnionWithZeroAreaShapes(unittest.TestCase):
    def test_union_with_a_point_equals_the_other_shapes_area(self):
        c = Circle(Point(0, 0), 3)
        p = Point(0, 0)
        self.assertAlmostEqual(Union(c, p).area(), c.area())

    def test_union_with_a_line_equals_the_other_shapes_area(self):
        r = Rectangle(Point(0, 0), Point(5, 5))
        line = Line(Point(1, 1), Point(4, 4))
        self.assertAlmostEqual(Union(r, line).area(), r.area())


class TestUnionValidation(unittest.TestCase):
    def test_rejects_non_shape_arguments(self):
        with self.assertRaises(TypeError):
            Union(Point(0, 0), 5)


if __name__ == "__main__":
    unittest.main()
