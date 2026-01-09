# Coordination Logic

The Coordination capsule manages the execution of programs within the HyperSync fabric. It orchestrates the flow of messages between nodes in the hypergraph using a geometry-aware routing mechanism.

## Key Components

- **Coordinator**: The central entity that manages the session and steps through the graph.
- **Session**: Represents a single execution run, tracking the log of envelopes and scratchpad data.
- **Envelope**: A container for messages moving between source and destination nodes.
- **Routing**: Uses hyperbolic distance embedding to score candidate nodes and select the next hop.

## Mechanism

1.  **Initialization**: A session is created with a unique ID.
2.  **Step**: At each step, the coordinator identifies neighbors of the current node.
3.  **Scoring**: Neighbors are scored based on their hyperbolic distance to the task tag or current node.
4.  **Selection**: The best candidate is selected as the next hop.
5.  **Execution**: The selected node's adapter handles the message, producing an output.
6.  **Termination**: The process repeats until `max_steps` is reached or a terminal node is encountered.
