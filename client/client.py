import pickle
import socket
import threading

from notebook.notebook import DistributedNotebook

RECV_BUFFER = 1024

class NotebookClient():
    """
    NotebookClient handles syncing with remote peers to implement asynchronous
    collaboration.
    """

    def __init__(self, port, peers, name="alice", hostname="localhost"):
        self.port = int(port)
        self.peers = {}
        for peer in peers:
            peer_parts = peer.split(":")
            if len(peer_parts) == 2:
                self.peers[peer_parts[0]] = ("localhost", int(peer_parts[1]))
            elif len(peer_parts) == 3:
                self.peers[peer_parts[0]] = (peer_parts[1], int(peer_parts[2]))
            else:
                raise ValueError("Invalid peer format: {}".format(peer))
        self.name = name
        self.hostname = hostname
        self.notebook = DistributedNotebook(id=name+":"+str(port))
        # The client listens and responds to sync messages on another thread.
        # Therefore, notebook accesses are critical sections and must be protected by a
        # lock to prevent concurrent access.
        self.lock = threading.Lock()
        self.editor = None

    def attach_editor(self, editor):
        """
        Attaches a NotebookEditor to the client to enable editor updates from listen().
        """
        self.editor = editor

    def get_peers(self):
        """
        Returns the list of peer names.
        """
        return list(self.peers.keys())
    
    def host(self):
        """
        Starts a listener thread to receive sync messages from remote peers.
        """
        listen = threading.Thread(target=self.listen, args=(self.port,))
        listen.start()

    def send_bytes(self, sock, data):
        """
        Send data over a socket.
        """
        size = len(data).to_bytes(4, byteorder='big')
        sock.sendall(size)
        sock.sendall(data)

    def recv_bytes(self, sock):
        """
        Receive data from a socket.
        """
        size = sock.recv(4)
        size = int.from_bytes(size, byteorder='big')
        data = b''
        while len(data) < size:
            buffer = sock.recv(size - len(data))
            if not buffer:
                raise EOFError("Connection closed")
            data += buffer
        return data

    def listen(self, port):
        """
        Listens for sync messages from remote peers.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.hostname, port))
            s.listen()
            print("Listening on port {}".format(port))
            while True:
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = self.recv_bytes(conn)
                        if not data:
                            break
                        remote = pickle.loads(data)

                        with self.lock:
                            self.notebook.merge(remote)
                            self.send_bytes(conn, pickle.dumps(self.notebook))
                        self.editor.render()

    def sync(self, peer):
        """
        Sends a sync message to a remote peer.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.peers[peer])

            with self.lock:
                self.send_bytes(s, pickle.dumps(self.notebook))

            data = self.recv_bytes(s)
            remote = pickle.loads(data)
            
            with self.lock:
                self.notebook.merge(remote)

    def create_cell(self, index=None):
        """
        Creates a new cell at the given index. If the index is not specified, the cell
        is appended to the end of the notebook.
        """
        with self.lock:
            self.notebook.create_cell(index)

    def update_cell(self, index, text):
        """
        Updates the text in a cell with new text.
        """
        with self.lock:
            self.notebook.update_cell(index, text)

    def remove_cell(self, index):
        """
        Removes the cell at the given index.
        """
        with self.lock:
            self.notebook.remove_cell(index)

    def get_cell_data(self):
        """
        Returns all the cell data in the notebook.
        """
        with self.lock:
            return self.notebook.get_cell_data()