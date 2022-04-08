import uuid

from crdt.sequence import Sequence
from notebook.cell import Cell

class DistributedNotebook(Sequence):
    """
    DistributedNotebook is a notebook designed for asynchronous collaboration. It
    consists of CRDT data structures which enable consistent merges between replicas.
    """

    def create_cell(self, index=None):
        """
        Creates a new cell at the given index. If the index is not specified, the cell
        is appended to the end of the notebook.
        """
        cell = Cell(id=self.id)
        if index is None:
            self.append(cell)
        else:
            self.insert(index, cell)

    def update_cell(self, index, text):
        """
        Updates the text in a cell with new text.
        """
        self.get()[index].update(text)

    def remove_cell(self, index):
        """
        Removes the cell at the given index.
        """
        self.remove(index)

    def get_cell_data(self):
        """
        Returns all the cell data in the notebook.
        """
        return [cell.get_text() for cell in self.get()]