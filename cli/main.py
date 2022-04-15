import sys
import argparse
from tkinter.ttk import Notebook

from ui.editor import NotebookEditor
from client.client import NotebookClient

def start_notebook(listen, peers, name):
    host_parts = listen.split(":")
    if len(host_parts) == 1:
        hostname = "localhost"
        port = int(host_parts[0])
    elif len(host_parts) == 2:
        hostname = host_parts[0]
        port = int(host_parts[1])
    client = NotebookClient(port, peers, name=name, hostname=hostname)
    client.host()
    editor = NotebookEditor(client=client)
    editor.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collaborative Notebook Client')
    parser.add_argument('--listen', type=str, default='alice:55101', help='hostname:port to listen on for sync requests')
    parser.add_argument('--peers', type=str, nargs="*", default='bob:55102 carol:55103', help='Remote peers to sync with')
    parser.add_argument('--name', type=str, default='alice', help='Client name')

    args = parser.parse_args()
    start_notebook(args.listen, args.peers, args.name)