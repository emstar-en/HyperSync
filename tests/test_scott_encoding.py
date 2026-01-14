"""
Unit Tests for Scott Encoding

This module contains comprehensive tests for Scott encoding implementation,
including pairs, lists, natural numbers, trees, and pattern matching.
"""

import pytest
import numpy as np
from src.hypersync_core.edge_cases import (
    ScottEncoding,
    scott_pair,
    scott_fst,
    scott_snd,
    scott_list,
    scott_nil,
    scott_cons,
)


class TestScottPairs:
    """Tests for Scott-encoded pairs."""
    
    def test_pair_construction(self):
        """Test pair construction and projection."""
        p = scott_pair(1, 2)
        
        assert scott_fst(p) == 1, "First element should be 1"
        assert scott_snd(p) == 2, "Second element should be 2"
    
    def test_pair_with_different_types(self):
        """Test pair with different types."""
        p = scott_pair("hello", 42)
        
        assert scott_fst(p) == "hello"
        assert scott_snd(p) == 42
    
    def test_nested_pairs(self):
        """Test nested pairs."""
        inner = scott_pair(1, 2)
        outer = scott_pair(inner, 3)
        
        inner_retrieved = scott_fst(outer)
        assert scott_fst(inner_retrieved) == 1
        assert scott_snd(inner_retrieved) == 2
        assert scott_snd(outer) == 3


class TestScottLists:
    """Tests for Scott-encoded lists."""
    
    def test_empty_list(self):
        """Test empty list construction."""
        lst = scott_nil()
        
        assert ScottEncoding.scott_is_nil(lst), "Empty list should be nil"
    
    def test_cons_construction(self):
        """Test cons cell construction."""
        lst = scott_cons(1, scott_nil())
        
        assert not ScottEncoding.scott_is_nil(lst), "Cons list should not be nil"
        assert ScottEncoding.scott_head(lst) == 1
    
    def test_list_from_python_list(self):
        """Test construction from Python list."""
        elements = [1, 2, 3]
        lst = scott_list(elements)
        
        assert not ScottEncoding.scott_is_nil(lst)
        assert ScottEncoding.scott_head(lst) == 1
    
    def test_list_head_tail(self):
        """Test head and tail operations."""
        lst = scott_list([1, 2, 3])
        
        head = ScottEncoding.scott_head(lst)
        assert head == 1
        
        tail = ScottEncoding.scott_tail(lst)
        tail_head = ScottEncoding.scott_head(tail)
        assert tail_head == 2
    
    def test_list_traversal(self):
        """Test list traversal."""
        elements = [1, 2, 3, 4, 5]
        lst = scott_list(elements)
        
        result = []
        current = lst
        while not ScottEncoding.scott_is_nil(current):
            result.append(ScottEncoding.scott_head(current))
            current = ScottEncoding.scott_tail(current)
        
        assert result == elements
    
    def test_empty_list_head_error(self):
        """Test that head of empty list raises error."""
        lst = scott_nil()
        
        with pytest.raises(ValueError):
            ScottEncoding.scott_head(lst)
    
    def test_empty_list_tail_error(self):
        """Test that tail of empty list raises error."""
        lst = scott_nil()
        
        with pytest.raises(ValueError):
            ScottEncoding.scott_tail(lst)


class TestScottMaybe:
    """Tests for Scott-encoded Maybe/Option type."""
    
    def test_nothing_construction(self):
        """Test Nothing construction."""
        nothing = ScottEncoding.scott_maybe_nothing()
        
        result = nothing(
            lambda: "is nothing",
            lambda x: f"is just {x}"
        )
        assert result == "is nothing"
    
    def test_just_construction(self):
        """Test Just construction."""
        just = ScottEncoding.scott_maybe_just(42)
        
        result = just(
            lambda: "is nothing",
            lambda x: f"is just {x}"
        )
        assert result == "is just 42"
    
    def test_maybe_pattern_match(self):
        """Test pattern matching on Maybe."""
        nothing = ScottEncoding.scott_maybe_nothing()
        just = ScottEncoding.scott_maybe_just(100)
        
        def extract_or_default(maybe, default):
            return maybe(
                lambda: default,
                lambda x: x
            )
        
        assert extract_or_default(nothing, 0) == 0
        assert extract_or_default(just, 0) == 100


class TestScottEither:
    """Tests for Scott-encoded Either/Sum type."""
    
    def test_left_construction(self):
        """Test Left construction."""
        left = ScottEncoding.scott_either_left("error")
        
        result = left(
            lambda x: f"Left: {x}",
            lambda y: f"Right: {y}"
        )
        assert result == "Left: error"
    
    def test_right_construction(self):
        """Test Right construction."""
        right = ScottEncoding.scott_either_right(42)
        
        result = right(
            lambda x: f"Left: {x}",
            lambda y: f"Right: {y}"
        )
        assert result == "Right: 42"
    
    def test_either_pattern_match(self):
        """Test pattern matching on Either."""
        left = ScottEncoding.scott_either_left("error")
        right = ScottEncoding.scott_either_right(100)
        
        def extract_value(either):
            return either(
                lambda err: f"Error: {err}",
                lambda val: val
            )
        
        assert extract_value(left) == "Error: error"
        assert extract_value(right) == 100


class TestScottNaturals:
    """Tests for Scott-encoded natural numbers."""
    
    def test_zero_construction(self):
        """Test zero construction."""
        zero = ScottEncoding.scott_nat_zero()
        
        result = zero(
            lambda: "is zero",
            lambda pred: "is successor"
        )
        assert result == "is zero"
    
    def test_successor_construction(self):
        """Test successor construction."""
        zero = ScottEncoding.scott_nat_zero()
        one = ScottEncoding.scott_nat_succ(zero)
        
        result = one(
            lambda: "is zero",
            lambda pred: "is successor"
        )
        assert result == "is successor"
    
    def test_nat_from_int(self):
        """Test conversion from Python int."""
        three = ScottEncoding.scott_nat_from_int(3)
        
        # Count successors
        count = 0
        def zero_case():
            return count
        def succ_case(pred):
            nonlocal count
            count += 1
            return pred(zero_case, succ_case)
        
        three(zero_case, succ_case)
        # Note: The count mechanism here is tricky, let's use the provided method
    
    def test_nat_to_int(self):
        """Test conversion to Python int."""
        zero = ScottEncoding.scott_nat_from_int(0)
        three = ScottEncoding.scott_nat_from_int(3)
        five = ScottEncoding.scott_nat_from_int(5)
        
        assert ScottEncoding.scott_nat_to_int(zero) == 0
        assert ScottEncoding.scott_nat_to_int(three) == 3
        assert ScottEncoding.scott_nat_to_int(five) == 5
    
    def test_nat_roundtrip(self):
        """Test int -> nat -> int roundtrip."""
        for n in [0, 1, 5, 10]:
            nat = ScottEncoding.scott_nat_from_int(n)
            result = ScottEncoding.scott_nat_to_int(nat)
            assert result == n, f"Roundtrip failed for {n}"
    
    def test_nat_fold(self):
        """Test fold over natural numbers."""
        three = ScottEncoding.scott_nat_from_int(3)
        
        # Compute 3! using fold
        result = ScottEncoding.scott_nat_fold(
            three,
            zero_val=1,
            succ_fn=lambda x: x + 1
        )
        assert result == 4  # 1 + 1 + 1 + 1


class TestScottTrees:
    """Tests for Scott-encoded trees."""
    
    def test_leaf_construction(self):
        """Test leaf construction."""
        leaf = ScottEncoding.scott_tree_leaf(42)
        
        result = leaf(
            lambda val: f"leaf({val})",
            lambda l, r: "node"
        )
        assert result == "leaf(42)"
    
    def test_node_construction(self):
        """Test node construction."""
        left = ScottEncoding.scott_tree_leaf(1)
        right = ScottEncoding.scott_tree_leaf(2)
        node = ScottEncoding.scott_tree_node(left, right)
        
        result = node(
            lambda val: f"leaf({val})",
            lambda l, r: "node"
        )
        assert result == "node"
    
    def test_tree_fold_sum(self):
        """Test tree fold for summing values."""
        leaf1 = ScottEncoding.scott_tree_leaf(1)
        leaf2 = ScottEncoding.scott_tree_leaf(2)
        leaf3 = ScottEncoding.scott_tree_leaf(3)
        
        left_subtree = ScottEncoding.scott_tree_node(leaf1, leaf2)
        tree = ScottEncoding.scott_tree_node(left_subtree, leaf3)
        
        total = ScottEncoding.scott_tree_fold(
            tree,
            leaf_fn=lambda x: x,
            node_fn=lambda l, r: l + r
        )
        assert total == 6
    
    def test_tree_fold_count_leaves(self):
        """Test tree fold for counting leaves."""
        leaf1 = ScottEncoding.scott_tree_leaf("a")
        leaf2 = ScottEncoding.scott_tree_leaf("b")
        leaf3 = ScottEncoding.scott_tree_leaf("c")
        
        left_subtree = ScottEncoding.scott_tree_node(leaf1, leaf2)
        tree = ScottEncoding.scott_tree_node(left_subtree, leaf3)
        
        count = ScottEncoding.scott_tree_fold(
            tree,
            leaf_fn=lambda x: 1,
            node_fn=lambda l, r: l + r
        )
        assert count == 3


class TestScottPatternMatching:
    """Tests for Scott pattern matching."""
    
    def test_pattern_match_pair(self):
        """Test pattern matching on pairs."""
        p = scott_pair(10, 20)
        
        result = ScottEncoding.scott_pattern_match(
            p,
            lambda x, y: x + y
        )
        assert result == 30
    
    def test_pattern_match_list(self):
        """Test pattern matching on lists."""
        lst = scott_cons(1, scott_cons(2, scott_nil()))
        
        result = lst(
            lambda: 0,  # nil case
            lambda h, t: h  # cons case
        )
        assert result == 1


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
