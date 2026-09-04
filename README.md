# Geometric Calculator

A small REPL for defining 2D shapes and querying their measurements.
Implements **Point**, **Line**, **Circle**, **Rectangle**, **Union**, and
**Intersection** (combining/overlapping two shapes), with distance
supported between every pair of shape types.

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
> c = Circle(Point(5, 0), 4)
c(center=(5, 0), r=4)
> r = Rectangle(Point(0, -3), Point(6, 3))
r(x: 0..6, y: -3..3)
> u = Union(c, r)
uUnion((center=(5, 0), r=4), (x: 0..6, y: -3..3))
> u.area()
58.78128246
> i = Intersection(Circle(Point(0,0), 5), Rectangle(Point(3,3), Point(9,9)))
iIntersection((center=(0, 0), r=5), (x: 3..9, y: 3..9))
> i.area()
0.54674
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
- `shapes/_overlap.py` — shared "how much do these two shapes overlap"
  math used by both `Union` and `Intersection`, so the overlap-area (and,
  for a couple of pairs, overlap-perimeter) logic exists in exactly one
  place: exact formulas for Circle-Circle and Rectangle-Rectangle, Monte
  Carlo sampling for Circle-Rectangle, and a free `0.0` for anything
  involving a Point/Line.
- `shapes/union.py` — `Union(shape_a, shape_b)`, the combined region
  covered by either shape ("A or B"). It's a `Shape` itself, so it
  supports `area()` / `perimeter()` / `distance(other)` like everything
  else, and can be nested (`Union(Union(a, b), c)`) to combine more than
  two shapes.
  - `area()` uses inclusion-exclusion: `|A| + |B| - |A ∩ B|`, via
    `_overlap.intersection_area()`.
  - `perimeter()` returns the exact sum of the two members' perimeters
    when they don't touch or overlap, and raises `NotImplementedError`
    with an explanatory message when they do (see "Known issues").
  - `distance(other)` is `min(shape_a.distance(other), shape_b.distance(other))`
    — the union's closest point to another shape is whichever member is closer.
  - `contains(point)` is `shape_a.contains(point) or shape_b.contains(point)`.
    This method was added to `Point`/`Line`/`Circle` too (`Rectangle`
    already had it) purely to support `Union`/`Intersection`'s
    area/membership checks.
- `shapes/intersection.py` — `Intersection(shape_a, shape_b)`, the shape
  formed by the overlap of two shapes ("A and B"). Same `Shape` interface:
  - `area()` calls the same `_overlap.intersection_area()` `Union` uses
    (exact for Circle-Circle/Rectangle-Rectangle/anything with a
    Point-Line, Monte Carlo for Circle-Rectangle).
  - `perimeter()` is exact for Circle-Circle (arc-length formula for the
    lens shape) and Rectangle-Rectangle (the overlap is itself a
    rectangle), `0.0` when there's no overlap, and raises
    `NotImplementedError` for Circle-Rectangle (see "Known issues").
  - `distance(other)` returns `math.inf` when the two shapes don't
    overlap at all (an empty region has no closest point) and raises
    `NotImplementedError` for a genuine non-empty overlap (see "Known
    issues").
  - `contains(point)` is `shape_a.contains(point) and shape_b.contains(point)`.
- `tests/test_union.py`, `tests/test_intersection.py` — `unittest`
  coverage for both: disjoint vs. overlapping shapes, identical/nested
  circles, Point/Line as one operand, and argument validation. Run with:
  `python3 -m unittest discover -s tests`.
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
- The REPL's arithmetic operators (`+ - * /`) apply only to numeric
  results (e.g. `p1.distance(p2) + p1.distance(p3)`), not to shapes
  themselves — combining shapes is done explicitly via `Union(a, b)`
  rather than an overloaded `+`, so it reads the same way a shape
  constructor call does and doesn't need new parser grammar.

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

- **Overlap area for Circle + Rectangle is approximate, not exact.** There's
  no simple closed-form formula for the area where a circle and an
  axis-aligned rectangle overlap (it requires case-by-case clipping of
  the circle's arc against up to 4 straight edges). Rather than pull in
  a computational-geometry library — explicitly disallowed for core
  calculator logic — `_overlap.py` estimates this one case with Monte
  Carlo sampling (200,000 random points inside the overlap's bounding
  box, fixed seed `1729` for determinism), which is typically within
  ~0.5% of the true value. Every other shape pair (Circle-Circle,
  Rectangle-Rectangle, and anything involving a Point/Line) is exact.
- **`Union.perimeter()`/`Intersection.perimeter()` don't support a
  Circle-Rectangle overlap**, and `Union.perimeter()` more broadly
  doesn't support *any* overlapping pair. Tracing the exact merged (or
  clipped) boundary where a straight edge meets a circular arc needs
  polygon-clipping/boundary-tracing machinery that's out of scope here.
  Both raise a clear `NotImplementedError` rather than returning a wrong
  number; the cases with a real closed-form answer (disjoint shapes for
  `Union`, Circle-Circle and Rectangle-Rectangle for `Intersection`) are
  still computed exactly.
- **`Intersection.distance(other)` only handles the empty-overlap case**
  (returns `math.inf`, since an empty region has no closest point) and
  raises `NotImplementedError` for a genuine non-empty overlap — finding
  the closest point of an arbitrary overlap region to a third shape
  needs that region's actual clipped boundary, which this project
  doesn't construct (only totals like area/perimeter, not boundary
  geometry). `Union.distance(other)` doesn't have this limitation
  (`min` of the two members always makes sense).
- No unit test suite for the pre-existing Point/Line/Circle/Rectangle
  shapes yet — `tests/test_union.py` and `tests/test_intersection.py`
  (new) only cover `Union`/`Intersection`.
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
