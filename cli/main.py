from ui.editor import NotebookEditor
from notebook.notebook import DistributedNotebook

def start_notebook():
    notebook = DistributedNotebook()
    editor = NotebookEditor(notebook=notebook)
    editor.start()

if __name__ == '__main__':
    start_notebook()