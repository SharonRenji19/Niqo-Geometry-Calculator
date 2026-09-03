"""Abstract base class for all 2D geometric shapes."""

from abc import ABC, abstractmethod


class Shape(ABC):
    """Every shape supports area, perimeter, and distance-to-another-shape."""

    @abstractmethod
    def area(self) -> float:
        """Return the shape's area (0.0 for shapes with no interior, e.g. Point/Line)."""
        raise NotImplementedError

    @abstractmethod
    def perimeter(self) -> float:
        """Return the shape's perimeter / circumference / length."""
        raise NotImplementedError

    @abstractmethod
    def distance(self, other: "Shape") -> float:
        """Return the shortest distance between this shape and another shape."""
        raise NotImplementedError
