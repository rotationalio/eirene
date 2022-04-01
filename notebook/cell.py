import uuid

from crdt.sequence import Sequence

class Cell():
    """
    Cell represents the contents of a cell in a DistributedNotebook.
    """

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.lines = Sequence(id)

    def append(self, line):
        """
        Appends a line to the end of a cell.
        """
        seq = Sequence(uuid.uuid4())
        for ch in line:
            seq.append(ch)
        self.lines.append(seq)
    
    def insert(self, index, line):
        """
        Inserts a line at the specified index.
        """
        seq = Sequence(uuid.uuid4())
        for ch in line:
            seq.append(ch)
        self.lines.insert(index, seq)

    def remove(self, index):
        """
        Removes a line at the specified index.
        """
        self.lines.remove(index)

    def append_chars(self, line_num, chars):
        """
        Appends a set of characters to the specified line.
        """
        for ch in chars:
            self.lines.get()[line_num].append(ch)

    def insert_chars(self, line_num, char_num, chars):
        """
        Inserts a set of characters at the specified line.
        """
        for ch in chars:
            self.lines.get()[line_num].insert(char_num, ch)
            char_num += 1

    def remove_chars(self, line_num, char_num, num_chars):
        """
        Removes a set of character from the specified line.
        """
        for i in range(num_chars):
            self.lines.get()[line_num].remove(char_num)

    def merge(self, other):
        """
        Merges another Cell with this one.
        """
        if not isinstance(other, Cell):
            raise ValueError("Incompatible CRDT for merge(), expected Cell")
        self.lines = self.lines.merge(other.lines)
        return self

    def get(self):
        """
        Returns all the lines in the cell.
        """
        return [''.join(line.get()) for line in self.lines.get()]
            
