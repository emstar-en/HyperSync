
import numpy as np
from typing import Tuple, Union

class HyperbolicMetrics:
    """
    Implements distance metrics for various hyperbolic geometry models.
    """

    def poincare_distance(self, u: Tuple[float, float], v: Tuple[float, float]) -> float:
        """
        Compute distance in the Poincare disk model.
        d(u, v) = arccosh(1 + 2 * |u - v|^2 / ((1 - |u|^2) * (1 - |v|^2)))
        """
        u = np.array(u)
        v = np.array(v)

        u_sq = np.sum(u**2)
        v_sq = np.sum(v**2)
        diff_sq = np.sum((u - v)**2)

        # Numerical stability check
        if u_sq >= 1.0 or v_sq >= 1.0:
            # Clamp to boundary or handle error
            u_sq = min(u_sq, 0.999999)
            v_sq = min(v_sq, 0.999999)

        delta = 2 * diff_sq / ((1 - u_sq) * (1 - v_sq))
        return np.arccosh(1 + delta)

    def hyperboloid_distance(self, u: Tuple[float, ...], v: Tuple[float, ...]) -> float:
        """
        Compute distance in the Hyperboloid model (Minkowski model).
        d(u, v) = arccosh(-<u, v>_L) where <u, v>_L is the Lorentzian inner product.
        u, v are (n+1)-dimensional vectors where u_0^2 - u_1^2 - ... - u_n^2 = 1 and u_0 > 0.
        """
        u = np.array(u)
        v = np.array(v)

        # Lorentzian inner product: -u0*v0 + u1*v1 + ... + un*vn
        # Note: Convention varies. Sometimes it's u0*v0 - u1*v1 ...
        # Assuming standard physics convention (- + + +) or math convention (+ - - -)
        # For hyperboloid model H^n = {x : x_0^2 - x_1^2 - ... = 1, x_0 > 0}
        # The metric is induced from Minkowski space.
        # Distance d(u, v) satisfies cosh(d(u, v)) = u_0 v_0 - u_1 v_1 - ... - u_n v_n

        lorentzian_product = u[0] * v[0] - np.sum(u[1:] * v[1:])

        # Numerical stability
        lorentzian_product = max(1.0, lorentzian_product)

        return np.arccosh(lorentzian_product)

    def klein_distance(self, u: Tuple[float, float], v: Tuple[float, float]) -> float:
        """
        Compute distance in the Klein model.
        d(u, v) = arccosh( (1 - <u, v>) / sqrt((1 - |u|^2)(1 - |v|^2)) )
        """
        u = np.array(u)
        v = np.array(v)

        u_sq = np.sum(u**2)
        v_sq = np.sum(v**2)
        dot_prod = np.dot(u, v)

        # Numerical stability
        u_sq = min(u_sq, 0.999999)
        v_sq = min(v_sq, 0.999999)

        numerator = 1 - dot_prod
        denominator = np.sqrt((1 - u_sq) * (1 - v_sq))

        arg = numerator / denominator
        arg = max(1.0, arg)

        return np.arccosh(arg)

    def upper_half_space_distance(self, u: Tuple[float, ...], v: Tuple[float, ...]) -> float:
        """
        Compute distance in the Upper Half Space model.
        d(u, v) = arccosh( 1 + |u - v|^2 / (2 * u_n * v_n) )
        where u_n, v_n are the last coordinates (height).
        """
        u = np.array(u)
        v = np.array(v)

        diff_sq = np.sum((u - v)**2)
        height_u = u[-1]
        height_v = v[-1]

        # Ensure positive height
        if height_u <= 0 or height_v <= 0:
            raise ValueError("Points must be in upper half space (height > 0)")

        delta = diff_sq / (2 * height_u * height_v)
        return np.arccosh(1 + delta)
