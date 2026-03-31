"""
Yo-Yo Leader Election Algorithm
================================
Implements the Yo-Yo protocol for leader election in arbitrary connected graphs.
"""

import random
import math
from collections import defaultdict


class YoYoAlgorithm:
    """
    Simulates the Yo-Yo leader election algorithm on an arbitrary connected graph.

    Attributes:
        nodes: list of node IDs (distinct positive integers)
        edges: list of (u, v) undirected edges
        message_count: total messages sent during the algorithm
    """

    def __init__(self, nodes, edges):
        """
        Args:
            nodes: list of distinct node IDs
            edges: list of (u, v) tuples representing undirected edges
        """
        self.nodes = list(nodes)
        self.edges = list(edges)
        self.message_count = 0

        # Adjacency list for the undirected graph
        self.adj = defaultdict(set)
        for u, v in self.edges:
            self.adj[u].add(v)
            self.adj[v].add(u)

        # DAG representation: in-neighbors and out-neighbors for each node
        self.in_neighbors = defaultdict(set)
        self.out_neighbors = defaultdict(set)

        # Track which nodes are still active (not pruned)
        self.active = set(nodes)

    def run(self):
        """
        Execute the Yo-Yo algorithm and return the elected leader.

        Returns:
            (leader_id, message_count) tuple
        """
        self.message_count = 0
        self._initialize_dag()

        while True:
            sources = self._get_sources()

            # If only one source remains, it's the leader
            if len(sources) == 1:
                return sources[0], self.message_count

            # If no sources (shouldn't happen in a correct run), break
            if len(sources) == 0:
                break

            # Execute one Yo-Yo iteration
            self._yo_down_yo_up()

        # Fallback: return the minimum active node
        return min(self.active), self.message_count

    def _initialize_dag(self):
        """
        Phase 1: Orient edges to form a DAG.
        Each node exchanges its ID with all neighbors (1 message per direction per edge).
        Edge is directed from smaller ID to larger ID.
        Cost: O(m) messages (2 messages per edge, but we count each exchange as 2).
        """
        self.in_neighbors = defaultdict(set)
        self.out_neighbors = defaultdict(set)

        for u, v in self.edges:
            # Each node sends its ID to the neighbor: 2 messages per edge
            self.message_count += 2

            if u < v:
                # Edge directed from u → v (smaller to larger)
                self.out_neighbors[u].add(v)
                self.in_neighbors[v].add(u)
            else:
                # Edge directed from v → u
                self.out_neighbors[v].add(u)
                self.in_neighbors[u].add(v)

    def _get_sources(self):
        """Return all active nodes with no in-neighbors (sources in the DAG)."""
        return [n for n in self.active
                if len(self.in_neighbors[n] & self.active) == 0
                and len(self.out_neighbors[n] & self.active) > 0]

    def _get_sinks(self):
        """Return all active nodes with no out-neighbors (sinks in the DAG)."""
        return [n for n in self.active
                if len(self.out_neighbors[n] & self.active) == 0
                and len(self.in_neighbors[n] & self.active) > 0]

    def _get_role(self, node):
        """Determine if a node is a source, sink, or internal."""
        has_in = len(self.in_neighbors[node] & self.active) > 0
        has_out = len(self.out_neighbors[node] & self.active) > 0
        if not has_in and has_out:
            return "source"
        elif has_in and not has_out:
            return "sink"
        elif has_in and has_out:
            return "internal"
        else:
            return "isolated"

    def _yo_down_yo_up(self):
        """
        Execute one full Yo-Yo iteration:
          1. YO- (send down): propagate minimum values from sources to sinks
          2. -YO (send up): send Yes/No responses back from sinks to sources
          3. Flip edges with "No" and apply pruning rules
        """
        # =====================================================================
        # YO- PHASE (send down)
        # =====================================================================
        # For each node, track the minimum value received and who sent it
        # min_value[node] = the minimum value this node will forward
        # received_from[node] = dict {in_neighbor: value_sent}

        min_value = {}
        received_from = defaultdict(dict)  # node -> {sender: value}

        # BFS-like topological processing: process nodes level by level
        # Sources start by "sending" their own ID
        sources = self._get_sources()
        for s in sources:
            min_value[s] = s  # A source's value is its own ID

        # Process in topological order using in-degree tracking
        # Count active in-neighbors for each active node
        pending_in = {}
        for n in self.active:
            pending_in[n] = len(self.in_neighbors[n] & self.active)

        # Queue starts with sources (pending_in == 0 and has out-neighbors)
        queue = list(sources)
        processed = set()

        while queue:
            node = queue.pop(0)
            if node in processed:
                continue
            processed.add(node)

            role = self._get_role(node)

            if role == "source":
                # Source sends its own value to all out-neighbors
                val = node
                min_value[node] = val
                for out_n in self.out_neighbors[node] & self.active:
                    self.message_count += 1  # one message sent
                    received_from[out_n][node] = val
                    pending_in[out_n] -= 1
                    if pending_in[out_n] == 0:
                        queue.append(out_n)

            elif role in ("internal", "sink"):
                # Node has received values from all in-neighbors
                if not received_from[node]:
                    continue

                val = min(received_from[node].values())
                min_value[node] = val

                if role == "internal":
                    # Forward the minimum to all out-neighbors
                    for out_n in self.out_neighbors[node] & self.active:
                        self.message_count += 1
                        received_from[out_n][node] = val
                        pending_in[out_n] -= 1
                        if pending_in[out_n] == 0:
                            queue.append(out_n)

        # =====================================================================
        # -YO PHASE (send up)
        # =====================================================================
        # For each node, determine Yes/No responses to send to in-neighbors
        # response_to[node] = dict {in_neighbor: "yes" or "no"}
        # response_from[node] = dict {out_neighbor: "yes" or "no"}

        response_from = defaultdict(dict)  # node -> {out_neighbor: response}

        # Process in reverse topological order: sinks first, then internals, then sources
        # Use reverse BFS from sinks
        pending_out = {}
        for n in self.active:
            pending_out[n] = len(self.out_neighbors[n] & self.active)

        sinks = self._get_sinks()
        queue = list(sinks)
        processed = set()

        while queue:
            node = queue.pop(0)
            if node in processed:
                continue
            processed.add(node)

            role = self._get_role(node)

            if role == "sink":
                # Send Yes to the in-neighbor(s) that sent the min value, No to others
                if not received_from[node]:
                    continue

                local_min = min_value[node]
                for in_n, val in received_from[node].items():
                    if val == local_min:
                        self.message_count += 1
                        response_from[in_n][node] = "yes"
                    else:
                        self.message_count += 1
                        response_from[in_n][node] = "no"

                # Update pending for in-neighbors
                for in_n in self.in_neighbors[node] & self.active:
                    pending_out[in_n] -= 1
                    if pending_out[in_n] == 0:
                        queue.append(in_n)

            elif role == "internal":
                # Check responses from out-neighbors
                responses = response_from[node]
                got_no = any(r == "no" for r in responses.values())

                if got_no:
                    # Send No to ALL in-neighbors
                    for in_n in self.in_neighbors[node] & self.active:
                        self.message_count += 1
                        response_from[in_n][node] = "no"
                else:
                    # All Yes: send Yes to min sender, No to others
                    local_min = min_value[node]
                    for in_n, val in received_from[node].items():
                        if val == local_min:
                            self.message_count += 1
                            response_from[in_n][node] = "yes"
                        else:
                            self.message_count += 1
                            response_from[in_n][node] = "no"

                # Update pending for in-neighbors
                for in_n in self.in_neighbors[node] & self.active:
                    pending_out[in_n] -= 1
                    if pending_out[in_n] == 0:
                        queue.append(in_n)

            elif role == "source":
                # Source just collects responses — handled below
                pass

        # =====================================================================
        # FLIP & PRUNE
        # =====================================================================

        # Collect all edges to flip (those that carried "No")
        edges_to_flip = []

        for node in self.active:
            role = self._get_role(node)
            if role in ("source", "internal"):
                for out_n, resp in response_from[node].items():
                    if resp == "no":
                        edges_to_flip.append((node, out_n))

        # Flip edges
        for u, v in edges_to_flip:
            # Remove u → v, add v → u
            self.out_neighbors[u].discard(v)
            self.in_neighbors[v].discard(u)
            self.out_neighbors[v].add(u)
            self.in_neighbors[u].add(v)

        # --- Pruning Rule 1: Remove sinks with exactly one in-neighbor ---
        changed = True
        while changed:
            changed = False
            to_remove = []
            for n in list(self.active):
                if self._get_role(n) == "sink":
                    active_in = self.in_neighbors[n] & self.active
                    if len(active_in) == 1:
                        to_remove.append(n)
            for n in to_remove:
                self.active.discard(n)
                changed = True

        # --- Pruning Rule 2: Remove redundant Yes edges ---
        # If a node received the same minimum value from multiple in-neighbors,
        # keep only one such edge and prune the rest.
        # (Only prune redundant YES edges, NOT redundant NO edges)
        for node in list(self.active):
            if self._get_role(node) in ("internal", "sink"):
                active_in = self.in_neighbors[node] & self.active
                if len(active_in) <= 1:
                    continue

                # Group in-neighbors by the value they sent during YO-down
                value_senders = defaultdict(list)
                for in_n in active_in:
                    if node in received_from and in_n in received_from.get(node, {}):
                        val = received_from[node][in_n]
                        value_senders[val].append(in_n)

                # For each value sent by multiple in-neighbors, keep only one
                # But only prune if these were YES edges (not NO)
                for val, senders in value_senders.items():
                    if len(senders) > 1:
                        # Check which of these senders got a "yes" response
                        yes_senders = [s for s in senders
                                       if response_from.get(s, {}).get(node) == "yes"]
                        if len(yes_senders) > 1:
                            # Keep the first, prune the rest
                            for s in yes_senders[1:]:
                                self.out_neighbors[s].discard(node)
                                self.in_neighbors[node].discard(s)
                                # If s has no more connections, deactivate
                                if (len(self.out_neighbors[s] & self.active) == 0
                                        and len(self.in_neighbors[s] & self.active) == 0):
                                    self.active.discard(s)

        # Re-check for sinks with one in-neighbor after pruning rule 2
        changed = True
        while changed:
            changed = False
            to_remove = []
            for n in list(self.active):
                if self._get_role(n) == "sink":
                    active_in = self.in_neighbors[n] & self.active
                    if len(active_in) == 1:
                        to_remove.append(n)
            for n in to_remove:
                self.active.discard(n)
                changed = True

        # Remove isolated nodes (no active neighbors at all)
        for n in list(self.active):
            if self._get_role(n) == "isolated":
                # Keep it only if it's the sole remaining node
                if len(self.active) > 1:
                    self.active.discard(n)


def generate_random_connected_graph(n, m):
    """
    Generate a random connected graph with n nodes and m edges.
    Nodes are labeled with distinct random IDs.

    Args:
        n: number of nodes
        m: number of edges (must be >= n-1 and <= n*(n-1)/2)

    Returns:
        (nodes, edges) where nodes is a list of distinct IDs
        and edges is a list of (u, v) tuples
    """
    max_edges = n * (n - 1) // 2
    m = min(m, max_edges)
    m = max(m, n - 1)  # Need at least n-1 edges for connectivity

    # Assign distinct random IDs to nodes
    node_ids = random.sample(range(1, 10 * n + 1), n)

    # Build a spanning tree first to ensure connectivity
    shuffled = list(node_ids)
    random.shuffle(shuffled)
    edges = set()

    for i in range(1, n):
        # Connect node i to a random node in [0, i-1]
        j = random.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        edge = (min(u, v), max(u, v))
        edges.add(edge)

    # Add remaining random edges
    all_possible = []
    for i in range(n):
        for j in range(i + 1, n):
            edge = (min(node_ids[i], node_ids[j]), max(node_ids[i], node_ids[j]))
            if edge not in edges:
                all_possible.append(edge)

    random.shuffle(all_possible)
    remaining = m - len(edges)
    for edge in all_possible[:remaining]:
        edges.add(edge)

    return node_ids, list(edges)
