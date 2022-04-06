import random

from notebook.cell import Cell
from notebook.notebook import DistributedNotebook
from tests.fixtures import generate

SEED = 42
CHARSET = "abcdefghijklmnopqrstuvwxyz"

class TestDistributedNotebook():
    """
    Tests for the DistributedNotebook class.
    """

    def test_single_notebook(self):
        """
        Test that the single notebook operations work.
        """
        book = DistributedNotebook()
        a = Cell(id="alice")
        a.append_text("Alice first line\nAlice second line")
        book.append(a)

        b = Cell(id="bob")
        b.append_text("Bob first line\nBob second line")
        book.append(b)
        assert book.get() == [a, b]

        c = Cell(id="carol")
        c.append_text("Carol first line")
        book.insert(1, c)
        assert book.get() == [a, c, b]

        book.remove(2)
        assert book.get() == [a, c]

    def test_merge(self):
        """
        Test that merging notebooks works.
        """
        book1 = DistributedNotebook(id="book_1")
        a = Cell(id="alice")
        a.append_text("Alice line 1")
        book1.append(a)

        b = Cell(id="bob")
        b.append_text("Bob line 1")
        book1.append(b)
        assert book1.get() == [a, b]

        book2 = DistributedNotebook(id="book_2")
        c = Cell(id="carol")
        c.append_text("Carol line 1")
        book2.append(c)

        d = Cell(id="dave")
        d.append_text("Dave line 1")
        book2.append(d)
        assert book2.get() == [c, d]

        assert book1.merge(book2).get() == [a, c, b, d]

    def test_associative(self):
        """
        Tests that the associative property holds -> A + (B + C) == (A + B) + C.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_notebook()
            b = generate.random_notebook()
            c = generate.random_notebook()
            left = a.merge(b.merge(c))
            right = c.merge(a.merge(b))
            assert left.get() == right.get()

    def test_commutative(self):
        """
        Test that the commutative property holds -> A + B == B + A.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_notebook()
            b = generate.random_notebook()
            left = a.merge(b)
            right = b.merge(a)
            assert left.get() == right.get()

    def test_idempotent(self):
        """
        Test that the idempotent property holds -> A + A == A.
        """
        random.seed(SEED)
        for i in range(100):
            a = generate.random_notebook()
            assert a.get() == a.merge(a).get()