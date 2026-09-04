"""Abstract base class for all 3D shapes.

Separate from `Shape` (the 2D interface) rather than sharing it, because
"perimeter" is a 2D boundary-length concept with no 3D equivalent — a solid
has a surface *area* and a *volume* instead. See README "Assumptions" for
the reasoning.
"""

from abc import ABC, abstractmethod


class Shape3D(ABC):
    @abstractmethod
    def area(self) -> float:
        """Surface area of the solid (0.0 for degenerate shapes like Point3D/Line3D)."""
        raise NotImplementedError

    @abstractmethod
    def volume(self) -> float:
        """Volume enclosed by the solid (0.0 for degenerate shapes like Point3D/Line3D)."""
        raise NotImplementedError

    @abstractmethod
    def distance(self, other: "Shape3D") -> float:
        """Shortest distance between this shape and another 3D shape."""
        raise NotImplementedError
