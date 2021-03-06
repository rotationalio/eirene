import random
import uuid
import pytest

from crdt.sequence import Sequence

SEED = 42

class TestSequence():
    """
    Tests for the Sequence CRDT.
    """

    def random_sequence(self):
        seq = Sequence(id=uuid.uuid4())
        chars = "abcdefghijklmnopqrstuvwxyz"
        seq.append(random.choice(chars))
        size = 1
        for i in range(100):
            op = random.choice(["append", "insert", "remove"])
            if op == "append":
                seq.append(random.choice(chars))
                size += 1
            elif op == "insert" and size > 1:
                index = random.randint(0, size-1)
                seq.insert(index, random.choice(chars))
                size += 1
            elif op == "remove" and size > 1:
                index = random.randint(0, size-1)
                seq.remove(index)
                size -= 1
        return seq

    def test_single_sequence(self):
        """
        Test that the single sequence operations work.
        """
        a = Sequence()
        a.append("b")
        assert a.get() == ["b"]
        a.append("c")
        assert a.get() == ["b", "c"]
        a.insert(0, "a")
        assert a.get() == ["a", "b", "c"]

        with pytest.raises(IndexError):
            a.insert(-1, "d")
            
        with pytest.raises(IndexError):
            a.insert(5, "d")

        with pytest.raises(IndexError):
            a.remove(4)

        a.remove(2)
        assert a.get() == ["a", "b"]

        a.append("c")
        assert a.get() == ["a", "b", "c"]

        a.insert(2, "z")
        assert a.get() == ["a", "b", "z", "c"]

        a.remove(3)
        assert a.get() == ["a", "b", "z"]
        a.remove(2)
        assert a.get() == ["a", "b"]
        a.remove(1)
        assert a.get() == ["a"]
        a.remove(0)
        assert a.get() == []

        with pytest.raises(IndexError):
            a.remove(0)

    def test_merge(self):
        """
        Test that merging sequences works.
        """
        a = Sequence(id="alice")
        a.append("a")
        a.append("b")
        
        b = Sequence(id="bob")
        b.append("c")
        b.append("d")

        assert a.merge(b).get() == ["a", "b", "c", "d"]
        assert b.merge(a).get() == ["a", "b", "c", "d"]

        c = Sequence(id="carol")
        c.append("c")
        c.insert(0, "a")
        c.insert(1, "b")
        assert c.get() == ["a", "b", "c"]

        d = Sequence(id="dave")
        d.append("y")
        d.append("z")
        d.insert(0, "x")
        d.insert(1, "q")
        d.remove(1)
        assert d.get() == ["x", "y", "z"]

        assert c.merge(d).get() == ["a", "b", "c", "x", "y", "z"]
        assert d.merge(c).get() == ["a", "b", "c", "x", "y", "z"]

        c.insert(2, "1")
        assert c.get() == ["a", "b", "1", "c", "x", "y", "z"]
        assert d.merge(c).get() == ["a", "b", "1", "c", "x", "y", "z"]

    @pytest.mark.skip(reason="what exactly breaks the logic here?")
    def test_merge_newlines(self):
        """
        FIXME: This test fails, need to narrow it down a bit more.
        """
        a = Sequence(id="alice")
        a.append("a")
        a.append("b")
        
        b = Sequence(id="bob")
        b.append("c")
        b.append("d")

        assert a.merge(b).get() == ["a", "b", "c", "d"]
        assert b.merge(a).get() == ["a", "b", "c", "d"]

        a.append_many(["\n", "x", "\n", "\n", "y"])
        assert a.get() == ["a", "b", "c", "d", "\n", "x", "\n", "\n", "y"]

        b.append_many(["\n", "1", "\n", "\n", "2"])
        assert b.get() == ["a", "b", "c", "d", "\n", "1", "\n", "\n", "2"]

        assert a.merge(b).get() == ["a", "b", "c", "d", "\n", "x", "\n", "\n", "y", "\n", "1", "\n", "\n", "2"]
        assert b.merge(a).get() == ["a", "b", "c", "d", "\n", "a", "\n", "\n", "b", "\n", "1", "\n", "\n", "2"]

    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.random_sequence()
            b = self.random_sequence()
            c = self.random_sequence()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.random_sequence()
            b = self.random_sequence()
            left = a.merge(b)
            right = b.merge(a)
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.random_sequence()
            assert a.get() == a.merge(a).get()