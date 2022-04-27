import tkinter as tk

class NotebookEditor():
    """
    NotebookEditor defines the UI for a simple notebook editor using tkinter. It
    optionally takes a DistributedNotebook object as input to synchronize with.
    """
    def __init__(self, client=None):
        self.root = tk.Tk()
        self.root.title(client.name if client is not None else "Untitled Notebook")
        self.client = client
        self.cells = []
        if self.client is not None:
            for peer in self.client.get_peers():
                tk.Button(self.root, text="sync with {}".format(peer), command=lambda p=peer: self.sync(p)).pack(side="top")
            self.client.attach_editor(self)

    def add_cell(self, after=None):
        cell = self.create_cell_frame()

        # Figure out if where to insert or append the cell based on which cell the add
        # button was clicked
        if after in self.cells:
            index = self.cells.index(after) + 1
        else:
            index = len(self.cells)

        if index >= len(self.cells):
            self.cells.append(cell)
            if self.client is not None:
                self.client.create_cell()
        else:
            self.cells.insert(index, cell)
            if self.client is not None:
                self.client.create_cell(index)
        self.render()

    def create_cell_frame(self, after=None, initial_text=''):
        # Create the subframe to hold the cell widgets
        cell = tk.Frame(self.root)

        # Button to remove the cell
        remove = tk.Button(cell, text="X", command=lambda: self.remove_cell(cell))
        remove.pack(side="top", anchor="ne")

        # Text editor widget
        text = tk.Text(cell, wrap="char", highlightbackground="gray")
        text.insert("end", initial_text)
        text.bind("<KeyRelease>", self.edit_cell_callback)
        text.pack()

        # Button to insert a new cell
        add = tk.Button(cell, text="+", command=lambda: self.add_cell(cell))
        add.pack(side="bottom")
        return cell

    def edit_cell_callback(self, event):
        cell = event.widget.master
        if self.client is not None:
            # If a notebook client is attached, send the new text to the correct notebook cell
            self.client.update_cell(self.cells.index(cell), event.widget.get("1.0", "end-1c"))

    def remove_cell(self, cell):
        if self.client is not None:
            self.client.remove_cell(self.cells.index(cell))
        self.cells.remove(cell)
        cell.destroy()

    def sync(self, peer):
        self.client.sync(peer)
        self.render()

    def render(self):
        """
        Refresh the UI to reflect the current state of the notebook.
        """
        if self.client is not None:
            # Delete the current cells
            for cell in self.cells:
                cell.destroy()
            self.cells = []

            # Recreate all the cells with the client's current state
            cell_data = self.client.get_cell_data()
            for text in cell_data:
                cell = self.create_cell_frame(initial_text=text)
                cell.pack(side="top", fill="both", expand=True)
                self.cells.append(cell)
        else:
            for cell in self.cells:
                cell.pack_forget()
            for cell in self.cells:
                cell.pack(side="top", fill="both", expand=True)

    def start(self):
        """
        Start the UI. Note that this method blocks until the UI is closed.
        """
        self.add_cell()
        self.root.mainloop()