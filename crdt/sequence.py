from functools import cmp_to_key
import uuid
from enum import Enum

from crdt.gset import GSet
from crdt.gcounter import GCounter
from crdt.tree import ObjectTree

class Sequence():
    """
    Sequence is a CRDT that represents an ordered set of objects and supports insertion
    and removal at arbitrary positions in the set.
    """

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.operations = GSet()
        self.clock = GCounter(self.id)
        self.sequence = ObjectTree()

    def compare_operations(self, a, b):
        """
        Compares two Operation objects to determine their ordering. This method
        compares the operation IDs of two operations a,b and returns -1 if a < b,
        0 if a == b, and 1 if a > b. This allows the method to be used as a custom
        sorting function for the sorted() built-in function.
        """
        return a.owner.compare(b.owner)

    def append(self, item):
        """
        Appends an item to the end of the sequence. This is implemented by applying an
        insert operation at the end of the operation log.
        """
        
        # Tick the clock
        self.clock.add(1)

        objects = self.get_objects()
        if len(self.get()) == 0:
            # Special case: there is no operation to reference
            target = None
            action = OperationType.INSERT_BEFORE
        elif len(objects) == 0:
            # Special case: no visible objects to reference
            target = self.sequence[0].operation
            action = OperationType.INSERT_BEFORE
        else:
            # Insert after the last object in the sequence
            target = objects[-1].operation
            action = OperationType.INSERT_AFTER

        # Add the insert operation to the log and update the sequence
        owner = OpId(self.id, self.clock.get())
        op = Operation(owner=owner, action=action, target=target, payload=item)
        self.operations.add(op)
        op.do(self.sequence)

    def append_many(self, items):
        """
        Appends an iterable of items to the end of the sequence.
        """
        for item in items:
            self.append(item)

    def object_at_position(self, position):
        """
        Returns the object at the specified position. The given position is from the
        perspective of the caller (e.g., does not count deleted objects).
        """
        objects = self.get_objects()
        if position < 0 or position >= len(objects):
            raise IndexError("Position {} out of range of sequence with length {}".format(position, len(objects)))
        return objects[position]

    def insert(self, position, item):
        """
        Inserts an item to the sequence at the specified position. The position is a
        0-based index from the perspective of the caller (e.g., does not count deleted
        objects). This makes it easier for the caller to make insertions because the
        caller does not have to keep track of object IDs.
        """

        # Tick the clock
        self.clock.add(1)

        target = self.object_at_position(position).operation
        owner = OpId(self.id, self.clock.get())

        # Add the insert operation to the log and update the sequence
        op = Operation(owner=owner, action=OperationType.INSERT_BEFORE, target=target, payload=item)
        self.operations.add(op)
        op.do(self.sequence)

    def insert_many(self, position, items):
        """
        Inserts an iterable of objects at the specified position.
        """
        for item in items:
            self.insert(position, item)
            position += 1

    def remove(self, position):
        """
        Removes an item from the set at the specified position. This raises an
        IndexError if the position is out of bounds of the current sequence.
        """
        # Tick the clock
        self.clock.add(1)

        target = self.object_at_position(position).operation
        owner = OpId(self.id, self.clock.get())

        # Add the remove operation to the log and update the sequence
        op = Operation(owner=owner, action=OperationType.REMOVE, target=target)
        self.operations.add(op)
        op.do(self.sequence)

    def remove_many(self, position, count):
        """
        Removes a number of items from the sequence at the specified position.
        """
        for i in range(count):
            self.remove(position)

    def merge(self, other):
        """
        Merges another Sequence with this one.
        """
        if not isinstance(other, Sequence):
            raise ValueError("Incompatible CRDT for merge(), expected Sequence")

        # Merge the two operation logs
        self.merge_operations(other)
        other.merge_operations(self)

        # If we are merging two sequences of sequences, we need to recursively merge
        # each of the sub-sequences.
        this_sequence = self.get()
        other_sequence = other.get()
        for i in range(len(this_sequence)):
            if isinstance(this_sequence[i], Sequence) and isinstance(other_sequence[i], Sequence):
                this_sequence[i].merge(other_sequence[i])
                this_sequence[i].id = self.id

        return self

    def merge_operations(self, other):
        """
        Merge the operation log of another Sequence with this one.
        """

        # Sync the local clock with the remote clock
        self.clock = self.clock.merge(other.clock)

        # Get the new operations to be applied
        patch_ops = other.operations.get().difference(self.operations.get())
        
        # Get a sorted view of the patches to apply
        patch_log = sorted(patch_ops, key=cmp_to_key(self.compare_operations))

        # Patch the sequence using the new operations
        for op in patch_log:
            op.do(self.sequence)

        # Merge the two operation logs
        self.operations = self.operations.merge(other.operations)

    def get_objects(self):
        """
        Returns the sorted list of objects that are not tombstones.
        """
        return [obj for obj in self.sequence if not obj.tombstone]

    def get(self):
        """
        Returns the sorted list of payloads in the sequence that are not tombstones.
        """
        return [obj.operation.payload for obj in self.sequence if not obj.tombstone]

class Object():
    """
    An Object represents a single item in a Sequence.
    """
    
    def __init__(self, operation):
        self.operation = operation
        self.tombstone = False

    def __repr__(self):
        """
        Prints the object to stdout.
        """
        return "owner: {}, payload: {}, tombstone: {}".format(self.operation.owner, self.operation.payload, self.tombstone)

class OpId():
    """
    An OpId represents a unique identifier for an Operation in a Sequence.
    
    node: str
    The name of the node that created the Operation, which is used to resolve conflicts.
    Usually this is a UUID which is assigned when the node is created, and is the same
    for all Operations that the node creates.

    id: int
    The global ID of the Operation, which is used to determine a global ordering of
    Operations. This should be unique across all Operations created by the node,
    ensuring that each (node, ID) pair is also unique. Note that IDs are not unique
    across nodes, but (node, ID) pairs are.
    """

    def __init__(self, node, id):
        self.node = node
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
            if self.node < other.node:
                return -1
            elif self.node > other.node:
                return 1
            else:
                return 0

    def is_earlier(self, other):
        """
        Returns true if this OpId is earlier than the other OpId.
        """
        cmp = self.compare(other)
        if cmp == 0:
            # In order to provide consistent ordering, OpIds need to be universally
            # unique.
            raise ValueError("Found conflicting Operations with the same OpId: ({}, {})".format(self.node, self.id))
        return cmp < 0
    
    def get_hash(self):
        """
        Returns a hash of the OpId.
        """
        return hash((self.node, self.id))

    def __eq__(self, other):
        if not isinstance(other, OpId):
            return False
        return self.node == other.node and self.id == other.id

    def __lt__(self, other):
        if not isinstance(other, OpId):
            return False
        return self.is_earlier(other)

    def __repr__(self):
        """
        Prints the OpId to stdout.
        """
        return "node: {}, id: {}".format(self.node, self.id)

class OperationType(Enum):
    """
    Enum for operations.
    """
    INSERT_BEFORE = 0
    INSERT_AFTER = 1
    REMOVE = 2

class Operation():
    """
    An Operation represents a point-in-time change to a Sequence. Every Operation
    has a globally-unique ID and references a previous Operation, enabling an order of
    Operations to be imposed.

    owner: OpId
    The OpId of the node that created the Operation, which is used to determine
    Operation ordering.

    action: OperationType
    The type of operation, either INSERT or REMOVE.

    target: Operation
    The target of the Operation, which is either a previous Operation or None if
    inserting at the end of a Sequence.

    payload: object
    The payload of the Operation, which is the actual object to be inserted or removed.
    """

    def __init__(self, owner=None, action=None, target=None, payload=None):
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
        obj = Object(self)
        if self.action == OperationType.INSERT_BEFORE:
            objects.insert(self.target, obj, before=True)
        elif self.action == OperationType.INSERT_AFTER:
            objects.insert(self.target, obj, before=False)
        elif self.action == OperationType.REMOVE:
            for obj in objects:
                if obj.operation == self.target:
                    obj.tombstone = True
                    break
        else:
            raise ValueError("Invalid operation type")

        print("Applied operation: {}".format(self))

        print("Resulting sequence: {}".format([obj.operation.payload for obj in objects if not obj.tombstone]))

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False
        return self.owner == other.owner

    def __lt__(self, other):
        if not isinstance(other, Operation):
            return False
        return self.owner < other.owner

    def __hash__(self):
        return hash(self.owner.get_hash())

    def __repr__(self):
        """
        Prints the Operation to stdout.
        """
        if isinstance(self.target, Operation):
            target = self.target.owner
        else:
            target = self.target
        return "owner: {}, action: {}, target: {}, payload: {}".format(self.owner, self.action, target, self.payload)