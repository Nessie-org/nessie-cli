# Nessie CLI Graph Plugin

A CLI plugin for the Nessie ecosystem that provides simple commands for creating, editing, and visualizing graph structures directly from the terminal.

The plugin allows you to manage **nodes**, **edges**, and their **properties** in a graph using concise CLI commands.

---

## Features

- Create nodes with arbitrary properties
- Create edges between nodes
- Modify node and edge properties
- Delete nodes and edges
- Reset the current graph
- Clear the console

---

## Concepts
### Node

A vertex in the graph identified by an **ID**.
Nodes can contain arbitrary **key-value properties**.

### Edge
A connection between two nodes.

Edges also have:

- an **ID**
- optional **properties**

## Commands
### Create Node

Create a new node with properties.
```
create node --id 1 --property name = John --property age = 30
```

### Create Edge

Create an edge between two nodes.

Arguments:
- first node id
- second node id
- edge id
- optional properties

```
create edge 1 2 --id someEdge --property key=value
```

### Edit Node

Modify node properties.

Options:

- ```--ch_prop``` – change or add a property
- ```--del_prop``` – remove a property

```
edit node --id 1 --ch_prop name = Tom --ch_prop address = "Main street" --del_prop age
```

### Edit Edge

Modify properties of an edge.

```
edit edge --id someEdge --ch_prop key = other value
```

### Delete Edge

Remove an edge from the graph.

```
delete edge --id someEdge
```

### Delete Node

Remove a node from the graph.

```
delete node --id 1
```
Note: You can't delete a node if there are incident edges

### Drop Graph

Completely remove the current graph.

```
drop graph
```

Clear

Reset the CLI state

```
clear
```









