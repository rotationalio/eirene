import sys
import argparse
from tkinter.ttk import Notebook

from ui.editor import NotebookEditor
from client.client import NotebookClient

def start_notebook(port, peers, name):
    client = NotebookClient(port, peers, name=name)
    client.host()
    editor = NotebookEditor(client=client)
    editor.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collaborative Notebook Client')
    parser.add_argument('--port', type=int, default=55101, help='Port to listen on for sync requests')
    parser.add_argument('--peers', type=str, nargs="*", default='bob:55102 carol:55103', help='Remote peers to sync with')
    parser.add_argument('--name', type=str, default='alice', help='Client name')

    args = parser.parse_args()
    start_notebook(args.port, args.peers, args.name)