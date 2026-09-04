"""An axis-aligned rectangular cuboid ("box"), defined by two opposite corner Point3Ds."""

import math

from .point3d import Point3D, _fmt
from .shape3d import Shape3D


class Box(Shape3D):
    def __init__(self, corner1: Point3D, corner2: Point3D):
        if not isinstance(corner1, Point3D) or not isinstance(corner2, Point3D):
            raise TypeError("Box requires two Point3D instances")
        if corner1.x == corner2.x or corner1.y == corner2.y or corner1.z == corner2.z:
            raise ValueError(
                "Box corners must differ in x, y, and z (zero width/height/depth)"
            )
        # Normalize so min_* is always the "lower" corner, regardless of
        # which two opposite corners the caller passed in.
        self.min_x = min(corner1.x, corner2.x)
        self.max_x = max(corner1.x, corner2.x)
        self.min_y = min(corner1.y, corner2.y)
        self.max_y = max(corner1.y, corner2.y)
        self.min_z = min(corner1.z, corner2.z)
        self.max_z = max(corner1.z, corner2.z)

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def depth(self) -> float:
        return self.max_z - self.min_z

    def area(self) -> float:
        # Surface area.
        w, h, d = self.width, self.height, self.depth
        return 2 * (w * h + w * d + h * d)

    def volume(self) -> float:
        return self.width * self.height * self.depth

    def distance(self, other: "Shape3D") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .sphere import Sphere
        from .line3d import Line3D

        if isinstance(other, Point3D):
            return self._distance_to_point(other)
        if isinstance(other, Box):
            return self._distance_to_box(other)
        if isinstance(other, Sphere):
            return self._distance_to_sphere(other)
        if isinstance(other, Line3D):
            return self._distance_to_line(other)
        raise TypeError(
            f"Cannot compute distance between Box and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point3D) -> float:
        # Clamp the point onto the box; 0 if the point is inside.
        dx = max(self.min_x - point.x, 0.0, point.x - self.max_x)
        dy = max(self.min_y - point.y, 0.0, point.y - self.max_y)
        dz = max(self.min_z - point.z, 0.0, point.z - self.max_z)
        return math.hypot(dx, dy, dz)

    def _distance_to_box(self, other: "Box") -> float:
        dx = max(self.min_x - other.max_x, other.min_x - self.max_x, 0.0)
        dy = max(self.min_y - other.max_y, other.min_y - self.max_y, 0.0)
        dz = max(self.min_z - other.max_z, other.min_z - self.max_z, 0.0)
        return math.hypot(dx, dy, dz)

    def _distance_to_sphere(self, sphere) -> float:
        center_dist = self._distance_to_point(sphere.center)
        return max(0.0, center_dist - sphere.radius)

    def _distance_to_line(self, line) -> float:
        """Shortest distance between this box and a 3D segment.

        Unlike the 2D Rectangle-Line case (where checking the 4 boundary
        edges is enough, since a 2D rectangle's boundary *is* a closed
        curve), a 3D box's closest surface point to an external line can
        land in the middle of a flat *face*, not on an edge — so an
        edges-only check would sometimes report a distance that's too
        large. Deriving every face/edge/corner case by hand is a lot of
        geometry to get exactly right.

        Instead: distance-from-point-to-box (`_distance_to_point`) is a
        convex function of the point (a box is a convex region, and
        distance-to-a-convex-set is always a convex function), and a point
        moving along the segment is an affine function of the parameter
        t in [0, 1] — so distance-to-box as a function of t is also convex.
        A convex 1D function has a single minimum, so ternary search finds
        it exactly (to floating-point precision) without needing to
        classify which face/edge/corner is closest by hand. This also
        naturally returns 0 whenever the segment passes through the box,
        with no separate intersection check needed.
        """
        p1, p2 = line.p1, line.p2

        def distance_at(t: float) -> float:
            x = p1.x + t * (p2.x - p1.x)
            y = p1.y + t * (p2.y - p1.y)
            z = p1.z + t * (p2.z - p1.z)
            return self._distance_to_point(Point3D(x, y, z))

        lo, hi = 0.0, 1.0
        for _ in range(100):  # convergence is exponential; 100 is a large margin
            m1 = lo + (hi - lo) / 3
            m2 = hi - (hi - lo) / 3
            if distance_at(m1) < distance_at(m2):
                hi = m2
            else:
                lo = m1
        return distance_at((lo + hi) / 2)

    def contains(self, point: Point3D) -> bool:
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
            and self.min_z <= point.z <= self.max_z
        )

    def __repr__(self) -> str:
        return (
            f"(x: {_fmt(self.min_x)}..{_fmt(self.max_x)}, "
            f"y: {_fmt(self.min_y)}..{_fmt(self.max_y)}, "
            f"z: {_fmt(self.min_z)}..{_fmt(self.max_z)})"
        )
