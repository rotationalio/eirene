from functools import cmp_to_key
from re import S
import uuid
from enum import Enum

from crdt.gset import GSet
from crdt.gcounter import GCounter

class Sequence():
    """
    Sequence is a CRDT that represents an ordered set of objects and supports insertion
    and removal at arbitrary positions in the set.
    """

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.operations = GSet()
        self.clock = GCounter(self.id)
        self.sequence = []

    def compare_operations(self, a, b):
        """
        Compares this Operation to another Operation to determine ordering.
        """
        return a.owner.compare(b.owner)

    def index_transform(self, position):
        """
        Returns the transformed index, which is the actual index of the object in the
        sequence, taking into account tombstones.
        """
        if position < 0 or position >= len(self.sequence):
            raise IndexError("Index out of bounds")

        index = -1
        while position >= 0:
            index += 1
            if not self.sequence[index].tombstone:
                position -= 1
        return index

    def append(self, object):
        """
        Appends an item to the end of the sequence.
        """
        
        # Tick the clock
        self.clock.add(1)

        # Add the insert operation to the log and update the sequence
        op = Operation(OpId(self.id, self.clock.get()), OperationType.INSERT, None, payload=object)
        self.operations.add(op)
        op.do(self.sequence)

    def insert(self, position, object):
        """
        Inserts an item to the sequence at the specified position. The position is a
        0-based index from the perspective of the caller (e.g., does not count deleted
        objects). This makes it easier for the caller to make insertions because the
        caller does not have to keep track of object IDs.
        """

        # Tick the clock
        self.clock.add(1)

        index = self.index_transform(position)
        target = self.sequence[index].operation
        op_id = self.clock.get()

        # Add the insert operation to the log and update the sequence
        op = Operation(OpId(self.id, op_id), OperationType.INSERT, target, payload=object)
        self.operations.add(op)
        op.do(self.sequence)

    def remove(self, position):
        """
        Removes an item from the set at the specified position. The position must be
        within bounds of the current sequence, or this raises an IndexError.
        """
        # Tick the clock
        self.clock.add(1)

        index = self.index_transform(position)
        target = self.sequence[index].operation
        op_id = self.clock.get()

        # Add the remove operation to the log and update the sequence
        op = Operation(OpId(self.id, op_id), OperationType.REMOVE, target)
        self.operations.add(op)
        op.do(self.sequence)

    def merge(self, other):
        """
        Merges another Sequence with this one.
        """
        if not isinstance(other, Sequence):
            raise ValueError("Incompatible CRDT for merge(), expected Sequence")
        
        # Sync the local clock with the remote clock
        self.clock = self.clock.merge(other.clock)

        # Get the new operations to be applied
        patch_ops = other.operations.get().difference(self.operations.get())
        
        # Get a sorted view of the patches to apply
        patch_log = sorted(patch_ops, key=cmp_to_key(self.compare_operations))

        # Path the sequence using the new operations
        for op in patch_log:
            op.do(self.sequence)

        # Merge the two operation logs
        self.operations = self.operations.merge(other.operations)
        return self

    def get(self):
        """
        Returns the sorted list of payloads in the sequence.
        """
        return [obj.operation.payload for obj in self.sequence if not obj.tombstone]

class Object():
    """
    An Object represents a single item in a Sequence.
    """
    
    def __init__(self, operation):
        self.operation = operation
        self.tombstone = False

    def print(self):
        """
        Prints the object to stdout.
        """
        print("owner: {}, payload: {}, tombstone: {}".format(self.operation.owner.print(), self.operation.payload, self.tombstone))

class OpId():
    """
    An OpId represents a unique identifier for an Operation.
    """

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def compare(self, other):
        if self.id < other.id:
            return -1
        elif self.id > other.id:
            return 1
        else:
            # Conflicts are resolved arbitrarily by comparing the owner IDs
            # TODO: We could handle "forks" of the operation log and allow for multiple
            # histories to be valid.
            if self.name < other.name:
                return -1
            elif self.name > other.name:
                return 1
            else:
                return 0

    def is_earlier(self, other):
        """
        Returns true if this OpId is earlier than the other OpId.
        """
        return self.compare(other) < 0

    def __eq__(self, other):
        if not isinstance(other, OpId):
            return False
        return self.name == other.name and self.id == other.id

    def print(self):
        """
        Prints the OpId to stdout.
        """
        return "name: {}, id: {}".format(self.name, self.id)

class OperationType(Enum):
    """
    Enum for operations.
    """
    INSERT = 0
    REMOVE = 1

class Operation():
    """
    An Operation represents a point-in-time change to a Sequence. Every Operation
    has a globally-unique ID and references a previous Operation, enabling an order of
    Operations to be imposed.
    """

    def __init__(self, owner, action, target, payload=None):
        if action not in OperationType:
            raise ValueError("Invalid operation type")
        self.owner = owner
        self.action = action
        self.target = target
        self.payload = payload

    def do(self, objects):
        """
        Applies this Operation to an ordered list of objects.
        """
        # Iterate through the sequence to find the index of the target object
        stomp = False
        if self.target is None:
            # Special case: Append at the end
            index = len(objects)
            while index > 0:
                op = objects[index-1].operation
                if op.target is None and not self.owner.is_earlier(op.owner):
                    # We found another operation older than us, so stop iteration.
                    break
                index -= 1
        else:
            # Normal case: Find the object to insert before
            index = 0
            while index < len(objects):
                op = objects[index].operation
                if op.target == self.target and self.owner.is_earlier(op.owner):
                    # We found another operation older than us, so stop iteration.
                    break
                elif op == self.target:
                    # We found the target index
                    break
                index += 1

        # Perform the operation at the index
        if self.action == OperationType.INSERT:
            obj = Object(self)
            if index < len(objects):
                objects.insert(index, obj)
            else:
                objects.append(obj)
        elif self.action == OperationType.REMOVE:
            # We need to keep the object around so that future operations can reference
            # it, so we mark it as deleted
            if index == len(objects):
                raise IndexError("Could not find object to remove")
            objects[index].tombstone = True

    def print(self):
        """
        Prints the Operation to stdout.
        """
        print("owner: {}, action: {}, target: {}, payload: {}".format(self.owner.print(), self.action, self.target, self.payload))