import uuid

class GCounter:
    """
    GCounter implements a grow-only counter CRDT. It must be instantiated with a
    network-unique ID.
    """

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.counts = {id: 0}

    def add(self, value):
        """
        Adds a non-negative value to the counter.
        """
        if value < 0:
            raise ValueError("Only non-negative values are allowed for add()")
        self.counts[self.id] += value

    def merge(self, other):
        """
        Merges another GCounter with this one.
        """
        if not isinstance(other, GCounter):
            raise ValueError("Incompatible CRDT for merge(), expected GCounter")
        for id, count in other.counts.items():
            self.counts[id] = max(self.counts.get(id, 0), count)
        return self

    def get(self):
        """
        Returns the current value of the counter.
        """
        return sum(self.counts.values())