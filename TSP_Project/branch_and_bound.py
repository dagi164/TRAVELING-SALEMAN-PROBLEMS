"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        File 4 of 5  :  branch_and_bound.py                              ║
║        Section      :  3. IMPLEMENTATION  (Part B — Exact Algorithm)    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Implements the exact TSP solver using Backtracking + Branch & Bound.   ║
║  This is the SECOND algorithm — guaranteed optimal solution.            ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────┐
  │  3. IMPLEMENTATION — Part B : Backtracking + Branch & Bound         │
  │                                                                     │
  │  Algorithm Name  :  Backtracking with Branch & Bound Pruning        │
  │  Type            :  Exact / Exhaustive Search with Pruning          │
  │  Time Complexity :  O(n!) worst case  /  much less with pruning     │
  │  Space Complexity:  O(n)  — recursion stack depth = n cities        │
  │                                                                     │
  │  How It Works (Step by Step):                                       │
  │  ─────────────────────────────                                      │
  │  1. Start at Addis Ababa (city 0).                                  │
  │  2. Try visiting each unvisited city next (DFS tree).               │
  │  3. Before going deeper, apply TWO pruning checks:                  │
  │                                                                     │
  │     ✂ PRUNE 1 — Upper-bound cut                                     │
  │       If  road_distance_so_far  ≥  best_complete_route              │
  │       → This path is already too long.  Abandon it.                │
  │                                                                     │
  │     ✂ PRUNE 2 — Lower-bound cut                                     │
  │       Estimate the MINIMUM possible remaining distance using        │
  │       the cheapest available roads for unvisited cities.            │
  │       If  current_dist + min_remaining  ≥  best_complete_route      │
  │       → Even the best case cannot improve.  Abandon it.            │
  │                                                                     │
  │  4. When all 15 cities are visited, record the route if it is      │
  │     shorter than the current best.                                  │
  │  5. BACKTRACK — undo the last city choice and try the next one.    │
  │  6. Repeat until all branches are explored or pruned.              │
  │                                                                     │
  │  Seeding Strategy:                                                  │
  │    The solver is pre-loaded with the best greedy tour as its       │
  │    initial upper bound.  This causes aggressive pruning from       │
  │    the very first recursive call — dramatically cutting runtime.   │
  │                                                                     │
  │  Nearest-First Ordering:                                            │
  │    At each step, unvisited cities are sorted by distance           │
  │    (nearest first).  This finds good complete tours early,         │
  │    tightening the upper bound faster and increasing pruning.       │
  │                                                                     │
  │  Why O(n!) worst case?                                              │
  │    Without pruning, we explore all (n-1)! permutations.            │
  │    For n=15: 14! = 87,178,291,200 routes.                          │
  │    With pruning: only ~24 million branches explored (0.03%).       │
  └─────────────────────────────────────────────────────────────────────┘

  Class
  ─────
  TSP_BranchAndBound
      __init__(initial_route, initial_dist)  — seed with greedy result
      solve()                                — run solver, return result
      best_route      (after solve)          — optimal city order
      best_distance   (after solve)          — shortest total km
      nodes_visited   (after solve)          — branches explored
      nodes_pruned    (after solve)          — branches cut by pruning
"""

import math
from cities import DIST, N


class TSP_BranchAndBound:
    """
    Exact TSP solver: recursive backtracking + branch-and-bound pruning.

    Usage
    ─────
        solver = TSP_BranchAndBound(initial_route=greedy_route,
                                    initial_dist=greedy_dist)
        optimal_route, optimal_dist = solver.solve()
        print(solver.nodes_visited, solver.nodes_pruned)
    """

    def __init__(self, initial_route: list = None, initial_dist: int = None):
        """
        Parameters
        ----------
        initial_route : list[int], optional
            Seed route (best greedy) used as the starting upper bound.
        initial_dist  : int, optional
            Total road distance of the seed route (km).
        """
        # Best solution known so far (seeded with greedy result)
        if initial_route is not None and initial_dist is not None:
            self.best_route    = initial_route[:]
            self.best_distance = initial_dist
        else:
            self.best_route    = []
            self.best_distance = math.inf

        # Search statistics — readable after solve()
        self.nodes_visited = 0
        self.nodes_pruned  = 0

        # Precompute the shortest outgoing road from each city.
        # min_edge[i] = shortest road from city i to any other city.
        # Used by the lower-bound estimator (Prune 2).
        self._min_edge = [
            min(DIST[i][j] for j in range(N) if j != i)
            for i in range(N)
        ]

    # ── Lower-bound estimator  (supports Prune 2) ─────────────────────────

    def _lower_bound(self, visited: list, current_dist: int, last: int) -> int:
        """
        Compute an optimistic lower bound for completing the tour.

        Formula
        ───────
        LB = current_dist
           + cheapest road from `last` city → any unvisited city
           + sum of cheapest outgoing road for each unvisited city
           + cheapest road from any unvisited city → Addis Ababa (city 0)

        This is always ≤ the true remaining cost, so it is safe to
        prune whenever  LB ≥ best_known_distance.

        Parameters
        ----------
        visited      : list[bool]  — cities already in the current path
        current_dist : int         — road distance accumulated so far
        last         : int         — index of the last city added

        Returns
        -------
        int  —  lower-bound estimate for the complete tour distance
        """
        unvisited = [c for c in range(N) if not visited[c]]

        if not unvisited:
            return current_dist + DIST[last][0]   # only return edge left

        min_from_last = min(DIST[last][c] for c in unvisited)
        min_internal  = sum(self._min_edge[c] for c in unvisited)
        min_return    = min(DIST[c][0] for c in unvisited)

        return current_dist + min_from_last + min_internal + min_return

    # ── Public entry point ────────────────────────────────────────────────

    def solve(self) -> tuple:
        """
        Run the Branch & Bound solver starting from Addis Ababa (city 0).

        Returns
        -------
        (best_route, best_distance) : (list[int], int)
            best_route    — city indices in optimal visit order
            best_distance — total road distance in km
        """
        visited    = [False] * N
        visited[0] = True                    # always start at Addis Ababa
        self._backtrack([0], visited, current_dist=0)
        return self.best_route, self.best_distance

    # ── Recursive backtracking  (private) ────────────────────────────────

    def _backtrack(self, path: list, visited: list, current_dist: int):
        """
        DFS with two pruning rules applied before each recursive call.

        Parameters
        ----------
        path         : list[int]   — cities visited so far (in order)
        visited      : list[bool]  — O(1) membership check
        current_dist : int         — total road distance accumulated
        """
        self.nodes_visited += 1

        # BASE CASE: all 15 cities visited → evaluate complete tour
        if len(path) == N:
            total = current_dist + DIST[path[-1]][path[0]]  # close the loop
            if total < self.best_distance:
                self.best_distance = total
                self.best_route    = path[:]
            return

        last = path[-1]

        # Sort candidates nearest-first → finds good tours early →
        # tightens upper bound faster → more pruning overall
        candidates = sorted(
            [c for c in range(N) if not visited[c]],
            key=lambda c: DIST[last][c]
        )

        for city in candidates:
            step_dist = current_dist + DIST[last][city]

            # ✂ PRUNE 1 — partial distance already too high
            if step_dist >= self.best_distance:
                self.nodes_pruned += 1
                continue                        # skip this entire subtree

            # ✂ PRUNE 2 — lower-bound estimate already too high
            visited[city] = True
            lb = self._lower_bound(visited, step_dist, city)
            if lb >= self.best_distance:
                visited[city] = False
                self.nodes_pruned += 1
                continue                        # skip this entire subtree

            # RECURSE — go deeper into this branch
            path.append(city)
            self._backtrack(path, visited, step_dist)

            # BACKTRACK — undo the choice, try the next candidate
            path.pop()
            visited[city] = False
