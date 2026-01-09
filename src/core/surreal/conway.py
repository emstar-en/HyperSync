"""
Surreal Number Implementation - Conway's Construction

Implements actual surreal number arithmetic using Conway's construction:
- Surreal numbers defined by left and right sets
- Birthday calculation via recursive depth
- Comparison and arithmetic operations
- Ordinal number support
"""

from typing import Set, Optional, Union, Tuple
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class SurrealNumber:
    """
    Surreal number defined by Conway's construction.

    A surreal number is defined by two sets:
    - left: Set of surreal numbers (all < this number)
    - right: Set of surreal numbers (all > this number)

    Constraint: All elements of left < all elements of right
    """
    left: frozenset  # frozenset of SurrealNumber
    right: frozenset  # frozenset of SurrealNumber

    def __post_init__(self):
        """Validate Conway cut constraint."""
        # Check that all left < all right
        for l in self.left:
            for r in self.right:
                if not (l < r):
                    raise ValueError(f"Invalid Conway cut: {l} not < {r}")

    def birthday(self) -> int:
        """
        Calculate birthday (generation) of surreal number.

        Birthday is the earliest generation at which this number can be constructed:
        birthday({L|R}) = max(birthday(L), birthday(R)) + 1

        Returns:
            int: Birthday (generation number)
        """
        if not self.left and not self.right:
            return 0  # 0 = {|}

        left_birthdays = [l.birthday() for l in self.left] if self.left else [0]
        right_birthdays = [r.birthday() for r in self.right] if self.right else [0]

        return max(max(left_birthdays), max(right_birthdays)) + 1

    def __lt__(self, other: 'SurrealNumber') -> bool:
        """
        Surreal number comparison: x < y.

        x < y iff:
        - No element of x.right <= y
        - No element of y.left >= x

        Returns:
            bool: True if self < other
        """
        if not isinstance(other, SurrealNumber):
            return NotImplemented

        # Check: no x_R <= y
        for x_r in self.right:
            if not (other < x_r):
                return False

        # Check: no y_L >= x
        for y_l in other.left:
            if not (y_l < self):
                return False

        return True

    def __le__(self, other: 'SurrealNumber') -> bool:
        """x <= y iff not (y < x)"""
        return not (other < self)

    def __gt__(self, other: 'SurrealNumber') -> bool:
        """x > y iff y < x"""
        return other < self

    def __ge__(self, other: 'SurrealNumber') -> bool:
        """x >= y iff not (x < y)"""
        return not (self < other)

    def __eq__(self, other: 'SurrealNumber') -> bool:
        """x == y iff x <= y and y <= x"""
        if not isinstance(other, SurrealNumber):
            return False
        return self <= other and other <= self

    def __hash__(self):
        """Hash based on left and right sets."""
        return hash((self.left, self.right))

    def __repr__(self):
        """String representation."""
        left_repr = "{" + ", ".join(str(l) for l in sorted(self.left, key=lambda x: x.birthday())) + "}"
        right_repr = "{" + ", ".join(str(r) for r in sorted(self.right, key=lambda x: x.birthday())) + "}"
        return f"{left_repr}|{right_repr}"

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "left": [l.to_dict() for l in self.left],
            "right": [r.to_dict() for r in self.right],
            "birthday": self.birthday()
        }


# ============================================================================
# Standard Surreal Numbers
# ============================================================================

# 0 = {|}
ZERO = SurrealNumber(frozenset(), frozenset())

# 1 = {0|}
ONE = SurrealNumber(frozenset([ZERO]), frozenset())

# -1 = {|0}
MINUS_ONE = SurrealNumber(frozenset(), frozenset([ZERO]))

# 2 = {1|}
TWO = SurrealNumber(frozenset([ONE]), frozenset())

# -2 = {|-1}
MINUS_TWO = SurrealNumber(frozenset(), frozenset([MINUS_ONE]))

# 1/2 = {0|1}
ONE_HALF = SurrealNumber(frozenset([ZERO]), frozenset([ONE]))

# ω (omega) = {0, 1, 2, ...|}
# Represented as {0, 1, 2|} for practical purposes
OMEGA = SurrealNumber(frozenset([ZERO, ONE, TWO]), frozenset())


# ============================================================================
# Surreal Number Operations
# ============================================================================

def surreal_add(x: SurrealNumber, y: SurrealNumber) -> SurrealNumber:
    """
    Surreal number addition: x + y.

    x + y = {x_L + y, x + y_L | x_R + y, x + y_R}

    Args:
        x: First surreal number
        y: Second surreal number

    Returns:
        SurrealNumber: Sum x + y
    """
    left = frozenset()
    right = frozenset()

    # x_L + y
    for x_l in x.left:
        left = left | frozenset([surreal_add(x_l, y)])

    # x + y_L
    for y_l in y.left:
        left = left | frozenset([surreal_add(x, y_l)])

    # x_R + y
    for x_r in x.right:
        right = right | frozenset([surreal_add(x_r, y)])

    # x + y_R
    for y_r in y.right:
        right = right | frozenset([surreal_add(x, y_r)])

    return SurrealNumber(left, right)


def surreal_negate(x: SurrealNumber) -> SurrealNumber:
    """
    Surreal number negation: -x.

    -x = {-x_R | -x_L}

    Args:
        x: Surreal number to negate

    Returns:
        SurrealNumber: Negation -x
    """
    left = frozenset(surreal_negate(x_r) for x_r in x.right)
    right = frozenset(surreal_negate(x_l) for x_l in x.left)

    return SurrealNumber(left, right)


def surreal_subtract(x: SurrealNumber, y: SurrealNumber) -> SurrealNumber:
    """
    Surreal number subtraction: x - y = x + (-y).

    Args:
        x: First surreal number
        y: Second surreal number

    Returns:
        SurrealNumber: Difference x - y
    """
    return surreal_add(x, surreal_negate(y))


def surreal_multiply(x: SurrealNumber, y: SurrealNumber) -> SurrealNumber:
    """
    Surreal number multiplication: x * y.

    x * y = {x_L*y + x*y_L - x_L*y_L, x_R*y + x*y_R - x_R*y_R |
             x_L*y + x*y_R - x_L*y_R, x_R*y + x*y_L - x_R*y_L}

    Args:
        x: First surreal number
        y: Second surreal number

    Returns:
        SurrealNumber: Product x * y
    """
    left = frozenset()
    right = frozenset()

    # Left set: x_L*y + x*y_L - x_L*y_L
    for x_l in x.left:
        for y_l in y.left:
            term = surreal_subtract(
                surreal_add(surreal_multiply(x_l, y), surreal_multiply(x, y_l)),
                surreal_multiply(x_l, y_l)
            )
            left = left | frozenset([term])

    # Left set: x_R*y + x*y_R - x_R*y_R
    for x_r in x.right:
        for y_r in y.right:
            term = surreal_subtract(
                surreal_add(surreal_multiply(x_r, y), surreal_multiply(x, y_r)),
                surreal_multiply(x_r, y_r)
            )
            left = left | frozenset([term])

    # Right set: x_L*y + x*y_R - x_L*y_R
    for x_l in x.left:
        for y_r in y.right:
            term = surreal_subtract(
                surreal_add(surreal_multiply(x_l, y), surreal_multiply(x, y_r)),
                surreal_multiply(x_l, y_r)
            )
            right = right | frozenset([term])

    # Right set: x_R*y + x*y_L - x_R*y_L
    for x_r in x.right:
        for y_l in y.left:
            term = surreal_subtract(
                surreal_add(surreal_multiply(x_r, y), surreal_multiply(x, y_l)),
                surreal_multiply(x_r, y_l)
            )
            right = right | frozenset([term])

    return SurrealNumber(left, right)


# ============================================================================
# Ordinal Number Support
# ============================================================================

def create_ordinal(n: int) -> SurrealNumber:
    """
    Create ordinal number n.

    0 = {|}
    1 = {0|}
    2 = {1|}
    n = {n-1|}

    Args:
        n: Non-negative integer

    Returns:
        SurrealNumber: Ordinal n
    """
    if n < 0:
        raise ValueError("Ordinals must be non-negative")

    if n == 0:
        return ZERO

    prev = create_ordinal(n - 1)
    return SurrealNumber(frozenset([prev]), frozenset())


def create_omega_plus_n(n: int) -> SurrealNumber:
    """
    Create ω + n.

    ω + n = {ω, ω+1, ..., ω+(n-1)|}

    Args:
        n: Non-negative integer

    Returns:
        SurrealNumber: ω + n
    """
    if n == 0:
        return OMEGA

    # Build left set: {ω, ω+1, ..., ω+(n-1)}
    left = frozenset([OMEGA])
    for i in range(1, n):
        left = left | frozenset([create_omega_plus_n(i)])

    return SurrealNumber(left, frozenset())


# ============================================================================
# Priority System Integration
# ============================================================================

def priority_to_surreal(priority: Union[int, float, str]) -> SurrealNumber:
    """
    Convert priority value to surreal number.

    Args:
        priority: Priority value (int, float, or special string)

    Returns:
        SurrealNumber: Surreal representation
    """
    if isinstance(priority, int):
        if priority >= 0:
            return create_ordinal(priority)
        else:
            return surreal_negate(create_ordinal(-priority))

    elif isinstance(priority, float):
        # Approximate float as dyadic rational
        # For simplicity, round to nearest integer
        return priority_to_surreal(round(priority))

    elif isinstance(priority, str):
        if priority == "omega":
            return OMEGA
        elif priority.startswith("omega+"):
            n = int(priority.split("+")[1])
            return create_omega_plus_n(n)
        else:
            raise ValueError(f"Unknown priority string: {priority}")

    else:
        raise TypeError(f"Unsupported priority type: {type(priority)}")


def compare_priorities(p1: Union[int, float, str], 
                      p2: Union[int, float, str]) -> int:
    """
    Compare two priorities using surreal number ordering.

    Args:
        p1: First priority
        p2: Second priority

    Returns:
        int: -1 if p1 < p2, 0 if p1 == p2, 1 if p1 > p2
    """
    s1 = priority_to_surreal(p1)
    s2 = priority_to_surreal(p2)

    if s1 < s2:
        return -1
    elif s1 == s2:
        return 0
    else:
        return 1


# ============================================================================
# Attestation Generation
# ============================================================================

def generate_surreal_attestation(number: SurrealNumber) -> dict:
    """
    Generate attestation for surreal number.

    Args:
        number: Surreal number

    Returns:
        dict: Attestation with Conway cut and birthday
    """
    return {
        "type": "surreal_number_attestation",
        "conway_cut": {
            "left": [l.to_dict() for l in number.left],
            "right": [r.to_dict() for r in number.right]
        },
        "birthday": number.birthday(),
        "representation": str(number),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# Testing and Validation
# ============================================================================

def test_surreal_arithmetic():
    """Test surreal number arithmetic."""
    print("Testing surreal number arithmetic...")

    # Test comparison
    assert ZERO < ONE
    assert MINUS_ONE < ZERO
    assert ONE_HALF < ONE
    assert ZERO < ONE_HALF
    print("  ✓ Comparison works")

    # Test birthday
    assert ZERO.birthday() == 0
    assert ONE.birthday() == 1
    assert ONE_HALF.birthday() == 2
    print("  ✓ Birthday calculation works")

    # Test addition
    one_plus_one = surreal_add(ONE, ONE)
    assert one_plus_one == TWO
    print("  ✓ Addition works")

    # Test negation
    neg_one = surreal_negate(ONE)
    assert neg_one == MINUS_ONE
    print("  ✓ Negation works")

    # Test ordinals
    three = create_ordinal(3)
    assert TWO < three
    print("  ✓ Ordinal creation works")

    # Test priority comparison
    assert compare_priorities(1, 2) == -1
    assert compare_priorities(2, 2) == 0
    assert compare_priorities(3, 2) == 1
    assert compare_priorities(5, "omega") == -1
    print("  ✓ Priority comparison works")

    print("All tests passed!")


if __name__ == '__main__':
    test_surreal_arithmetic()
