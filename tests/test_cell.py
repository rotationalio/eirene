import random
import uuid

from notebook.cell import Cell

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
        assert a.get() == "this is the first line\nthis is the second line"

        a.remove(1)
        assert a.get() == "this is the first line"

        a.insert_chars(0, 11, " edited")
        assert a.get() == "this is the edited first line"

        a.insert(0, "this is an inserted line")
        assert a.get() == "this is an inserted line\nthis is the edited first line"

        a.append_chars(1, " -- append to the second line")
        assert a.get() == "this is an inserted line\nthis is the edited first line -- append to the second line"

        a.remove_chars(0, 5, 3)
        assert a.get() == "this an inserted line\nthis is the edited first line -- append to the second line"