import random

from crdt.gset import GSet

SEED = 42

class TestGSet():
    """
    Tests for the GSet CRDT.
    """

    def randomGSet(self):
        set = GSet()
        for b in random.randbytes(100):
            set.add(b)
        return set

    def test_set(self):
        """
        Test that the basic operations work.
        """
        a = GSet()
        a.add("a")
        a.add("b")
        a.add("c")
        assert a.get() == {"a", "b", "c"}

        b = GSet()
        b.add("a")
        b.add(1)
        assert b.get() == {"a", 1}

        assert a.merge(b).get() == {"a", "b", "c", 1}

    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGSet()
            b = self.randomGSet()
            c = self.randomGSet()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGSet()
            b = self.randomGSet()
            left = a.merge(b)
            right = b.merge(a)
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGSet()
            left = a.merge(a)
            right = a
            assert left.get() == right.get()