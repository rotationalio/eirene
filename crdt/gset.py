class GSet():
    """
    GSet implements a grow-only set CRDT. Items can be added to the set but can't be
    removed.
    """
    
    def __init__(self):
        self.items = set()

    def add(self, item):
        """
        Adds an item to the set.
        """
        self.items.add(item)

    def merge(self, other):
        """
        Merges another GSet with this one.
        """
        if not isinstance(other, GSet):
            raise ValueError("Incompatible CRDT for merge(), expected GSet")
        self.items = self.items.union(other.items)
        return self

    def get(self):
        """
        Returns the current items in the set.
        """
        return self.items