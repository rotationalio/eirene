import uuid

from crdt.sequence import Sequence

class DistributedNotebook():
    """
    DistributedNotebook is a notebook designed for asynchronous collaboration. It
    consists of CRDT data structures which enable consistent merges between replicas.
    """

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.cells = Sequence(uuid.uuid4())
    
    def append(self, cell):
        """
        Appends a cell to the end of the notebook.
        """
        self.cells.append(cell)

    def insert(self, index, cell):
        """
        Inserts a cell at the specified index.
        """
        self.cells.insert(index, cell)

    def remove(self, index):
        """
        Removes a cell at the specified index.
        """
        self.cells.remove(index)

    def merge(self, other):
        """
        Merges another DistributedNotebook with this one.
        """
        if not isinstance(other, DistributedNotebook):
            raise ValueError("Incompatible CRDT for merge(), expected DistributedNotebook")
        self.cells = self.cells.merge(other.cells)
        return self