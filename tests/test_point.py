"""Unit tests for shapes/point.py.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shapes.point import Point


class TestPoint(unittest.TestCase):
    def test_area_and_perimeter_are_zero(self):
        p = Point(3, 4)
        self.assertEqual(p.area(), 0.0)
        self.assertEqual(p.perimeter(), 0.0)

    def test_distance_between_points(self):
        self.assertAlmostEqual(Point(0, 0).distance(Point(3, 4)), 5.0)

    def test_distance_is_symmetric(self):
        p1, p2 = Point(1, 1), Point(4, 5)
        self.assertAlmostEqual(p1.distance(p2), p2.distance(p1))

    def test_distance_to_self_is_zero(self):
        self.assertAlmostEqual(Point(7, 7).distance(Point(7, 7)), 0.0)

    def test_distance_to_unsupported_type_raises(self):
        with self.assertRaises(TypeError):
            Point(0, 0).distance("not a shape")

    def test_contains_only_true_for_itself(self):
        p = Point(2, 2)
        self.assertTrue(p.contains(Point(2, 2)))
        self.assertFalse(p.contains(Point(2, 3)))

    def test_repr_matches_assignment_example(self):
        self.assertEqual(repr(Point(10, 10)), "(10, 10)")

    def test_repr_keeps_decimals_when_not_whole(self):
        self.assertEqual(repr(Point(1.5, 2.25)), "(1.5, 2.25)")


if __name__ == "__main__":
    unittest.main()
