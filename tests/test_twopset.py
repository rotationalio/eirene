import random

from crdt.twopset import TwoPhaseSet

SEED = 42

class TestTwoPhaseSet():
    """
    Tests for the TwoPhaseSet CRDT.
    """

    def randomTwoPhaseSet(self):
        set = TwoPhaseSet()
        chars = "abcdefghijklmnopqrstuvwxyz"
        added = [random.choice(chars) for i in range(10)]
        removed = [random.choice(added) for i in range(3)]
        for i in added:
            set.add(i)
        for i in removed:
            set.remove(i)
        return set

    def test_set(self):
        """
        Test that the basic operations work.
        """
        a = TwoPhaseSet()
        a.add("a")
        a.add("b")
        a.add("c")
        a.remove("b")
        assert a.get() == {"a", "c"}

        b = TwoPhaseSet()
        b.add("a")
        b.add(1)
        assert b.get() == {"a", 1}

        assert a.merge(b).get() == {"a", "c", 1}
        a.remove("a")
        assert a.get() == {"c", 1}

    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomTwoPhaseSet()
            b = self.randomTwoPhaseSet()
            c = self.randomTwoPhaseSet()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomTwoPhaseSet()
            b = self.randomTwoPhaseSet()
            left = a.merge(b)
            right = b.merge(a)
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomTwoPhaseSet()
            left = a.merge(a)
            right = a
            assert left.get() == right.get()