"""A straight segment between two distinct Point3D endpoints in 3D space."""

import math

from .point3d import Point3D
from .shape3d import Shape3D

_EPS = 1e-12


class Line3D(Shape3D):
    def __init__(self, p1: Point3D, p2: Point3D):
        if not isinstance(p1, Point3D) or not isinstance(p2, Point3D):
            raise TypeError("Line3D requires two Point3D instances")
        if p1 == p2:
            raise ValueError("Line3D requires two distinct points")
        self.p1 = p1
        self.p2 = p2

    def length(self) -> float:
        return self.p1.distance(self.p2)

    def area(self) -> float:
        return 0.0

    def volume(self) -> float:
        return 0.0

    def distance(self, other: "Shape3D") -> float:
        # Imported lazily to avoid circular imports between the shape modules.
        from .sphere import Sphere
        from .box import Box

        if isinstance(other, Point3D):
            return self._distance_to_point(other)
        if isinstance(other, Line3D):
            return self._distance_to_line(other)
        if isinstance(other, (Sphere, Box)):
            # Both implement the Line3D case explicitly, so delegating here
            # is safe and won't bounce back and forth.
            return other.distance(self)
        raise TypeError(
            f"Cannot compute distance between Line3D and {type(other).__name__}"
        )

    def _distance_to_point(self, point: Point3D) -> float:
        """Shortest distance from `point` to this *segment* (clamped projection)."""
        x1, y1, z1 = self.p1.x, self.p1.y, self.p1.z
        x2, y2, z2 = self.p2.x, self.p2.y, self.p2.z
        px, py, pz = point.x, point.y, point.z

        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        seg_len_sq = dx * dx + dy * dy + dz * dz

        t = ((px - x1) * dx + (py - y1) * dy + (pz - z1) * dz) / seg_len_sq
        t = max(0.0, min(1.0, t))

        cx, cy, cz = x1 + t * dx, y1 + t * dy, z1 + t * dz
        return math.hypot(px - cx, py - cy, pz - cz)

    def _distance_to_line(self, other: "Line3D") -> float:
        """Shortest distance between two 3D segments (handles skew, parallel,
        and intersecting cases). Standard closest-point-between-two-segments
        algorithm (see e.g. Ericson, "Real-Time Collision Detection" §5.1.9) —
        needed because in 3D, two non-intersecting segments aren't necessarily
        parallel (they can be skew), unlike the 2D case.
        """
        p1, p2, p3, p4 = self.p1, self.p2, other.p1, other.p2
        d1 = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
        d2 = (p4.x - p3.x, p4.y - p3.y, p4.z - p3.z)
        r = (p1.x - p3.x, p1.y - p3.y, p1.z - p3.z)

        a = _dot(d1, d1)
        e = _dot(d2, d2)
        f = _dot(d2, r)

        if a <= _EPS and e <= _EPS:
            s, t = 0.0, 0.0
        elif a <= _EPS:
            s = 0.0
            t = _clamp(f / e, 0.0, 1.0)
        else:
            c = _dot(d1, r)
            if e <= _EPS:
                t = 0.0
                s = _clamp(-c / a, 0.0, 1.0)
            else:
                b = _dot(d1, d2)
                denom = a * e - b * b
                s = _clamp((b * f - c * e) / denom, 0.0, 1.0) if abs(denom) > _EPS else 0.0
                t = (b * s + f) / e
                if t < 0.0:
                    t = 0.0
                    s = _clamp(-c / a, 0.0, 1.0)
                elif t > 1.0:
                    t = 1.0
                    s = _clamp((b - c) / a, 0.0, 1.0)

        closest1 = (p1.x + s * d1[0], p1.y + s * d1[1], p1.z + s * d1[2])
        closest2 = (p3.x + t * d2[0], p3.y + t * d2[1], p3.z + t * d2[2])
        return math.hypot(
            closest1[0] - closest2[0], closest1[1] - closest2[1], closest1[2] - closest2[2]
        )

    def contains(self, point: Point3D) -> bool:
        return math.isclose(self._distance_to_point(point), 0.0, abs_tol=1e-9)

    def __repr__(self) -> str:
        return (
            f"[{_fmt(self.p1.x)}, {_fmt(self.p1.y)}, {_fmt(self.p1.z)} -> "
            f"{_fmt(self.p2.x)}, {_fmt(self.p2.y)}, {_fmt(self.p2.z)}]"
        )


def _dot(u, v) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _fmt(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.10g}"
