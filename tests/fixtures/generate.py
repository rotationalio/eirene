import random
import uuid

from notebook.cell import Cell
from notebook.notebook import DistributedNotebook

CHARSET = "abcdefghijklmnopqrstuvwxyz"

def random_word(charset=CHARSET):
    return "".join(random.choice(charset) for i in range(random.randint(1, 10)))

def random_cell():
    cell = Cell(id=uuid.uuid4())
    chars = CHARSET
    cell.append(random.choice(chars))
    size = 1
    for i in range(100):
        op = random.choice(["append", "insert", "remove"])
        if op == "append":
            cell.append(random.choice(chars))
            size += 1
        elif op == "insert" and size > 1:
            index = random.randint(0, size-1)
            cell.insert(index, random.choice(chars))
            size += 1
        elif op == "remove" and size > 1:
            index = random.randint(0, size-1)
            cell.remove(index)
            size -= 1
    return cell

def random_notebook():
    notebook = DistributedNotebook(id=uuid.uuid4())
    size = 0
    for i in range(10):
        op = random.choice(["append", "insert", "remove"])
        if op == "append":
            notebook.append(random_cell())
            size += 1
        elif op == "insert" and size > 1:
            index = random.randint(0, size - 1)
            notebook.insert(index, random_cell())
            size += 1
        elif op == "remove" and size > 1:
            index = random.randint(0, size - 1)
            notebook.remove(index)
            size -= 1
    return notebook