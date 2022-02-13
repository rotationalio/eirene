import uuid
import random

from crdt.gcounter import GCounter

SEED = 42

class TestGCounter():
    """
    Tests for the GCounter CRDT.
    """

    def randomGCounter(self):
        counter = GCounter(id=uuid.uuid4())
        for i in range(random.randint(0, 100)):
            counter.add(random.randint(0, 100))
        return counter

    def test_counter(self):
        """
        Test that the basic operations work. This uses different IDs for the counters
        to represent different nodes.
        """
        a = GCounter(id=uuid.uuid4())
        a.add(1)
        a.add(2)
        a.add(3)
        assert a.get() == 6

        b = GCounter(id=uuid.uuid4())
        b.add(4)
        assert b.get() == 4

        c = GCounter(id=uuid.uuid4())
        c.add(10)
        assert c.get() == 10

        assert a.merge(b).get() == 10
        assert b.merge(c).get() == 14


    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGCounter()
            b = self.randomGCounter()
            c = self.randomGCounter()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.counts == right.counts
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGCounter()
            b = self.randomGCounter()
            left = a.merge(b)
            right = b.merge(a)
            assert left.counts == right.counts
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = self.randomGCounter()
            left = a.merge(a)
            right = a
            assert left.counts == right.counts
            assert left.get() == right.get()