"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        File 2 of 5  :  utils.py                                         ║
║        Section      :  2. ALGORITHM DESIGN                              ║
╠══════════════════════════════════════════════════════════════════════════╣
║  This file covers the algorithm design decisions:                       ║
║    • How the problem is modelled (graph representation)                 ║
║    • Core distance calculation used by both algorithms                  ║
║    • All display/output helpers used throughout the project             ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────┐
  │  2. ALGORITHM DESIGN                                                │
  │                                                                     │
  │  Graph Representation                                               │
  │  ─────────────────────                                              │
  │  The 15 Ethiopian cities are modelled as a COMPLETE WEIGHTED        │
  │  UNDIRECTED GRAPH:                                                  │
  │    • Nodes  = cities                                                │
  │    • Edges  = roads between every pair of cities                   │
  │    • Weight = road distance in km                                   │
  │    • Stored as a 2D adjacency matrix  DIST[i][j]                   │
  │                                                                     │
  │  Why adjacency matrix?                                              │
  │    O(1) edge lookup — critical for performance since both           │
  │    algorithms access DIST[i][j] millions of times.                 │
  │                                                                     │
  │  Algorithm Selection                                                │
  │  ───────────────────                                                │
  │  Two algorithms are designed and compared:                          │
  │                                                                     │
  │  A. Greedy Nearest Neighbor  (greedy.py)                           │
  │     Design: At each step, choose the locally optimal move          │
  │             (nearest unvisited city).                               │
  │     Pros  : O(n²) — very fast                                      │
  │     Cons  : No global optimality guarantee                         │
  │                                                                     │
  │  B. Backtracking + Branch & Bound  (branch_and_bound.py)           │
  │     Design: Exhaustive DFS with two pruning rules to cut           │
  │             branches that cannot improve the best solution.        │
  │     Pros  : Guaranteed optimal solution                            │
  │     Cons  : O(n!) worst case — slow for large n                    │
  │                                                                     │
  │  Seeding Strategy (key design decision):                           │
  │    Run greedy first → use its result as the initial upper          │
  │    bound for B&B → dramatically increases pruning from step 1.    │
  └─────────────────────────────────────────────────────────────────────┘

  Functions in this file
  ──────────────────────
  route_distance(route)          →  total round-trip road distance (km)
  banner(title)                  →  bold section header for output
  print_city_list()              →  two-column city index table
  print_distance_matrix()        →  compact adjacency matrix grid
  format_route(route)            →  wrapped multi-line route string
  print_route_box(route, label)  →  formatted route display box
"""

from cities import CITIES, DIST, N

W = 72   # console width — used by all display functions


# ══════════════════════════════════════════════════════════════════════════
#  CORE CALCULATION  —  used by both algorithms
# ══════════════════════════════════════════════════════════════════════════

def route_distance(route: list) -> int:
    """
    Compute the total round-trip road distance of a TSP route.

    Sums every consecutive edge in `route`, then adds the closing
    edge from the last city back to the first (completing the circuit).

    Parameters
    ----------
    route : list[int]
        Ordered city indices, each appearing exactly once.

    Returns
    -------
    int  —  total road distance in km (full round trip).

    Example
    -------
        route_distance([0, 7, 10, 4, 11])
        # Addis Ababa → Adama → Shashamane → Hawassa → Arba Minch
        # → back to Addis Ababa
    """
    total  = sum(DIST[route[i]][route[i + 1]] for i in range(len(route) - 1))
    total += DIST[route[-1]][route[0]]   # closing edge: last city → start
    return total


# ══════════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS  —  used by main.py for the output report
# ══════════════════════════════════════════════════════════════════════════

def banner(title: str):
    """Print a bold full-width section banner."""
    print("\n" + "═" * W)
    pad = (W - len(title) - 2) // 2
    print(" " * pad + title)
    print("═" * W)


def print_city_list():
    """Display all 15 Ethiopian cities in a two-column numbered table."""
    print()
    print(f"  {'#':<5} {'City':<20}    {'#':<5} {'City':<20}")
    print(f"  {'─'*5} {'─'*20}    {'─'*5} {'─'*20}")
    for i in range(8):
        j     = i + 8
        left  = f"  [{i:2d}]  {CITIES[i]:<20}"
        right = f"  [{j:2d}]  {CITIES[j]}" if j < N else ""
        print(left + "   " + right)
    if N % 2 == 1:
        print(f"  [{N-1:2d}]  {CITIES[N-1]}")
    print()


def print_distance_matrix():
    """
    Display the 15×15 road distance matrix as a compact grid.
    Uses 3-letter abbreviations so the table fits the console.
    """
    abbr = ["ADD","DDW","BHD","MEK","HAW","JIM","GON","ADM",
            "DES","JIJ","SHA","ARB","AXU","NEK","HAR"]

    print("\n  Road Distance Matrix (km)  —  2D Adjacency Matrix")
    print("  " + "─" * (N * 5 + 8))
    print("       " + "  ".join(f"{a:>3}" for a in abbr))
    print("  " + "─" * (N * 5 + 8))
    for i in range(N):
        row = f"  {abbr[i]:>3}  |"
        for j in range(N):
            row += "    -" if DIST[i][j] == 0 else f" {DIST[i][j]:>4}"
        print(row)
    print("  " + "─" * (N * 5 + 8))
    print()
    print("  Key  (abbreviation = city name):")
    for i in range(N):
        print(f"    {abbr[i]}  =  {CITIES[i]}")


def format_route(route: list) -> str:
    """
    Wrap a route into multiple lines, each at most W-6 characters wide.
    Returns a ready-to-print indented string.
    """
    names = [CITIES[c] for c in route] + [CITIES[route[0]]]
    lines, line = [], ""
    for i, name in enumerate(names):
        seg = name if i == 0 else f" → {name}"
        if line and len(line) + len(seg) > W - 6:
            lines.append(line)
            line = name
        else:
            line += seg
    if line:
        lines.append(line)
    return "\n".join(f"    {l}" for l in lines)


def print_route_box(route: list, label: str, step_num: int = None) -> int:
    """
    Print a route inside a labelled box showing the full path
    and total road distance.  Returns the total distance (km).
    """
    dist   = route_distance(route)
    prefix = f"  Step {step_num} — " if step_num else "  "
    print(f"\n  {'─' * (W - 2)}")
    print(f"{prefix}{label}")
    print(f"  {'─' * (W - 2)}")
    print()
    print(format_route(route))
    print()
    print(f"    Total Road Distance :  {dist:>6,} km")
    print(f"  {'─' * (W - 2)}")
    return dist
