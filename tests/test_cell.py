import random
import uuid

from notebook.cell import Cell
from tests.fixtures import generate

SEED = 42

class TestCell():
    """
    Tests for the Cell class.
    """

    def test_single_cell(self):
        """
        Test that the single cell operations work.
        """
        a = Cell()
        a.append("this is the first line")
        a.append("this is the second line")
        assert a.get() == ["this is the first line", "this is the second line"]

        a.remove(1)
        assert a.get() == ["this is the first line"]

        a.insert_chars(0, 11, " edited")
        assert a.get() == ["this is the edited first line"]

        a.insert(0, "this is an inserted line")
        assert a.get() == ["this is an inserted line", "this is the edited first line"]

        a.append_chars(1, " -- append to the second line")
        assert a.get() == ["this is an inserted line", "this is the edited first line -- append to the second line"]

        a.remove_chars(0, 5, 3)
        assert a.get() == ["this an inserted line", "this is the edited first line -- append to the second line"]

    def test_merge(self):
        """
        Test that merging cells works.
        """
        a = Cell(id="alice")
        a.append("Alice line 1")
        a.append("Alice line 2")
        
        b = Cell(id="bob")
        b.append("Bob line 1")
        b.append("Bob line 2")

        assert a.merge(b).get() == ["Alice line 1", "Bob line 1", "Alice line 2", "Bob line 2"]
        assert b.merge(a).get() == ["Alice line 1", "Bob line 1", "Alice line 2", "Bob line 2"]

        c = Cell(id="carol")
        c.append("Carol initial line")
        c.insert(0, "Carol insert before line 1")
        c.insert(1, "Carol insert before line 2")
        assert c.get() == ["Carol insert before line 1", "Carol insert before line 2", "Carol initial line"]

        d = Cell(id="dave")
        d.append("Dave initial line")
        d.append("Dave second line")
        d.append_chars(1, " -- Dave append to second line")
        d.insert(0, "Dave insert before line 1")
        d.insert(1, "Dave insert before line 2")
        d.remove(1)
        assert d.get() == ["Dave insert before line 1", "Dave initial line", "Dave second line -- Dave append to second line"]
        
        merged = [
            "Carol insert before line 1",
            "Carol insert before line 2",
            "Carol initial line",
            "Dave insert before line 1",
            "Dave initial line",
            "Dave second line -- Dave append to second line",
        ]
        assert c.merge(d).get() == merged
        assert d.merge(c).get() == merged

        c.insert(5, "Carol insert before line 6")
        c.remove_chars(6, 20, 5)
        after_insert = [
            "Carol insert before line 1",
            "Carol insert before line 2",
            "Carol initial line",
            "Dave insert before line 1",
            "Dave initial line",
            "Carol insert before line 6",
            "Dave second line -- append to second line",
        ]
        assert c.get() == after_insert
        assert d.merge(c).get() == after_insert

    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_cell()
            b = generate.random_cell()
            c = generate.random_cell()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_cell()
            b = generate.random_cell()
            left = a.merge(b)
            right = b.merge(a)
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_cell()
            assert a.get() == a.merge(a).get()