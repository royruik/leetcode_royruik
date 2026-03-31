import random
import math
from collections import defaultdict


class YoYoAlgorithm:
    """Simulates the Yo-Yo leader election on an arbitrary connected graph."""

    def __init__(self, nodes, edges):
        self.nodes = list(nodes)
        self.edges = list(edges)
        self.message_count = 0

        # build adjacency list
        self.adj = defaultdict(set)
        for u, v in self.edges:
            self.adj[u].add(v)
            self.adj[v].add(u)

        # DAG edges (will be populated during init phase)
        self.in_nbrs = defaultdict(set)
        self.out_nbrs = defaultdict(set)

        # nodes that haven't been pruned yet
        self.active = set(nodes)

    def run(self):
        """Run the full algorithm. Returns (leader_id, total_messages)."""
        self.message_count = 0
        self._init_dag()

        while True:
            sources = self._sources()
            if len(sources) == 1:
                return sources[0], self.message_count
            if not sources:
                break
            self._yo_iteration()

        # shouldn't really get here, but just in case
        return min(self.active), self.message_count

    # ---- Phase 1: build the initial DAG ----

    def _init_dag(self):
        """Orient each edge small->large to create a DAG. 2 msgs per edge."""
        self.in_nbrs = defaultdict(set)
        self.out_nbrs = defaultdict(set)

        for u, v in self.edges:
            self.message_count += 2  # both endpoints exchange IDs
            if u < v:
                self.out_nbrs[u].add(v)
                self.in_nbrs[v].add(u)
            else:
                self.out_nbrs[v].add(u)
                self.in_nbrs[u].add(v)

    # ---- Helper: classify nodes ----

    def _sources(self):
        return [n for n in self.active
                if not (self.in_nbrs[n] & self.active)
                and (self.out_nbrs[n] & self.active)]

    def _sinks(self):
        return [n for n in self.active
                if not (self.out_nbrs[n] & self.active)
                and (self.in_nbrs[n] & self.active)]

    def _role(self, node):
        has_in = bool(self.in_nbrs[node] & self.active)
        has_out = bool(self.out_nbrs[node] & self.active)
        if has_in and has_out:
            return "internal"
        if has_out:
            return "source"
        if has_in:
            return "sink"
        return "isolated"

    # ---- One full yo-yo round ----

    def _yo_iteration(self):
        # -- YO-down: push min values from sources toward sinks --
        min_val = {}
        recv_from = defaultdict(dict)  # node -> {sender: value}

        sources = self._sources()
        for s in sources:
            min_val[s] = s

        # track how many in-neighbors each node is still waiting on
        waiting = {}
        for n in self.active:
            waiting[n] = len(self.in_nbrs[n] & self.active)

        queue = list(sources)
        seen = set()

        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)

            role = self._role(cur)
            if role == "source":
                v = cur
                min_val[cur] = v
                for nb in self.out_nbrs[cur] & self.active:
                    self.message_count += 1
                    recv_from[nb][cur] = v
                    waiting[nb] -= 1
                    if waiting[nb] == 0:
                        queue.append(nb)

            elif role in ("internal", "sink"):
                if not recv_from[cur]:
                    continue
                v = min(recv_from[cur].values())
                min_val[cur] = v
                # internal nodes forward; sinks just hold the value
                if role == "internal":
                    for nb in self.out_nbrs[cur] & self.active:
                        self.message_count += 1
                        recv_from[nb][cur] = v
                        waiting[nb] -= 1
                        if waiting[nb] == 0:
                            queue.append(nb)

        # -- YO-up: sinks reply yes/no, propagates back to sources --
        resp_from = defaultdict(dict)  # node -> {out_neighbor: yes/no}

        waiting_out = {}
        for n in self.active:
            waiting_out[n] = len(self.out_nbrs[n] & self.active)

        queue = list(self._sinks())
        seen = set()

        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            role = self._role(cur)

            if role == "sink":
                if not recv_from[cur]:
                    continue
                best = min_val[cur]
                for sender, val in recv_from[cur].items():
                    self.message_count += 1
                    resp_from[sender][cur] = "yes" if val == best else "no"
                for nb in self.in_nbrs[cur] & self.active:
                    waiting_out[nb] -= 1
                    if waiting_out[nb] == 0:
                        queue.append(nb)

            elif role == "internal":
                got_no = any(r == "no" for r in resp_from[cur].values())
                if got_no:
                    # propagate no to everyone upstream
                    for nb in self.in_nbrs[cur] & self.active:
                        self.message_count += 1
                        resp_from[nb][cur] = "no"
                else:
                    # only say yes to whoever sent the min
                    best = min_val[cur]
                    for sender, val in recv_from[cur].items():
                        self.message_count += 1
                        resp_from[sender][cur] = "yes" if val == best else "no"
                for nb in self.in_nbrs[cur] & self.active:
                    waiting_out[nb] -= 1
                    if waiting_out[nb] == 0:
                        queue.append(nb)

        # -- Flip all edges that carried "no" --
        to_flip = []
        for node in self.active:
            if self._role(node) in ("source", "internal"):
                for out_n, r in resp_from[node].items():
                    if r == "no":
                        to_flip.append((node, out_n))

        for u, v in to_flip:
            self.out_nbrs[u].discard(v)
            self.in_nbrs[v].discard(u)
            self.out_nbrs[v].add(u)
            self.in_nbrs[u].add(v)

        # -- Pruning rule 1: drop sinks that only have one parent --
        self._prune_leaf_sinks()

        # -- Pruning rule 2: drop redundant YES edges --
        # (do NOT prune redundant NO edges - that breaks correctness)
        for node in list(self.active):
            if self._role(node) not in ("internal", "sink"):
                continue
            active_in = self.in_nbrs[node] & self.active
            if len(active_in) <= 1:
                continue

            # group by what value was sent
            by_val = defaultdict(list)
            for sender in active_in:
                if sender in recv_from.get(node, {}):
                    by_val[recv_from[node][sender]].append(sender)

            for val, senders in by_val.items():
                if len(senders) <= 1:
                    continue
                # only prune the ones that got "yes"
                yes_list = [s for s in senders
                            if resp_from.get(s, {}).get(node) == "yes"]
                # keep first, cut the rest
                for s in yes_list[1:]:
                    self.out_nbrs[s].discard(node)
                    self.in_nbrs[node].discard(s)
                    if not (self.out_nbrs[s] & self.active) and \
                       not (self.in_nbrs[s] & self.active):
                        self.active.discard(s)

        # might have created new leaf sinks, so prune again
        self._prune_leaf_sinks()

        # clean up any nodes left with zero connections
        for n in list(self.active):
            if self._role(n) == "isolated" and len(self.active) > 1:
                self.active.discard(n)

    def _prune_leaf_sinks(self):
        """Keep removing sinks that have exactly one in-neighbor."""
        changed = True
        while changed:
            changed = False
            for n in list(self.active):
                if self._role(n) == "sink":
                    if len(self.in_nbrs[n] & self.active) == 1:
                        self.active.discard(n)
                        changed = True


def generate_random_connected_graph(n, m):
    """
    Make a random connected graph with n nodes (distinct random IDs) and m edges.
    Builds a spanning tree first so it's always connected, then adds random edges.
    """
    max_edges = n * (n - 1) // 2
    m = max(n - 1, min(m, max_edges))

    # pick n distinct IDs
    ids = random.sample(range(1, 10 * n + 1), n)

    # random spanning tree for connectivity
    order = list(ids)
    random.shuffle(order)
    edges = set()
    for i in range(1, n):
        j = random.randint(0, i - 1)
        e = (min(order[i], order[j]), max(order[i], order[j]))
        edges.add(e)

    # fill in extra edges randomly
    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            e = (min(ids[i], ids[j]), max(ids[i], ids[j]))
            if e not in edges:
                candidates.append(e)
    random.shuffle(candidates)
    for e in candidates[:m - len(edges)]:
        edges.add(e)

    return ids, list(edges)


# quick sanity check when run directly
if __name__ == "__main__":
    print("Testing Yo-Yo algorithm...")

    # small example from the slides
    nodes = [3, 4, 5, 7, 2]
    edges = [(3, 4), (3, 5), (3, 7), (4, 5), (4, 7), (5, 7), (2, 7)]
    algo = YoYoAlgorithm(nodes, edges)
    leader, msgs = algo.run()
    print(f"Slide example: leader={leader}, msgs={msgs}, expected={min(nodes)}")
    assert leader == min(nodes)

    # random tests
    passed = 0
    total = 200
    for _ in range(total):
        n = random.randint(5, 60)
        m = random.randint(n - 1, min(n * (n - 1) // 2, n * 3))
        ns, es = generate_random_connected_graph(n, m)
        a = YoYoAlgorithm(ns, es)
        l, _ = a.run()
        if l == min(ns):
            passed += 1

    print(f"Random tests: {passed}/{total} passed")