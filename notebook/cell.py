import difflib

from crdt.sequence import Sequence

class Cell(Sequence):
    """
    Cell represents the contents of a cell in a DistributedNotebook.
    """

    def append_text(self, text):
        """
        Appends the given text to the end of the cell.
        """
        self.append_many(list(text))

    def insert_text(self, index, text):
        """
        Inserts the given text at the given index.
        """
        self.insert_many(index, list(text))

    def update(self, text):
        """
        Updates the text in the cell with the given text. Internally, this method
        calculates the diff between the current text in the cell and the new text and 
        decomposes the diff into a set of operations which are sequentially applied to
        the cell.
        """
        changes = difflib.ndiff(self.get_text(), text)
        offset = 0
        for i, s in enumerate(changes):
            char_index = i + offset
            if s[0] == '-':
                self.remove(char_index)
                # difflib positions are relative to the original text, so account for
                # the removed character
                offset -= 1
            elif s[0] == '+':
                if char_index >= len(self.get()):
                    self.append(s[-1])
                else:
                    self.insert(char_index, s[-1])

    def get_text(self):
        """
        Returns the text in the cell.
        """
        return ''.join(self.get())
            
