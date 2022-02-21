from crdt.gset import GSet

class TwoPhaseSet:
    """
    TwoPhaseSet implements a two-phase set CRDT, which includes an added set and a
    removed set.
    """

    def __init__(self):
        self.added = GSet()
        self.removed = GSet()

    def add(self, item):
        """
        Adds an item to the set.
        """
        self.added.add(item)

    def remove(self, item):
        """
        Removes an item from the set.
        """
        self.removed.add(item)

    def merge(self, other):
        """
        Merges another TwoPhaseSet with this one.
        """
        if not isinstance(other, TwoPhaseSet):
            raise ValueError("Incompatible CRDT for merge(), expected TwoPhaseSet")
        self.added = self.added.merge(other.added)
        self.removed = self.removed.merge(other.removed)
        return self

    def get(self):
        """
        Returns the current items in the set.
        """
        return self.added.get().difference(self.removed.get())