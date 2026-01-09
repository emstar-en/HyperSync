
from dataclasses import dataclass
import cmath

@dataclass
class Point:
    x: float
    y: float

    def __post_init__(self):
        if self.magnitude >= 1.0:
            # Floating point tolerance
            if self.magnitude > 1.0000001:
                raise ValueError(f"Point ({self.x}, {self.y}) is outside the Poincaré disk (magnitude {self.magnitude} >= 1)")

    @property
    def complex(self) -> complex:
        return complex(self.x, self.y)

    @property
    def magnitude(self) -> float:
        return abs(self.complex)

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    @staticmethod
    def from_complex(z: complex) -> 'Point':
        return Point(z.real, z.imag)
