import random
import pytest

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
        a.append_text("this is the first line")
        a.append_text("\nthis is the second line")
        assert a.get_text() == "this is the first line\nthis is the second line"

        a.remove_many(0, 5)
        assert a.get_text() == "is the first line\nthis is the second line"

        a.insert_text(7, "edited ")
        assert a.get_text() == "is the edited first line\nthis is the second line"

    @pytest.mark.parametrize(
        "before,after",
        [
            ("", "abc"),
            ("abc", "ab"),
            ("ab", "def"),
            ("def", "a\nb\nc"),
            ("a\nb\nc", "a\nx\ny"),
            ("abc", "ab\n"),
        ]
    )
    def test_update(self, before, after):
        """
        Test updating a cell with new text content.
        """
        a = Cell()
        a.append_text(before)
        a.update(after)
        assert a.get_text() == after

    def test_update_random(self):
        """
        Test updating a cell with random text data.
        """
        random.seed(SEED)
        a = Cell()
        charset = "abcdefghijklmnopqrstuvwxyz \n"
        for i in range(100):
            text = generate.random_word(charset=charset)
            a.update(text)
            assert a.get_text() == text

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