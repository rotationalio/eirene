# eirene

`eirene` is a demo client for CRDT-driven collaboration, implemented in Python. It uses CRDT data structures to achieve eventual consistency across remote peers.

## How it works
`eirene` is built on top of a `Sequence` CRDT. When the user makes an edit to the notebook or a cell, the edit gets decomposed into a series of individual operations. These operations get added to the `Sequence`'s operation log. The operation log is organized as an unordered Grow-only set CRDT, but each operation is assigned a unique ID, using another CRDT (a Grow-only counter). This allows a total ordering to be imposed on the set of operations that is consistent acrosss replicas.

The `Sequence` object supports merging different versions with itself. Therefore, for two concurrently operating clients sync with each other, they simply have to exchange their versions of the notebook and each peer performs a merge with the remote notebook. After the sync, both peers should have the same operation log and should therefore be able to render the same notebook state.

The demo in its current state represents an offline-first style of collaboration similar to GIT. However, the underlying data structure could potentially be used to also implement a more real-time collaborative application similar to google docs.

There are also some fairly arbitrary conflict handling choices made here which could be altered for different applications. Concurrent conflicts are always resolved by lexigraphically sorting the client names, which means that the same peer will always write first if two peers have conflicting writes. Also, writes from both parties are always preserved but a delete from one peer will always take precedence over a write from the other peer.

## Installation
In its present state eirene is built to run using Python 3 and only requires the standard Python libraries, although `tkinter` must be configured correctly to run the interactive demo.

## Starting a client
From the root of the project, enter the following:

```python
python cli/main.py --name [NAME] --listen [PORT]
```

This will start a new client with the name `NAME` and start listening on the port `PORT`. It will also open up a UI window titled with `NAME`.

## Staring multiple clients
Clients can be started from other shell windows using the same command. Although by default clients will listen for connections, they will not know how to send sync requests to each other by default. This information is provided with the `--peers [NAME:PORT ...]` argument. This identifies a list of peers that the client should know how to talk to. For example, the following commands instantiate an `alice` and `bob` client who each know how to communicate with each other.

```python
python cli/main.py --name alice --listen 55101 --peers bob:55102
python cli/main.py --name bob --listen 55102 --peers alice:55101
```

Multiple peers can be specified with a space-separated list, like so:
```python
python cli/main.py --name alice --listen 55101 --peers bob:55102 charlie:55103
```

Note that notebook uniqueness is determined by the `NAME:PORT` combination. The same name can be specified by different peers as long as the port numbers are unique. In fact, the first part of each peer in the `peers` argument is purely a client-side idenitifier and only affects what name is displayed in the UI.

## Using the UI
Pressing the `sync with [NAME]` button causes the client to sync with the indicated peer. During a sync, the peers exchange notebooks and the UI for each peer gets updated with the current state of the new, merged notebook. Immediately after this point the two clients should display an identical notebook (same number of cells and same data within each cell). If they aren't, then feel free to create a bug report issue!