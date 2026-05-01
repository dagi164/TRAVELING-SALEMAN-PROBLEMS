"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        File 3 of 5  :  greedy.py                                        ║
║        Section      :  3. IMPLEMENTATION  (Part A — Greedy Algorithm)   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Implements the Greedy Nearest Neighbor heuristic for TSP.              ║
║  This is the FIRST algorithm — fast approximation.                      ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────┐
  │  3. IMPLEMENTATION — Part A : Greedy Nearest Neighbor               │
  │                                                                     │
  │  Algorithm Name  :  Nearest Neighbor Heuristic                     │
  │  Type            :  Greedy Algorithm                                │
  │  Time Complexity :  O(n²)                                           │
  │  Space Complexity:  O(n)                                            │
  │                                                                     │
  │  How It Works (Step by Step):                                       │
  │  ─────────────────────────────                                      │
  │  1. Start at Addis Ababa (city 0).                                  │
  │  2. Look at all unvisited cities.                                   │
  │  3. Drive to the NEAREST unvisited city.                            │
  │  4. Mark that city as visited.                                      │
  │  5. Repeat steps 2-4 until all 15 cities are visited.              │
  │  6. Return to Addis Ababa to complete the circuit.                  │
  │                                                                     │
  │  Example Trace (starting from Addis Ababa):                        │
  │    Step 1: Addis Ababa → Adama       (99 km  — nearest)            │
  │    Step 2: Adama       → Shashamane  (149 km — nearest unvisited)  │
  │    Step 3: Shashamane  → Hawassa     (75 km  — nearest unvisited)  │
  │    Step 4: Hawassa     → Arba Minch  (230 km — nearest unvisited)  │
  │    ... continues until all 15 cities are visited ...               │
  │    Last  : [last city] → Addis Ababa (return home)                 │
  │                                                                     │
  │  Why O(n²)?                                                         │
  │    We take n steps.  At each step we scan all n cities to find     │
  │    the nearest one.  Total = n × n = n² comparisons.               │
  │                                                                     │
  │  Limitation:                                                        │
  │    Greedy makes the LOCALLY best choice at each step, but this     │
  │    does NOT guarantee the GLOBALLY shortest route.  The result     │
  │    can be 20-25% longer than the true optimal route.               │
  │                                                                     │
  │  Improvement Used:                                                  │
  │    Run greedy from ALL 15 starting cities (O(n³) total) and        │
  │    keep the shortest result.  This best greedy tour is then        │
  │    used to SEED the Branch & Bound solver as its initial           │
  │    upper bound — maximising pruning efficiency.                    │
  └─────────────────────────────────────────────────────────────────────┘

  Functions
  ─────────
  greedy_nearest_neighbor(start)  →  one greedy tour from city `start`
  best_greedy_all_starts()        →  best tour across all 15 starts
"""

import math
from cities import DIST, N
from utils  import route_distance


# ══════════════════════════════════════════════════════════════════════════
#  IMPLEMENTATION — Greedy Nearest Neighbor
# ══════════════════════════════════════════════════════════════════════════

def greedy_nearest_neighbor(start: int = 0) -> list:
    """
    Build one TSP tour using the Nearest Neighbor greedy strategy.

    Parameters
    ----------
    start : int
        Index of the starting city  (default 0 = Addis Ababa).

    Returns
    -------
    list[int]
        Ordered city indices forming the delivery route.
        The closing edge (last city → start) is NOT stored here;
        route_distance() adds it automatically.

    Complexity
    ----------
    Time  : O(n²)  — n steps, each scanning n cities
    Space : O(n)   — visited array + route list
    """
    visited        = [False] * N
    route          = [start]
    visited[start] = True

    for _ in range(N - 1):
        current      = route[-1]
        nearest      = -1
        nearest_dist = math.inf

        # Scan every unvisited city, pick the closest one  →  O(n)
        for city in range(N):
            if not visited[city] and DIST[current][city] < nearest_dist:
                nearest      = city
                nearest_dist = DIST[current][city]

        route.append(nearest)
        visited[nearest] = True

    return route


# ══════════════════════════════════════════════════════════════════════════
#  IMPROVEMENT — Run from all starting cities, keep the best
# ══════════════════════════════════════════════════════════════════════════

def best_greedy_all_starts() -> tuple:
    """
    Run greedy_nearest_neighbor from every one of the 15 cities
    and return the shortest tour found.

    Why try all 15 starting cities?
    ────────────────────────────────
    The greedy result depends heavily on the starting city.
    Starting from Adama may give a shorter tour than starting
    from Addis Ababa.  Trying all N starts costs O(n³) total
    and gives the tightest possible greedy upper bound — which
    seeds the Branch & Bound solver for maximum pruning.

    Returns
    -------
    (best_route, best_dist) : (list[int], int)
        best_route  — city indices of the shortest greedy tour found
        best_dist   — total road distance of that tour (km)

    Complexity
    ----------
    Time  : O(n³)  — n starting cities × O(n²) per greedy run
    Space : O(n)
    """
    best_route = None
    best_dist  = math.inf

    for start in range(N):
        route = greedy_nearest_neighbor(start)
        dist  = route_distance(route)
        if dist < best_dist:
            best_dist  = dist
            best_route = route[:]

    return best_route, best_dist
