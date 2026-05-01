"""
╔══════════════════════════════════════════════════════════════════════════╗
║   TSP — Q8  |  File 5 of 5 :  main.py                                  ║
║   Purpose   :  Orchestrator — runs both algorithms, prints full report  ║
╚══════════════════════════════════════════════════════════════════════════╝

  Scenario
  ────────
  A delivery truck starts from Addis Ababa, must visit 14 other
  Ethiopian cities exactly once, and return to Addis Ababa.
  What is the shortest possible road route?

  Report Steps
  ────────────
  Step 1 — Dataset      : city list + road distance matrix
  Step 2 — Greedy       : nearest-neighbor approximation
  Step 3 — Branch&Bound : exact optimal solution
  Step 4 — Comparison   : side-by-side results table
  Step 5 — Complexity   : analysis + real-world discussion

  Run
  ───
      python main.py

  Imports
  ───────
  cities.py           — CITIES, N
  utils.py            — banner, print helpers, route_distance
  greedy.py           — best_greedy_all_starts
  branch_and_bound.py — TSP_BranchAndBound
"""

import math
import time

from cities            import CITIES, N
from utils             import (banner, print_city_list, print_distance_matrix,
                                print_route_box, route_distance)
from greedy            import best_greedy_all_starts
from branch_and_bound  import TSP_BranchAndBound

W = 72   # console width (must match utils.py)


# ══════════════════════════════════════════════════════════════════════════
#  STEP REPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

def report_dataset():
    """Step 1 — Display the Ethiopian cities and distance matrix."""
    banner("STEP 1 — DATASET  :  15 Ethiopian Cities")
    print(f"""
  Problem Scenario
  ────────────────
  A delivery company based in Addis Ababa must send a truck to
  deliver goods to 14 other major Ethiopian cities and return
  to Addis Ababa.  Goal: find the SHORTEST possible road route
  that visits every city exactly once  (Hamiltonian circuit).

  Dataset Details
  ───────────────
  Cities        : {N} major Ethiopian towns/cities
  Graph type    : Undirected, weighted  (symmetric road distances)
  Representation: 2D adjacency matrix  →  DIST[i][j] = road km
  Starting city : Addis Ababa  (index 0)
    """)
    print_city_list()
    print_distance_matrix()


def report_greedy(route: list, elapsed_ms: float):
    """Step 2 — Show greedy algorithm explanation and result."""
    banner("STEP 2 — GREEDY NEAREST NEIGHBOR  (Fast Approximation)")
    print("""
  Algorithm  :  Nearest Neighbor Heuristic
  ─────────────────────────────────────────
  Idea       :  From the current city, always drive to the nearest
                unvisited city.  Simple, fast, intuitive.

  Example trace (starting from Addis Ababa):
    Addis Ababa  →  Adama       (99 km  — nearest city)
    Adama        →  Shashamane  (149 km — nearest unvisited)
    Shashamane   →  Hawassa     (75 km  — nearest unvisited)
    ... continues until all 15 cities are visited ...

  Complexity :  O(n²) time  |  O(n) space
  Guarantee  :  NO optimality guarantee — can be 20-25% longer
                than the true shortest route.
  Trick used :  Run from ALL 15 starting cities, keep the best.
                This gives a tight upper bound to seed B&B.
    """)
    print_route_box(route, "Best Greedy Route  (best of all 15 starting cities)",
                    step_num=2)
    print(f"\n  ⏱  Time taken (all 15 starts) :  {elapsed_ms:.3f} ms")


def report_bb(route: list, elapsed_s: float,
              nodes_visited: int, nodes_pruned: int):
    """Step 3 — Show B&B explanation and optimal result."""
    banner("STEP 3 — BRANCH & BOUND  (Exact Optimal Solution)")
    total_nodes = nodes_visited + nodes_pruned
    pruning_pct = (nodes_pruned / total_nodes * 100) if total_nodes else 0
    print("""
  Algorithm  :  Backtracking with Branch & Bound Pruning
  ────────────────────────────────────────────────────────
  Idea       :  Try all possible routes (DFS), but SKIP any
                route that is already longer than the best
                complete route found so far.

  Two Pruning Rules applied before every recursive call:

    ┌──────────────────────────────────────────────────────────┐
    │  ✂ PRUNE 1 — Upper-bound cut                             │
    │    If  road_distance_so_far  ≥  best_complete_route      │
    │    → This path is already too long.  Skip it.            │
    │                                                          │
    │  ✂ PRUNE 2 — Lower-bound cut                             │
    │    Estimate minimum possible remaining distance using    │
    │    cheapest available roads for unvisited cities.        │
    │    If  current + min_remaining  ≥  best_route            │
    │    → Even the best case won't improve.  Skip it.         │
    └──────────────────────────────────────────────────────────┘

  Seeding    :  Pre-loaded with best greedy route as upper bound.
  Complexity :  O(n!) worst case  |  O(n) space
  Guarantee  :  ALWAYS finds the true shortest route.
    """)
    print_route_box(route, "Branch & Bound — Optimal (Shortest) Route",
                    step_num=3)
    print(f"\n  ⏱  Solve time           :  {elapsed_s:.4f} s")
    print(f"  🔍 Branches explored   :  {nodes_visited:>12,}")
    print(f"  ✂  Branches pruned     :  {nodes_pruned:>12,}")
    print(f"  📊 Pruning efficiency  :  {pruning_pct:.1f}% of branches eliminated")


def report_comparison(greedy_dist: int, greedy_ms: float,
                      optimal_dist: int, bb_s: float,
                      nodes_visited: int, nodes_pruned: int):
    """Step 4 — Side-by-side comparison table."""
    banner("STEP 4 — COMPARISON  :  Greedy  vs  Branch & Bound")
    improvement = (greedy_dist - optimal_dist) / greedy_dist * 100
    total_nodes = nodes_visited + nodes_pruned
    pruning_pct = (nodes_pruned / total_nodes * 100) if total_nodes else 0
    speed_ratio = bb_s / (greedy_ms / 1000) if greedy_ms > 0 else 0
    col = 32
    print()
    print(f"  {'Metric':<{col}} {'Greedy NN':>14}   {'Branch & Bound':>14}")
    print(f"  {'─'*col} {'─'*14}   {'─'*14}")
    print(f"  {'Total Road Distance (km)':<{col}} {greedy_dist:>14,}   {optimal_dist:>14,}")
    print(f"  {'Execution Time':<{col}} {greedy_ms:>11.3f} ms   {bb_s:>11.4f}  s")
    print(f"  {'Branches Explored':<{col}} {'—':>14}   {nodes_visited:>14,}")
    print(f"  {'Branches Pruned':<{col}} {'—':>14}   {nodes_pruned:>14,}")
    print(f"  {'Pruning Effectiveness':<{col}} {'—':>14}   {pruning_pct:>13.1f}%")
    print(f"  {'Finds Optimal Route?':<{col}} {'No':>14}   {'Yes ✓':>14}")
    print(f"  {'─'*col} {'─'*14}   {'─'*14}")
    print(f"""
  Key Findings
  ────────────
  ► B&B found a route  {improvement:.2f}% shorter  than greedy.
    The delivery truck saves  {greedy_dist - optimal_dist:,} km  per round trip.

  ► Greedy is  {speed_ratio:,.0f}×  faster  but does NOT guarantee the
    shortest route — it only makes the locally best choice each step.

  ► Pruning eliminated  {pruning_pct:.1f}%  of all branches, making the
    exact solution feasible despite O(n!) worst-case complexity.
    """)


def report_complexity():
    """Step 5 — Complexity analysis and real-world connections."""
    banner("STEP 5 — COMPLEXITY ANALYSIS & REAL-WORLD DISCUSSION")
    fact_15 = math.factorial(15)
    print(f"""
  ┌──────────────────────────────────────────────────────────────────┐
  │  ALGORITHM COMPLEXITY SUMMARY                                    │
  ├────────────────────────────┬─────────────────┬───────────────────┤
  │  Algorithm                 │  Time           │  Space            │
  ├────────────────────────────┼─────────────────┼───────────────────┤
  │  Greedy Nearest Neighbor   │  O(n²)          │  O(n)             │
  │  Backtracking (no pruning) │  O(n!)          │  O(n)             │
  │  Branch & Bound (pruned)   │  O(n!) worst    │  O(n)             │
  │                            │  << n! actual   │                   │
  └────────────────────────────┴─────────────────┴───────────────────┘

  For n = 15 Ethiopian cities:
    Worst-case routes to check  :  15! = {fact_15:,}
    B&B branches actually tried :  ~24 million   (0.002% of worst case)
    B&B branches pruned         :  ~88 million
    Greedy comparisons          :  15² = 225  (nearly instant)

  ┌──────────────────────────────────────────────────────────────────┐
  │  SCALABILITY  —  How does it grow with more cities?              │
  ├──────────────────────────┬───────────────────────────────────────┤
  │  n ≤ 12 cities           │  B&B solves in under 1 second         │
  │  n = 15 cities           │  B&B takes a few minutes              │
  │  n > 20 cities           │  Exact methods become too slow        │
  │  n > 100 cities          │  Must use heuristics/metaheuristics   │
  └──────────────────────────┴───────────────────────────────────────┘

  For large n, real systems use:
    • Christofides Algorithm   — guarantees ≤ 1.5× optimal route
    • Lin-Kernighan Heuristic  — used by Google Maps, logistics firms
    • Simulated Annealing      — probabilistic improvement search
    • Genetic Algorithms       — evolutionary route optimisation
    • Held-Karp (DP)           — O(n² · 2ⁿ), exact for n ≤ 20

  ┌──────────────────────────────────────────────────────────────────┐
  │  REAL-WORLD CONNECTIONS  (Ethiopian & Global)                    │
  ├──────────────────────────────────────────────────────────────────┤
  │  🇪🇹 Ethiopian Postal Service  — optimising delivery routes       │
  │  🇪🇹 Ethiopian Airlines cargo  — ground logistics planning        │
  │  🇪🇹 Aid distribution          — reaching remote towns efficiently │
  │  🌍 Last-mile delivery         — FedEx, DHL, Amazon routing       │
  │  🌍 PCB manufacturing          — minimise drill-head travel       │
  │  🌍 DNA sequencing             — fragment assembly ordering       │
  │  🌍 Telescope scheduling       — minimise slew time between stars │
  └──────────────────────────────────────────────────────────────────┘
    """)


# ══════════════════════════════════════════════════════════════════════════
#  MAIN — orchestrates all 5 steps
# ══════════════════════════════════════════════════════════════════════════

def main():

    # Title card
    print("\n" + "█" * W)
    for line in ["",
                 "TRAVELING SALESMAN PROBLEM  (TSP)  —  Q8",
                 "Ethiopian Cities Edition",
                 "Backtracking + Branch & Bound  vs  Greedy Nearest Neighbor",
                 "Scenario: Shortest delivery route across 15 Ethiopian cities",
                 ""]:
        print(f"█{line:^{W-2}}█")
    print("█" * W)

    # ── Step 1: Dataset ───────────────────────────────────────────────────
    report_dataset()

    # ── Step 2: Greedy (all 15 starting cities) ───────────────────────────
    banner("STEP 2 — RUNNING GREEDY NEAREST NEIGHBOR ...")
    print("\n  Running greedy from all 15 Ethiopian cities as start points ...")
    t0 = time.time()
    greedy_route, greedy_dist = best_greedy_all_starts()
    greedy_ms = (time.time() - t0) * 1000
    report_greedy(greedy_route, greedy_ms)

    # ── Step 3: Branch & Bound (seeded with best greedy) ──────────────────
    banner("STEP 3 — RUNNING BRANCH & BOUND (EXACT SOLVER) ...")
    print(f"\n  Seeding solver with best greedy route as upper bound ...")
    print(f"  Initial upper bound : {greedy_dist:,} km")
    print(f"\n  Searching for the optimal route ...")
    print(f"  (Branch & Bound with pruning — may take a few minutes)\n")

    solver = TSP_BranchAndBound(initial_route=greedy_route,
                                initial_dist=greedy_dist)
    t0 = time.time()
    optimal_route, optimal_dist = solver.solve()
    bb_s = time.time() - t0

    report_bb(optimal_route, bb_s, solver.nodes_visited, solver.nodes_pruned)

    # ── Step 4: Comparison ────────────────────────────────────────────────
    report_comparison(greedy_dist, greedy_ms,
                      optimal_dist, bb_s,
                      solver.nodes_visited, solver.nodes_pruned)

    # ── Step 5: Complexity ────────────────────────────────────────────────
    report_complexity()

    # Footer
    print("█" * W)
    print(f"█{'END OF REPORT':^{W-2}}█")
    print("█" * W + "\n")


if __name__ == "__main__":
    import sys
    
    # Check if user wants direct run (no menu)
    if len(sys.argv) > 1 and sys.argv[1] == "--direct":
        main()
    else:
        # Show menu first
        W = 72
        print("\n" + "█" * W)
        print(f"█{'TSP — Ethiopian Cities  |  Q8 Project':^{W-2}}█")
        print("█" * W)
        print("""
  Choose what to run:

  [1]  Full Report       — Complete 5-step analysis (15 cities, ~5 min)
  [2]  Quick Demo        — 5 cities, instant result, see all routes
  [3]  Custom Cities     — Pick your own cities (4-10), run both algorithms
  [4]  Step-by-Step      — Watch Greedy make decisions step by step
  [5]  Run Tests         — Verify all components (22 automated tests)
  [0]  Exit
        """)
        
        while True:
            try:
                choice = input("  Enter choice (0-5): ").strip()
                if choice in ["0","1","2","3","4","5"]:
                    break
                print("  ⚠  Please enter a number between 0 and 5.")
            except (KeyboardInterrupt, EOFError):
                print("\n\n  Goodbye!\n")
                sys.exit(0)
        
        if choice == "0":
            print("\n  Goodbye!\n")
        elif choice == "1":
            print("\n  Starting full 15-city report...\n")
            main()
        elif choice in ["2","3","4"]:
            print("\n  Launching interactive demo...\n")
            import subprocess
            # Map choice to demo mode
            mode_map = {"2": "1", "3": "2", "4": "3"}
            # Launch demo.py - it will show its own menu or we can pass mode
            subprocess.run([sys.executable, "demo.py"])
        elif choice == "5":
            print("\n  Running test suite...\n")
            import subprocess
            subprocess.run([sys.executable, "test_tsp.py"])
