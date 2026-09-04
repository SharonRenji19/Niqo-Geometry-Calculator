# Geometric Calculator

A small REPL for defining 2D and 3D shapes and querying their
measurements. 2D: **Point**, **Line**, **Circle**, **Rectangle**,
**Union**, and **Intersection** (combining/overlapping two shapes). 3D:
**Point3D**, **Line3D**, **Sphere**, **Box**. Distance is supported
between every pair of shape types *within* the same dimensionality
(2D-2D and 3D-3D); mixing a 2D and a 3D shape raises a clear error
rather than silently doing something wrong — see "Assumptions".

## Setup & Running (step-by-step)

**Prerequisites:** Python 3.10 or later, nothing else — no pip installs
needed to run the calculator itself (only the automated tests use one
extra tool, `pytest`, which is optional — see below).

1. **Check your Python version.**
   ```bash
   python3/python --version
   ```
   Needs to say `3.10` or higher (the code uses modern type hints like
   `list[Token]` and `X | None`).

   **On Windows**, `**python3**` commonly isn't set up — running it may
   print a message about installing Python from the Microsoft Store
   even when Python is already installed. Use `**python**` instead
   (`py` also works if that's set up on your machine); the rest of the
   commands below are identical either way, just swap `**python3**` for
   whichever one resolves on your system.

2. **Get the code.** Either clone the repo:
   ```bash
   git clone https://github.com/SharonRenji19/Niqo-Geometry-Calculator.git
   cd Niqo-Geometry-Calculator
   ```
   or unzip the submitted archive and `cd` into the extracted folder —
   either way, you should now be in the folder containing `repl.py` and
   the `shapes/` directory directly (run `ls` / `dir` to confirm).

3. **Run it — no build step, no install step:**
   ```bash
   python3/python repl.py
   ```
   You should see:
   ```
   Geometric Calculator — supports Point, Line, Circle, Rectangle, Union, Intersection. Type 'exit' to quit.
   >
   ```
   Try the assignment's own example to confirm it's working:
   ```
   > p1 = Point(10, 10)
   p1(10, 10)
   > p2 = Point(20, 20)
   p2(20, 20)
   > p1.distance(p2)
   14.14213562
   ```
   Type `exit` (or Ctrl+C / Ctrl+D) to quit.

4. **(Optional) Run the automated test suite**, which independently
   verifies all the area/perimeter/distance math without needing the
   REPL at all:
   ```bash
   python3/python -m unittest discover -s tests
   ```
   Expect `OK` at the bottom with all tests passing. If `pytest` is
   installed (`pip install pytest`), `python3/python -m pytest` works too and
   gives slightly more detailed output.

No external dependencies, virtual environment, or `pip install` are
required for step 3 — only Python's own standard library (`math`, `re`)
is used anywhere in the core calculator.

## Example session

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
> p3d = Point3D(0, 0, 0)
p3d(0, 0, 0)
> sph = Sphere(Point3D(10, 0, 0), 4)
sph(center=(10, 0, 0), r=4)
> p3d.distance(sph)
6
> box = Box(Point3D(0, 0, 0), Point3D(5, 5, 5))
box(x: 0..5, y: 0..5, z: 0..5)
> box.volume()
125
> box.area()
150
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
  for a few pairs, overlap-perimeter) logic exists in exactly one
  place: exact formulas for Circle-Circle and Rectangle-Rectangle overlap
  area/perimeter, Monte Carlo sampling for Circle-Rectangle *area*, a
  free `0.0` for anything involving a Point/Line, and `fully_contains()`
  — a cheap, *exact* "does shape A completely swallow shape B" test for
  all four Circle/Rectangle combinations (no sampling needed even for
  Circle-Rectangle, since full containment is a much easier question
  than the exact overlap boundary).
- `shapes/union.py` — `Union(shape_a, shape_b)`, the combined region
  covered by either shape ("A or B"). It's a `Shape` itself, so it
  supports `area()` / `perimeter()` / `distance(other)` like everything
  else, and can be nested (`Union(Union(a, b), c)`) to combine more than
  two shapes.
  - `area()` uses inclusion-exclusion: `|A| + |B| - |A ∩ B|`, via
    `_overlap.intersection_area()`.
  - `perimeter()` is exact for every case: disjoint shapes (plain sum),
    full containment of any shape pair (just the containing shape's own
    perimeter), Circle-Circle overlap (each circle's circumference minus
    the swallowed arc), Rectangle-Rectangle overlap
    (`perimeter(A) + perimeter(B) - perimeter(overlap)`), and even a
    genuinely *partial* Circle-Rectangle overlap — see "Known issues"
    for how that last one works (it's more involved, but still exact,
    no approximation).
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
  - `perimeter()` is exact for every case, the mirror image of `Union`'s:
    full containment of any shape pair (the intersection is just the
    *smaller*, fully-swallowed shape's own perimeter), Circle-Circle
    (arc-length formula for the lens shape), Rectangle-Rectangle (the
    overlap is itself a rectangle), `0.0` when there's no overlap at
    all, and a genuinely *partial* Circle-Rectangle overlap (see "Known
    issues").
  - `distance(other)` returns `math.inf` when the two shapes don't
    overlap at all (an empty region has no closest point), the smaller
    shape's own `distance(other)` for full containment, and raises
    `NotImplementedError` for a genuine *partial* overlap (see "Known
    issues").
  - `contains(point)` is `shape_a.contains(point) and shape_b.contains(point)`.
- `tests/test_union.py`, `tests/test_intersection.py` — `unittest`

  coverage for both: disjoint vs. overlapping shapes, identical/nested
  circles, Point/Line as one operand, and argument validation. Run with:
  `python3/python -m unittest discover -s tests`.
- `shapes/shape3d.py`, `shapes/point3d.py`, `shapes/line3d.py`,
  `shapes/sphere.py`, `shapes/box.py` — the 3D shapes, following the
  same overall pattern as their 2D counterparts (each shape handles
  distance to shapes "simpler" than itself directly and delegates
  upward only where that's guaranteed to terminate). Two things needed
  genuinely new math rather than a straightforward 2D→3D port:
  - **Line3D-Line3D distance** — in 2D, two non-parallel segments either
    intersect (distance 0) or don't; in 3D, two segments can be
    **skew** — not parallel, and never intersecting, like two edges of
    a box on different faces. `Line3D._distance_to_line` uses the
    standard closest-point-between-two-segments algorithm (clamped
    parametric projection onto each segment, handling the degenerate
    parallel/point cases separately) rather than a 2D-style
    intersection check.
  - **Box-Line3D distance** — in 2D, `Rectangle`'s boundary is a closed
    curve (4 edges), so checking just those edges against the line is
    enough, since the closest point on a convex 2D region to an
    outside point always lies on that boundary curve. A 3D `Box`'s
    boundary is a *surface* (6 faces), and the closest point can land
    in the middle of a flat face — not on any of the 12 edges — so an
    edges-only check (the naive 2D-style approach) would sometimes
    report too large a distance. Instead, `Box._distance_to_line` uses
    the fact that distance-from-a-point-to-a-box is a convex function,
    and a point moving along a segment is an affine function of the
    segment parameter `t` — so distance-to-box as a function of `t` is
    also convex, meaning **ternary search** over `t ∈ [0, 1]` finds the
    true minimum (this also makes a separate "does the segment
    intersect the box" check unnecessary — the search just finds 0
    naturally when it does). See "Known issues" for why this is a
    numerical method rather than a closed-form one.
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

## Additional assumptions (3D: Point3D, Line3D, Sphere, Box)

- **3D shapes use a separate `Shape3D` interface with `area()` +
  `volume()` instead of `Shape`'s `area()` + `perimeter()`.**
  "Perimeter" is a 2D boundary-*length* concept; a solid's boundary is
  a surface, so the natural measurements are surface **area** and
  **volume** instead. `area()` on a 3D shape means *surface* area
  (e.g. `Sphere.area()` is `4πr²`, not the circle's `πr²`).
- **2D and 3D shapes cannot be mixed** — `Point3D(...).distance(Point(...))`
  raises `TypeError` rather than guessing an interpretation (e.g.
  silently treating the 2D point as having `z=0`). This wasn't the
  assignment's Point/Line/Circle/Rectangle model to begin with, and
  guessing felt like the wrong kind of "fair assumption."
- `Box` is axis-aligned, exactly like `Rectangle` in 2D — same
  rationale (rotated boxes need real 3D linear algebra for very little
  payoff here).
- `Sphere` requires a strictly positive radius, same as `Circle`.

## Known issues / not yet implemented

- **`Box.distance(Line3D)` uses ternary search (a numerical method),
  not a closed-form formula.** In 2D, `Rectangle`'s distance to a `Line`
  only needs to check the rectangle's 4 boundary edges, because the
  closest point on a convex 2D shape's boundary to an outside point
  always lies on that boundary. A 3D `Box`'s boundary is a surface (6
  faces), and the closest point can land in the *middle* of a face —
  not on any of the 12 edges — so deriving this by hand would mean
  correctly classifying which of a face/edge/corner is closest for
  every possible line orientation (dozens of cases). Instead,
  `Box._distance_to_line` exploits that distance-to-a-box is a convex
  function of position along the segment, and finds its minimum via
  ternary search (100 iterations, converging well past floating-point
  precision — this is exact for all practical purposes, unlike the
  Circle-Rectangle Monte Carlo case below, which is a genuine
  approximation). Verified against hand-derived cases including the
  specific scenario that would break an edges-only approach (a line
  hovering directly over the *center* of a face) — see
  `tests/test_box.py`.


- **Overlap *area* for Circle + Rectangle is approximate, not exact** (its
  *perimeter* is exact — see below). There's no simple closed-form
  formula for the *area* where a circle and an axis-aligned rectangle
  overlap without tracing the actual clipped polygon-plus-arc boundary
  and integrating it, which is meaningfully more work than the
  perimeter case. Rather than pull in a computational-geometry library
  — explicitly disallowed for core calculator logic — `_overlap.py`
  estimates area with Monte Carlo sampling (200,000 random points
  inside the overlap's bounding box, fixed seed `1729` for
  determinism), which is typically within ~0.5% of the true value.
  Every other shape pair's area (Circle-Circle, Rectangle-Rectangle,
  and anything involving a Point/Line) is exact.
- **`Union.perimeter()`/`Intersection.perimeter()` are exact for every
  case, including a genuinely *partial* Circle-Rectangle overlap.**
  Initially this project treated Circle-Rectangle overlap as too hard
  to solve exactly for perimeter and raised `NotImplementedError` — but
  it turns out perimeter (a 1-D boundary length) doesn't need the full
  clipped-polygon machinery area does; it only needs to classify pieces
  of the boundary as in/out, not trace an ordered closed loop. The
  general algorithm (`shapes/_overlap.py`, `_circle_rectangle_boundary_pieces`
  and the two `circle_rectangle_*_perimeter` functions):
  1. Finds every point where the circle crosses one of the rectangle's
     4 edges (a circle crosses any straight line in at most 2 points,
     so this is bounded and simple — no iterative/numerical solving).
  2. Splits each rectangle edge into sub-segments at those crossings,
     and splits the circle into arcs at those same crossings (converted
     to angles).
  3. Classifies each sub-segment/arc as inside or outside the *other*
     shape by testing its midpoint.
  4. Sums the pieces that are outside (for `Union`) or inside (for
     `Intersection`) the other shape.

  This handles every topology correctly — including a rectangle edge
  the circle crosses *twice* (acting as a chord) and a circle poking
  through two, three, or all four rectangle edges at once — verified
  against [Shapely](https://shapely.readthedocs.io/) (an independent,
  mature geometry library used only offline to *generate* the expected
  test values in `tests/test_circle_rectangle_boundary.py` — it is
  **not** a runtime dependency of this project) across thousands of
  randomized configurations plus several hand-picked tricky cases, all
  matching to floating-point precision. Full containment of any shape
  pair (including Circle-Rectangle) is handled separately and even more
  cheaply via `_overlap.fully_contains` — an exact, no-crossings-needed
  check — before this general algorithm is even reached.

  Other closed-form cases, also exact:
  - **Circle-Circle union**: each circle's own circumference, minus
    the arc "swallowed" by sitting inside the other circle.
  - **Rectangle-Rectangle union**: `perimeter(A) + perimeter(B) -
    perimeter(overlap rectangle)` — verified against a hand-traced
    example in the union tests.
  - **Full containment (any pair)**: the union is just the containing
    shape's own perimeter; the intersection is just the contained
    shape's own perimeter.
- **`Intersection.distance(other)` handles the empty-overlap case**
  (returns `math.inf`, since an empty region has no closest point) **and
  full containment** (the intersection is exactly the smaller shape, so
  its distance is just that shape's own `distance()`), but raises
  `NotImplementedError` for a genuine *partial* overlap — finding the
  closest point of an arbitrary overlap region to a third shape needs
  that region's actual clipped boundary, which this project doesn't
  construct for partial overlaps. `Union.distance(other)` doesn't have
  this limitation (`min` of the two members always makes sense).
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
- A real bug surfaced during manual testing: `run_repl()`'s exception
  handler listed specific exception types to catch, but
  `NotImplementedError` (used by `Union`/`Intersection` for genuinely
  unsupported cases) wasn't among them — so instead of printing a clean
  `Error: ...` line, it crashed the whole REPL process with a
  traceback. Fixed by adding it to the caught types, and locked in with
  a regression test (`tests/test_repl_error_handling.py`) that
  statically scans every exception type raised anywhere under `shapes/`
  and asserts the REPL's handler covers all of them — so this class of
  bug can't silently reappear if a future `raise` is added without
  updating the handler.
- The same bug report also prompted tightening `Union`/`Intersection`
  perimeter support twice over. First pass: the initial version refused
  *any* overlapping shape pair with a blanket `NotImplementedError`,
  which was more conservative than necessary — Circle-Circle overlap,
  Rectangle-Rectangle overlap, and full containment of any shape pair
  all have real closed-form perimeter formulas (see "Design" above).
  Second pass: even the remaining *partial* Circle-Rectangle overlap
  turned out to be solvable exactly (see "Known issues" for the
  boundary-decomposition algorithm) — the earlier `NotImplementedError`
  there wasn't a fundamental limit, just an underestimate of how much
  simpler *perimeter* (a 1-D boundary length) is than *area* (the actual
  hard 2-D clipping problem, still Monte-Carlo-approximated). Verified
  against Shapely across thousands of randomized configurations before
  trusting it enough to ship.


## Anything else

A few things worth mentioning that didn't fit neatly elsewhere:

- **The whole cross-shape `distance()` system follows one consistent
  pattern everywhere** — 2D, 3D, and even Union/Intersection: each shape
  implements distance to shapes "simpler" than itself directly, and
  delegates upward only to a shape guaranteed to handle the case
  explicitly. This is what keeps adding a new shape a bounded,
  well-defined task (implement its own cases, delegate the rest)
  instead of an ever-growing matrix of special cases scattered across
  every file.
- **Two places in this project use a numerical method instead of a
  closed-form formula, and I think it's worth being upfront about the
  difference between them rather than presenting both the same way**:
  Circle-Rectangle overlap *area* (Monte Carlo sampling) is a genuine
  approximation — it converges toward the true value but never reaches
  it exactly. Box-to-Line3D distance (ternary search) is different: the
  function being minimized is provably convex, so the search converges
  to the exact answer, just via iteration instead of algebra. Both are
  documented in "Known issues," but they're not really the same kind of
  "known issue."
- **Test coverage grew in two different ways.** Most of it was written
  after the corresponding shape already existed — still real, automated
  coverage, but not strict TDD. One case (documented under
  "Challenges") was genuinely test-first: a bug was found, a test was
  written to reproduce it, then the fix made that test pass. I'd rather
  be precise about which is which than claim more process rigor than
  actually happened.
- Given the 48-hour window, I prioritized breadth-with-correctness
  (get every required shape/query genuinely right, verified by tests)
  over depth-with-approximation (e.g. spending the remaining time only
  on exact polygon-clipping for Circle-Rectangle overlap). Happy to
  walk through what an exact version of that would take if useful.
