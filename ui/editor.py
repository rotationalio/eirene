import tkinter as tk

class NotebookEditor():
    '''
    NotebookEditor defines the UI for a simple notebook editor using tkinter. It
    optionally takes a DistributedNotebook object as input to synchronize with.
    '''
    def __init__(self, notebook=None):
        self.root = tk.Tk()
        self.root.title("Collaborative Notebook Editor")
        self.notebook = notebook
        self.cells = []

    def add_cell(self, after=None):
        # Create the subframe to hold the cell widgets
        cell = tk.Frame(self.root)

        # Button to remove the cell
        remove = tk.Button(cell, text="X", command=lambda: self.remove_cell(cell))
        remove.pack(side="top", anchor="ne")

        # Text editor widget
        text = tk.Text(cell, wrap="char", highlightbackground="gray")
        text.bind("<KeyRelease>", self.edit_cell_callback)
        text.pack()

        # Button to insert a new cell
        add = tk.Button(cell, text="+", command=lambda: self.add_cell(cell))
        add.pack(side="bottom")

        # Figure out if where to insert or append the cell based on which cell the add
        # button was clicked
        if after in self.cells:
            index = self.cells.index(after) + 1
        else:
            index = len(self.cells)

        if index >= len(self.cells):
            self.cells.append(cell)
            if self.notebook is not None:
                self.notebook.create_cell()
        else:
            self.cells.insert(index, cell)
            if self.notebook is not None:
                self.notebook.create_cell(index)
        self.render()

    def edit_cell_callback(self, event):
        cell = event.widget.master
        if self.notebook is not None:
            # If a notebook is attached, send the new text to the correct notebook cell
            self.notebook.update_cell(self.cells.index(cell), event.widget.get("1.0", "end-1c"))

    def remove_cell(self, cell):
        if self.notebook is not None:
            self.notebook.remove_cell(self.cells.index(cell))
        self.cells.remove(cell)
        cell.destroy()

    def render(self):
        '''
        Refresh the UI to reflect the current state of the notebook.
        '''
        for cell in self.cells:
            cell.pack_forget()
        for cell in self.cells:
            cell.pack(side="top", fill="both", expand=True)

    def start(self):
        '''
        Start the UI. Note that this method blocks until the UI is closed.
        '''
        self.add_cell()
        self.root.mainloop()