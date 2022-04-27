class ObjectTree():
    """
    An ObjectTree is an append-only data structure which stores a sequence of objects
    as a tree to optimize searching.
    """
    def __init__(self):
        self.roots = []

    def insert(self, target, object, before=True):
        """
        Inserts a new object into the tree.
        """
        if target is None:
            self.insert_root(object)
        else:
            self.insert_node(target, object, before)

    def insert_root(self, object):
        """
        Inserts a new root into the tree.
        """
        index = len(self.roots)
        for i, root in enumerate(self.roots):
            if object.operation < root.obj.operation:
                index = i
                break
        if index == len(self.roots):
            self.roots.append(ObjectRoot(object))
        else:
            self.roots.insert(index, ObjectRoot(object))

    def find_insert(self, target, object, iter):
        """
        Find the insertion point for the object.
        """
        for root, i, obj in iter:
            op = obj.operation
            if op == target:
                # We found the target.
                return root, i
            elif op.target == target and object.operation < op:
                # Same target, so order the operations
                return root, i
        return None, -1

    def insert_node(self, target, object, before):
        """
        Inserts a new object into the tree before.
        """
        if before:
            enumerate_nodes = self.enumerate()
        else:
            enumerate_nodes = self.enumerate_reverse()

        root, i = self.find_insert(target, object, enumerate_nodes)
        if before:
            if root is None:
                self.roots[-1].nodes.append(object)
            else:
                root.nodes.insert(i, object)
        else:
            if root is None:
                self.roots[0].nodes.insert(0, object)
            else:
                root.nodes.insert(i + 1, object)

    def enumerate(self):
        """
        Enumerates the objects in the tree by depth-first traversal and yields a list
        of (root, node_index, object) tuples.
        """
        for root in self.roots:
            for i, obj in enumerate(root.nodes):
                yield root, i, obj

    def enumerate_reverse(self):
        """
        Enumerates the objects in the tree by depth-first traversal and yields a list
        of (root, node_index, object) tuples.
        """
        for root in reversed(self.roots):
            for i, obj in reversed(list(enumerate(root.nodes))):
                yield root, i, obj

    def __iter__(self):
        """
        Iterates over the objects in the tree.
        """
        for root in self.roots:
            yield from root.nodes

class ObjectRoot():
    """
    A root in an ObjectTree
    """
    def __init__(self, obj):
        self.obj = obj
        self.nodes = [obj]