
import cmath
import math
from .primitives import Point

def poincare_distance(p1: Point, p2: Point) -> float:
    """
    Calculates the hyperbolic distance between two points on the Poincaré disk.
    Formula: d(u, v) = arccosh(1 + 2 * |u-v|^2 / ((1-|u|^2)(1-|v|^2)))
    """
    u = p1.complex
    v = p2.complex

    u_sq = abs(u)**2
    v_sq = abs(v)**2
    diff_sq = abs(u - v)**2

    if u_sq >= 1.0 or v_sq >= 1.0:
        return float('inf')

    delta = 2 * diff_sq / ((1 - u_sq) * (1 - v_sq))
    return math.acosh(1 + delta)

def mobius_transform(z: Point, a: Point) -> Point:
    """
    Applies a Möbius transformation to point z using parameter a.
    f(z) = (z - a) / (1 - conj(a)z)
    """
    z_c = z.complex
    a_c = a.complex

    numerator = z_c - a_c
    denominator = 1 - (a_c.conjugate() * z_c)

    if denominator == 0:
        return Point(0, 0)

    return Point.from_complex(numerator / denominator)

def hyperbolic_midpoint(p1: Point, p2: Point) -> Point:
    """
    Calculates the hyperbolic midpoint between p1 and p2.
    Strategy: Transform p1 to origin, find Euclidean midpoint to transformed p2, transform back.
    """
    # 1. Transform p1 to origin (0,0) using f(z) = (z - p1) / (1 - conj(p1)z)
    # This is exactly mobius_transform(z, p1)

    # We need the inverse transform later: f^-1(w) = (w + p1) / (1 + conj(p1)w)
    # Which is mobius_transform(w, -p1)

    p2_prime = mobius_transform(p2, p1)

    # 2. The midpoint of 0 and p2_prime lies on the ray from 0 to p2_prime.
    # The hyperbolic distance from 0 to m_prime is half the distance from 0 to p2_prime.
    dist = poincare_distance(Point(0,0), p2_prime)
    half_dist = dist / 2.0

    # In the disk model, distance from origin r to Euclidean distance R is: r = tanh(R/2)
    # Wait, standard formula d(0,r) = 2 artanh(r). So r = tanh(d/2).
    # Here 'dist' is the hyperbolic distance.
    # The Euclidean magnitude of the midpoint m_prime is tanh(half_dist / 2).

    m_prime_mag = math.tanh(half_dist / 2.0)

    if abs(p2_prime.complex) == 0:
        return p1 # They were the same point

    # Scale p2_prime to this magnitude
    scale = m_prime_mag / abs(p2_prime.complex)
    m_prime = Point.from_complex(p2_prime.complex * scale)

    # 3. Transform back
    # Inverse of Mobius(z, a) is Mobius(z, -a)
    neg_p1 = Point(-p1.x, -p1.y)
    midpoint = mobius_transform(m_prime, neg_p1)

    return midpoint
