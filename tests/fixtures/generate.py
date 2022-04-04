import random
import uuid

from notebook.cell import Cell
from notebook.notebook import DistributedNotebook

CHARSET = "abcdefghijklmnopqrstuvwxyz"

def random_word():
    return "".join(random.choice(CHARSET) for i in range(random.randint(1, 10)))

def random_cell():
    cell = Cell(id=uuid.uuid4())
    sizes = []
    for i in range(50):
        op = random.choice(["append", "insert", "remove", "append_chars", "insert_chars", "remove_chars"])
        if op == "append":
            word = random_word()
            cell.append(word)
            sizes.append(len(word))
        elif op == "insert" and len(sizes) > 1:
            word = random_word()
            index = random.randint(0, len(sizes) - 1)
            cell.insert(index, word)
            sizes.insert(index, len(word))
        elif op == "remove" and len(sizes) > 1:
            index = random.randint(0, len(sizes) - 1)
            cell.remove(index)
            sizes.pop(index)
        elif op == "append_chars" and len(sizes) > 1:
            word = random_word()
            index = random.randint(0, len(sizes) - 1)
            cell.append_chars(index, word)
            sizes[index] += len(word)
        elif op == "insert_chars" and len(sizes) > 1:
            word = random_word()
            index = random.randint(0, len(sizes) - 1)
            if sizes[index] > 1:
                char_index = random.randint(0, sizes[index] - 1)
                cell.insert_chars(index, char_index, word)
                sizes[index] += len(word)
        elif op == "remove_chars" and len(sizes) > 1:
            index = random.randint(0, len(sizes) - 1)
            if sizes[index] > 1:
                char_index = random.randint(0, sizes[index] - 1)
                length = random.randint(1, sizes[index] - char_index)
                cell.remove_chars(index, char_index, length)
                sizes[index] -= length
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