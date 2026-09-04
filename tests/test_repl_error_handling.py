"""Regression tests for repl.py's error handling.

These exist because of a real bug: NotImplementedError (raised by
Union.perimeter()/Intersection.perimeter()/.distance() for unsupported
cases) wasn't in evaluate_line/run_repl's caught-exception list, so it
crashed the whole REPL process instead of printing a clean "Error: ..."
line and continuing. This locks in the fix.

Run from the project root with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import repl
from shapes.circle import Circle
from shapes.point import Point
from shapes.rectangle import Rectangle
from shapes.union import Union


class TestReplSurvivesEveryExceptionShapesCanRaise(unittest.TestCase):
    """run_repl()'s except clause must list every exception type any shape
    method can raise, or the REPL crashes instead of printing 'Error: ...'."""

    def test_run_repl_except_clause_covers_every_raised_exception_type(self):
        import ast
        import inspect

        # Collect every exception type actually raised anywhere under shapes/.
        shapes_dir = os.path.join(os.path.dirname(__file__), "..", "shapes")
        raised_types = set()
        for filename in os.listdir(shapes_dir):
            if not filename.endswith(".py"):
                continue
            with open(os.path.join(shapes_dir, filename)) as f:
                tree = ast.parse(f.read(), filename)
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise) and node.exc is not None:
                    target = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
                    if isinstance(target, ast.Name):
                        raised_types.add(target.id)

        # Collect exception types run_repl()'s except clause actually catches.
        source = inspect.getsource(repl.run_repl)
        tree = ast.parse(source)
        caught_types = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                elts = node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
                for elt in elts:
                    if isinstance(elt, ast.Name):
                        caught_types.add(elt.id)

        missing = raised_types - caught_types
        self.assertFalse(
            missing,
            f"run_repl() doesn't catch {missing} — an uncaught exception "
            "of this type will crash the whole REPL process instead of "
            "printing a clean 'Error: ...' line.",
        )

    def test_union_perimeter_not_implemented_error_prints_cleanly(self):
        # A direct, concrete repro of the exact bug: exercises
        # evaluate_line() (what run_repl() calls per line) the same way
        # the REPL loop does, and confirms it raises the *same* exception
        # type run_repl()'s except clause is asserted (above) to catch.
        # NOTE: this uses a genuinely *partial* Circle-Rectangle overlap
        # (Circle-Rectangle full containment is now handled exactly —
        # see test_previously_reported_scenario_now_works_correctly below).
        env = {}
        repl.evaluate_line("c = Circle(Point(5, 0), 4)", env)
        repl.evaluate_line("r = Rectangle(Point(0, -3), Point(6, 3))", env)
        repl.evaluate_line("u = Union(c, r)", env)
        with self.assertRaises(NotImplementedError):
            repl.evaluate_line("u.perimeter()", env)

    def test_repl_env_survives_a_not_implemented_error(self):
        # Even though evaluate_line() propagates the exception (run_repl()
        # is what catches it), the environment dict itself must stay
        # intact and usable for the next line — this checks that.
        env = {}
        repl.evaluate_line("c = Circle(Point(5, 0), 4)", env)
        repl.evaluate_line("r = Rectangle(Point(0, -3), Point(6, 3))", env)
        repl.evaluate_line("u = Union(c, r)", env)
        try:
            repl.evaluate_line("u.perimeter()", env)
        except NotImplementedError:
            pass
        # u (and everything before it) should still be usable afterward.
        result = repl.evaluate_line("u.area()", env)
        self.assertIsNotNone(result)

    def test_originally_reported_scenario_now_works_correctly(self):
        # This is the *exact* case that first surfaced the crash: a
        # Rectangle entirely inside a Circle. It no longer raises at all
        # — full containment is cheap and exact for every shape pair, so
        # Union.perimeter() now just returns the containing circle's own
        # perimeter instead of refusing.
        env = {}
        repl.evaluate_line("c1 = Circle(Point(0, 0), 5)", env)
        repl.evaluate_line("r1 = Rectangle(Point(0, 0), Point(4, 3))", env)
        repl.evaluate_line("u1 = Union(c1, r1)", env)
        result = repl.evaluate_line("u1.perimeter()", env)
        self.assertEqual(result, "31.41592654")  # 2*pi*5, the circle's own perimeter


if __name__ == "__main__":
    unittest.main()
