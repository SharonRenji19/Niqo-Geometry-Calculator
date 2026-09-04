# Geometric Calculator

A small REPL for defining 2D shapes and querying their measurements.
Implements **Point**, **Line**, **Circle**, and **Rectangle**, with
distance supported between every pair of shape types.

## Setup & Running

Requires Python 3.10+ (uses `list[Token]` / `X | None` type hints). No
third-party dependencies.

```bash
python3 repl.py
```

Example session:

```
> p1 = Point(10, 10)
p1(10, 10)
> p2 = Point(20, 20)
p2(20, 20)
> p1.distance(p2)
14.14213562
> l1 = Line(p1, p2)
l1[10, 10 -> 20, 20]
> l1.length()
14.14213562
```

## Design

- `shapes/shape.py` — abstract `Shape` base class defining the common
  interface every shape implements: `area()`, `perimeter()`, `distance(other)`.
- `shapes/point.py`, `shapes/line.py`, `shapes/circle.py`,
  `shapes/rectangle.py` — concrete shapes. `distance()` is implemented
  per pair of shape types (Point-Point, Point-Line, Circle-Rectangle,
  etc.) rather than as one generic formula, since each pair needs
  genuinely different math. `Line.distance(Point)` measures to the
  *segment*, not the infinite line, using the standard clamped-projection
  formula. `Rectangle` is axis-aligned, built from two opposite corner
  Points, and normalizes them internally so it doesn't matter which two
  opposite corners are passed in.
  - To avoid every shape needing an explicit case for every other shape,
    each shape implements distance to shapes "simpler" than itself
    directly (Circle→Point, Rectangle→Point, Rectangle→Circle, etc.) and
    delegates to the other shape's method for anything it doesn't handle
    itself — but only where the other shape is guaranteed to handle it
    explicitly, so the delegation always terminates and can't bounce
    back and forth forever.
- `repl.py` — a small hand-written interpreter:
  - **Tokenizer** (`tokenize`) — regex-based, splits an input line into
    NUMBER / NAME / OP tokens.
  - **Parser** (`Parser`) — recursive-descent, one method per grammar rule
    (`parse_expr` → `parse_term` → `parse_factor` → `parse_call_chain`),
    giving `*`/`/` higher precedence than `+`/`-` and letting constructor
    calls and method calls nest arbitrarily
    (e.g. `p1.distance(p2) + p1.distance(p3)`).
  - A dict-based environment (`env`) persists variables across lines.

No external geometry libraries are used for any of the above — only
`math` for `sqrt`/`hypot`-style primitives, and `re` for tokenizing, both
of which are language/arithmetic utilities rather than geometry logic.

## Assumptions

- `Line` requires two **distinct** points (a zero-length line is rejected
  with a clear error rather than silently allowed).
- `Line.distance(Point)` / `Line.distance(Line)` measure against the
  finite **segment**, not the mathematically infinite line through it —
  this matches how "a line" is used in the assignment's own examples
  (constructed from two points) and is the more useful real-world
  interpretation for a robotics context.
- `area()` and `perimeter()` are defined on `Point`/`Line` and return
  `0.0`, rather than raising, since both shapes are degenerate 
  (zero-dimensional / one-dimensional) rather than invalid. This keeps
  the `Shape` interface uniform for future shapes to also just work when
  passed to generic area/perimeter-consuming code.
- Numbers print without a trailing `.0` when they're whole (`10` not
  `10.0`), matching the assignment's sample output, but keep full
  precision (`%.10g`) otherwise.
- The REPL's arithmetic operators (`+ - * /`) currently only apply to
  numeric results (e.g. `p1.distance(p2) + p1.distance(p3)`), not to
  shapes themselves — shape arithmetic (union/intersection) is a
  separate concern to be added as its own methods later.

## Additional assumptions (Circle, Rectangle)

- `Rectangle` is always **axis-aligned** — built from two opposite
  corners, e.g. `Rectangle(Point(0,0), Point(10,10))`. Rotated rectangles
  aren't supported; this keeps distance/area math tractable without a
  general polygon library, which the assignment doesn't ask for.
- `Circle` requires a strictly positive radius; a zero or negative radius
  is rejected rather than silently treated as a degenerate point.
- Distance from a shape to a shape it's "inside of" or overlapping with
  (e.g. a point inside a circle, two overlapping rectangles) is `0.0`,
  not negative — distance never goes negative in this calculator.

## Known issues / not yet implemented

- Union / Intersection (optional extra credit) are not implemented yet.
- No unit test suite yet (planned as automated `pytest` tests, run
  separately from the core no-library constraint since testing tooling
  isn't "core calculator" logic).
- Line-Line distance for non-intersecting segments checks only the four
  endpoint-to-opposite-segment distances; this is provably sufficient
  for straight segments (the closest pair between two disjoint convex
  sets includes an extreme point) but is worth calling out explicitly.
- Rectangle-Line distance checks rectangle edges against the line segment
  for intersection and otherwise takes the minimum over corner/endpoint
  candidate distances — correct, but more expensive than a closed-form
  solution would be; fine at this scale.

## Challenges

- Getting operator precedence right in the parser (`*`/`/` before
  `+`/`-`) while still allowing shape constructor calls and chained
  method calls to nest inside expressions, without pulling in a parser
  library.
- Deciding what "distance from a point to a line" should mean given the
  assignment models `Line` as a segment (via two `Point`s) rather than
  an infinite line — went with segment distance as the more intuitive,
  practically useful choice.
