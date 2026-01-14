"""
Edge Case Handling Module

This package provides specialized encoding schemes and lambda calculus utilities
for handling edge cases in geometric operations.

Main Components:
- scott_encoding: Scott and Mogensen-Scott encoding for algebraic data types
- lambda_calculus: Lambda calculus operations and transformations
"""

from .scott_encoding import (
    ScottEncoding,
    scott_pair,
    scott_fst,
    scott_snd,
    scott_list,
    scott_nil,
    scott_cons,
)

__all__ = [
    'ScottEncoding',
    'scott_pair',
    'scott_fst',
    'scott_snd',
    'scott_list',
    'scott_nil',
    'scott_cons',
]
