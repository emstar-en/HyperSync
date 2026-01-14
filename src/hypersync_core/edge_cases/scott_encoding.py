"""
Scott Encoding for Algebraic Data Types

Scott encoding is a technique for representing algebraic data types using
lambda calculus. It enables efficient pattern matching in O(1) time by
encoding data structures as their own eliminators.

Key Concepts:
- Scott encoding: Data as elimination function (pattern match directly)
- Church encoding: Data as iteration/fold (requires full traversal)
- Mogensen-Scott: Hybrid approach combining both advantages

Scott encodings enable:
- O(1) pattern matching (vs O(n) for Church)
- Efficient head/tail operations on lists
- Direct projection for pairs
- Lazy evaluation friendly

References:
- Mogensen "Efficient Self-Interpretations in Lambda Calculus" (1992)
- Parigot "Recursive Programming with Proofs" (1992)
"""

import numpy as np
from typing import Any, Callable, Optional, Union, List, Tuple, TypeVar
import functools

T = TypeVar('T')
U = TypeVar('U')


class ScottEncoding:
    """
    Scott encoding utilities for algebraic data types.
    
    This class provides methods for encoding and manipulating data structures
    using Scott encoding, enabling efficient pattern matching.
    """
    
    @staticmethod
    def scott_pair(x: T, y: U) -> Callable[[Callable], Any]:
        """
        Construct a Scott-encoded pair.
        
        Scott pair encoding:
            pair(x, y) = λf. f x y
        
        This allows O(1) projection:
            fst p = p (λx y. x)
            snd p = p (λx y. y)
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            Scott-encoded pair function
            
        Example:
            >>> p = ScottEncoding.scott_pair(1, 2)
            >>> first = p(lambda x, y: x)
            >>> print(first)  # Output: 1
        """
        def pair_elim(f: Callable) -> Any:
            return f(x, y)
        return pair_elim
    
    @staticmethod
    def scott_fst(pair: Callable) -> Any:
        """
        Extract first element from Scott pair in O(1) time.
        
        Args:
            pair: Scott-encoded pair
            
        Returns:
            First element
        """
        return pair(lambda x, y: x)
    
    @staticmethod
    def scott_snd(pair: Callable) -> Any:
        """
        Extract second element from Scott pair in O(1) time.
        
        Args:
            pair: Scott-encoded pair
            
        Returns:
            Second element
        """
        return pair(lambda x, y: y)
    
    @staticmethod
    def scott_nil() -> Callable:
        """
        Construct Scott-encoded empty list.
        
        Scott nil encoding:
            nil = λn c. n
        
        Args:
            None
            
        Returns:
            Scott-encoded empty list
        """
        def nil_elim(n: Callable, c: Callable) -> Any:
            return n()
        return nil_elim
    
    @staticmethod
    def scott_cons(head: T, tail: Callable) -> Callable:
        """
        Construct Scott-encoded cons cell.
        
        Scott cons encoding:
            cons(h, t) = λn c. c h t
        
        This allows O(1) pattern matching:
            is_nil xs = xs (λ. True) (λh t. False)
            head xs = xs (λ. error) (λh t. h)
            tail xs = xs (λ. error) (λh t. t)
        
        Args:
            head: List head element
            tail: Scott-encoded tail list
            
        Returns:
            Scott-encoded cons cell
        """
        def cons_elim(n: Callable, c: Callable) -> Any:
            return c(head, tail)
        return cons_elim
    
    @staticmethod
    def scott_list(elements: List[T]) -> Callable:
        """
        Construct Scott-encoded list from Python list.
        
        Args:
            elements: Python list of elements
            
        Returns:
            Scott-encoded list
            
        Example:
            >>> lst = ScottEncoding.scott_list([1, 2, 3])
            >>> head = ScottEncoding.scott_head(lst)
            >>> print(head)  # Output: 1
        """
        if not elements:
            return ScottEncoding.scott_nil()
        
        result = ScottEncoding.scott_nil()
        for elem in reversed(elements):
            result = ScottEncoding.scott_cons(elem, result)
        return result
    
    @staticmethod
    def scott_is_nil(lst: Callable) -> bool:
        """
        Check if Scott list is empty in O(1) time.
        
        Args:
            lst: Scott-encoded list
            
        Returns:
            True if empty, False otherwise
        """
        return lst(lambda: True, lambda h, t: False)
    
    @staticmethod
    def scott_head(lst: Callable) -> Any:
        """
        Extract head of Scott list in O(1) time.
        
        Args:
            lst: Scott-encoded list
            
        Returns:
            Head element
            
        Raises:
            ValueError: If list is empty
        """
        def error():
            raise ValueError("Cannot take head of empty list")
        return lst(error, lambda h, t: h)
    
    @staticmethod
    def scott_tail(lst: Callable) -> Callable:
        """
        Extract tail of Scott list in O(1) time.
        
        Args:
            lst: Scott-encoded list
            
        Returns:
            Scott-encoded tail list
            
        Raises:
            ValueError: If list is empty
        """
        def error():
            raise ValueError("Cannot take tail of empty list")
        return lst(error, lambda h, t: t)
    
    @staticmethod
    def scott_maybe_nothing() -> Callable:
        """
        Construct Scott-encoded Nothing (Option/Maybe type).
        
        Scott maybe encoding:
            nothing = λn j. n
            just(x) = λn j. j x
        
        Returns:
            Scott-encoded Nothing
        """
        def nothing_elim(n: Callable, j: Callable) -> Any:
            return n()
        return nothing_elim
    
    @staticmethod
    def scott_maybe_just(value: T) -> Callable:
        """
        Construct Scott-encoded Just value.
        
        Args:
            value: Value to wrap
            
        Returns:
            Scott-encoded Just value
        """
        def just_elim(n: Callable, j: Callable) -> Any:
            return j(value)
        return just_elim
    
    @staticmethod
    def scott_either_left(value: T) -> Callable:
        """
        Construct Scott-encoded Left (Either/Sum type).
        
        Scott either encoding:
            left(x) = λl r. l x
            right(y) = λl r. r y
        
        Args:
            value: Left value
            
        Returns:
            Scott-encoded Left
        """
        def left_elim(l: Callable, r: Callable) -> Any:
            return l(value)
        return left_elim
    
    @staticmethod
    def scott_either_right(value: U) -> Callable:
        """
        Construct Scott-encoded Right.
        
        Args:
            value: Right value
            
        Returns:
            Scott-encoded Right
        """
        def right_elim(l: Callable, r: Callable) -> Any:
            return r(value)
        return right_elim
    
    @staticmethod
    def scott_pattern_match(data: Callable, *cases: Callable) -> Any:
        """
        Perform efficient O(1) pattern matching on Scott-encoded data.
        
        Scott encoding enables direct pattern matching by encoding data
        structures as their own eliminators.
        
        Args:
            data: Scott-encoded data structure
            *cases: Case handlers (functions)
            
        Returns:
            Result of pattern matching
            
        Example:
            >>> p = scott_pair(1, 2)
            >>> result = scott_pattern_match(p, lambda x, y: x + y)
            >>> print(result)  # Output: 3
        """
        return data(*cases)
    
    @staticmethod
    def scott_nat_zero() -> Callable:
        """
        Construct Scott-encoded natural number zero.
        
        Scott natural encoding:
            zero = λz s. z
            succ(n) = λz s. s n
        
        Returns:
            Scott-encoded zero
        """
        def zero_elim(z: Callable, s: Callable) -> Any:
            return z()
        return zero_elim
    
    @staticmethod
    def scott_nat_succ(n: Callable) -> Callable:
        """
        Construct Scott-encoded successor.
        
        Args:
            n: Scott-encoded natural number
            
        Returns:
            Scott-encoded successor
        """
        def succ_elim(z: Callable, s: Callable) -> Any:
            return s(n)
        return succ_elim
    
    @staticmethod
    def scott_nat_from_int(n: int) -> Callable:
        """
        Convert Python integer to Scott-encoded natural number.
        
        Args:
            n: Non-negative integer
            
        Returns:
            Scott-encoded natural number
            
        Raises:
            ValueError: If n < 0
        """
        if n < 0:
            raise ValueError(f"Natural number must be non-negative, got {n}")
        
        result = ScottEncoding.scott_nat_zero()
        for _ in range(n):
            result = ScottEncoding.scott_nat_succ(result)
        return result
    
    @staticmethod
    def scott_nat_to_int(n: Callable) -> int:
        """
        Convert Scott-encoded natural number to Python integer.
        
        Args:
            n: Scott-encoded natural number
            
        Returns:
            Python integer
        """
        count = 0
        def zero_case():
            return count
        def succ_case(pred):
            nonlocal count
            count += 1
            return ScottEncoding.scott_nat_to_int(pred)
        return n(zero_case, succ_case)
    
    @staticmethod
    def scott_nat_fold(n: Callable, zero_val: T, succ_fn: Callable[[T], T]) -> T:
        """
        Fold over Scott-encoded natural number.
        
        This is the catamorphism for natural numbers, enabling recursion.
        
        Args:
            n: Scott-encoded natural number
            zero_val: Value for zero case
            succ_fn: Function for successor case
            
        Returns:
            Folded result
            
        Example:
            >>> three = scott_nat_from_int(3)
            >>> result = scott_nat_fold(three, 0, lambda x: x + 1)
            >>> print(result)  # Output: 3
        """
        def zero_case():
            return zero_val
        def succ_case(pred):
            return succ_fn(ScottEncoding.scott_nat_fold(pred, zero_val, succ_fn))
        return n(zero_case, succ_case)
    
    @staticmethod
    def scott_tree_leaf(value: T) -> Callable:
        """
        Construct Scott-encoded tree leaf.
        
        Scott tree encoding:
            leaf(x) = λl n. l x
            node(l, r) = λl n. n l r
        
        Args:
            value: Leaf value
            
        Returns:
            Scott-encoded leaf
        """
        def leaf_elim(l: Callable, n: Callable) -> Any:
            return l(value)
        return leaf_elim
    
    @staticmethod
    def scott_tree_node(left: Callable, right: Callable) -> Callable:
        """
        Construct Scott-encoded tree node.
        
        Args:
            left: Left subtree
            right: Right subtree
            
        Returns:
            Scott-encoded node
        """
        def node_elim(l: Callable, n: Callable) -> Any:
            return n(left, right)
        return node_elim
    
    @staticmethod
    def scott_tree_fold(tree: Callable, leaf_fn: Callable, node_fn: Callable) -> Any:
        """
        Fold over Scott-encoded tree (catamorphism).
        
        Visits each node exactly once in O(n) time.
        
        Args:
            tree: Scott-encoded tree
            leaf_fn: Function for leaf case
            node_fn: Function for node case
            
        Returns:
            Folded result
            
        Example:
            >>> leaf1 = scott_tree_leaf(1)
            >>> leaf2 = scott_tree_leaf(2)
            >>> tree = scott_tree_node(leaf1, leaf2)
            >>> sum_tree = scott_tree_fold(
            ...     tree,
            ...     lambda x: x,
            ...     lambda l, r: l + r
            ... )
        """
        def leaf_case(value):
            return leaf_fn(value)
        def node_case(left, right):
            left_result = ScottEncoding.scott_tree_fold(left, leaf_fn, node_fn)
            right_result = ScottEncoding.scott_tree_fold(right, leaf_fn, node_fn)
            return node_fn(left_result, right_result)
        return tree(leaf_case, node_case)


# Convenience functions

def scott_pair(x: T, y: U) -> Callable:
    """Convenience function for creating Scott-encoded pair."""
    return ScottEncoding.scott_pair(x, y)


def scott_fst(pair: Callable) -> Any:
    """Convenience function for extracting first element."""
    return ScottEncoding.scott_fst(pair)


def scott_snd(pair: Callable) -> Any:
    """Convenience function for extracting second element."""
    return ScottEncoding.scott_snd(pair)


def scott_list(elements: List[T]) -> Callable:
    """Convenience function for creating Scott-encoded list."""
    return ScottEncoding.scott_list(elements)


def scott_nil() -> Callable:
    """Convenience function for empty Scott list."""
    return ScottEncoding.scott_nil()


def scott_cons(head: T, tail: Callable) -> Callable:
    """Convenience function for Scott cons."""
    return ScottEncoding.scott_cons(head, tail)
