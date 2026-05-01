"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        demo.py  —  Interactive User Demo                                ║
║        For: Student testing + Instructor submission                     ║
╚══════════════════════════════════════════════════════════════════════════╝
  Run:  python TSP_Project/demo.py
"""

import time
import math
from itertools import permutations

from cities import CITIES, DIST, N
from utils  import route_distance, banner, format_route

W = 68


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════

def line(ch="─"):
    print("  " + ch * (W - 2))

def title(text):
    print("\n" + "█" * W)
    print(f"█{text:^{W-2}}█")
    print("█" * W)

def section(text):
    print("\n" + "═" * W)
    pad = (W - len(text) - 2) // 2
    print(" " * pad + text)
    print("═" * W)

def pause():
    input("\n  Press ENTER to continue ...")

def show_cities(indices=None):
    """Print city list. If indices given, show only those."""
    cities = indices if indices else range(N)
    print()
    for i, idx in enumerate(cities):
        print(f"    [{i:2d}]  {CITIES[idx]}")
    print()

def get_int(prompt, lo, hi):
    """Ask user for an integer in [lo, hi]."""
    while True:
        try:
            val = int(input(f"  {prompt}: "))
            if lo <= val <= hi:
                return val
            print(f"  ⚠  Please enter a number between {lo} and {hi}.")
        except ValueError:
            print("  ⚠  Invalid input. Enter a number.")

def get_choice(prompt, options):
    """Ask user to pick from a list of options."""
    while True:
        ans = input(f"  {prompt}: ").strip().upper()
        if ans in options:
            return ans
        print(f"  ⚠  Please enter one of: {', '.join(options)}")


# ══════════════════════════════════════════════════════════════════════════
#  MINI B&B  (self-contained, works on any sub-matrix)
# ══════════════════════════════════════════════════════════════════════════

class MiniSolver:
    """Branch & Bound solver that works on any distance matrix."""

    def __init__(self, dist_matrix, seed_route=None, seed_dist=None):
        self.D  = dist_matrix
        self.n  = len(dist_matrix)
        self.best_route = seed_route[:] if seed_route else list(range(self.n))
        self.best_dist  = seed_dist if seed_dist else math.inf
        self.visited_count = 0
        self.pruned_count  = 0
        self._min_edge = [
            min(dist_matrix[i][j] for j in range(self.n) if j != i)
            for i in range(self.n)
        ]

    def _lb(self, vis, cur, last):
        unvis = [c for c in range(self.n) if not vis[c]]
        if not unvis:
            return cur + self.D[last][0]
        return (cur
                + min(self.D[last][c] for c in unvis)
                + sum(self._min_edge[c] for c in unvis)
                + min(self.D[c][0] for c in unvis))

    def solve(self):
        vis = [False] * self.n
        vis[0] = True
        self._bt([0], vis, 0)
        return self.best_route, self.best_dist

    def _bt(self, path, vis, cur):
        self.visited_count += 1
        if len(path) == self.n:
            total = cur + self.D[path[-1]][path[0]]
            if total < self.best_dist:
                self.best_dist  = total
                self.best_route = path[:]
            return
        last = path[-1]
        for city in sorted([c for c in range(self.n) if not vis[c]],
                           key=lambda c: self.D[last][c]):
            step = cur + self.D[last][city]
            if step >= self.best_dist:
                self.pruned_count += 1
                continue
            vis[city] = True
            if self._lb(vis, step, city) >= self.best_dist:
                vis[city] = False
                self.pruned_count += 1
                continue
            path.append(city)
            self._bt(path, vis, step)
            path.pop()
            vis[city] = False


def greedy_on(dist_matrix, start=0):
    """Greedy nearest-neighbor on any distance matrix."""
    n = len(dist_matrix)
    visited = [False] * n
    route   = [start]
    visited[start] = True
    for _ in range(n - 1):
        cur  = route[-1]
        best = min((dist_matrix[cur][c], c)
                   for c in range(n) if not visited[c])
        route.append(best[1])
        visited[best[1]] = True
    return route

def dist_on(dist_matrix, route):
    """Round-trip distance on any distance matrix."""
    total  = sum(dist_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
    total += dist_matrix[route[-1]][route[0]]
    return total


# ══════════════════════════════════════════════════════════════════════════
#  MODE 1 — QUICK DEMO  (5 cities, instant results)
# ══════════════════════════════════════════════════════════════════════════

def mode_quick_demo():
    section("MODE 1 — QUICK DEMO  (5 Ethiopian Cities)")

    print("""
  This demo uses 5 cities so you can see EVERY possible route
  and verify the algorithm finds the shortest one instantly.

  Cities used:
    [0] Addis Ababa   [1] Adama   [2] Hawassa
    [3] Shashamane    [4] Arba Minch
    """)

    sub   = [0, 7, 4, 10, 11]   # indices in full DIST
    names = [CITIES[i] for i in sub]
    n5    = len(sub)
    D5    = [[DIST[sub[i]][sub[j]] for j in range(n5)] for i in range(n5)]

    # ── Show distance table ───────────────────────────────────────────────
    print("  Road distances between the 5 cities (km):")
    print()
    abbr = [n[:3].upper() for n in names]
    print("        " + "  ".join(f"{a:>5}" for a in abbr))
    line()
    for i in range(n5):
        row = f"  {abbr[i]:>3}  |"
        for j in range(n5):
            row += "     -" if D5[i][j] == 0 else f"  {D5[i][j]:>4}"
        print(row)
    line()

    # ── Brute force: show ALL routes ──────────────────────────────────────
    print("\n  All possible routes (fixing start = Addis Ababa):\n")
    all_routes = []
    for perm in permutations(range(1, n5)):
        route = [0] + list(perm)
        d     = dist_on(D5, route)
        all_routes.append((d, route))
    all_routes.sort()

    for rank, (d, route) in enumerate(all_routes, 1):
        path = " → ".join(names[c] for c in route) + f" → {names[0]}"
        marker = "  ◄ SHORTEST" if rank == 1 else ""
        print(f"  Route {rank:2d}: {d:>5,} km  |  {path}{marker}")

    optimal_d     = all_routes[0][0]
    optimal_route = all_routes[0][1]

    # ── Greedy ────────────────────────────────────────────────────────────
    print("\n" + "─" * W)
    print("  GREEDY NEAREST NEIGHBOR result:")
    g_route = greedy_on(D5, start=0)
    g_dist  = dist_on(D5, g_route)
    g_path  = " → ".join(names[c] for c in g_route) + f" → {names[0]}"
    print(f"  Route : {g_path}")
    print(f"  Total : {g_dist:,} km")

    # ── B&B ───────────────────────────────────────────────────────────────
    print("\n" + "─" * W)
    print("  BRANCH & BOUND result:")
    solver = MiniSolver(D5, seed_route=g_route, seed_dist=g_dist)
    bb_route, bb_dist = solver.solve()
    bb_path = " → ".join(names[c] for c in bb_route) + f" → {names[0]}"
    print(f"  Route : {bb_path}")
    print(f"  Total : {bb_dist:,} km")

    # ── Verdict ───────────────────────────────────────────────────────────
    print("\n" + "═" * W)
    print("  VERDICT")
    print("═" * W)
    print(f"  Brute-force optimal : {optimal_d:,} km")
    print(f"  Greedy result       : {g_dist:,} km  {'✓ optimal' if g_dist==optimal_d else '✗ not optimal'}")
    print(f"  Branch & Bound      : {bb_dist:,} km  {'✓ optimal' if bb_dist==optimal_d else '✗ not optimal'}")
    print(f"\n  B&B nodes explored  : {solver.visited_count}")
    print(f"  B&B nodes pruned    : {solver.pruned_count}")
    print(f"  (Brute force needed : {len(all_routes)} routes)")

    pause()


# ══════════════════════════════════════════════════════════════════════════
#  MODE 2 — CUSTOM CITY SELECTOR
# ══════════════════════════════════════════════════════════════════════════

def mode_custom():
    section("MODE 2 — CUSTOM CITY SELECTOR")

    print("\n  All 15 Ethiopian cities:\n")
    for i in range(N):
        print(f"    [{i:2d}]  {CITIES[i]}")

    print()
    k = get_int("How many cities to include? (4 to 10 recommended)", 3, 12)

    print(f"\n  Enter {k} city numbers (0–14), one at a time:")
    chosen = []
    for i in range(k):
        while True:
            idx = get_int(f"  City {i+1}", 0, N-1)
            if idx in chosen:
                print(f"  ⚠  {CITIES[idx]} already chosen. Pick another.")
            else:
                chosen.append(idx)
                print(f"      ✓  Added: {CITIES[idx]}")
                break

    # Make sure city 0 (Addis Ababa) is the start
    if chosen[0] != chosen[0]:   # always start from first chosen
        pass
    start_city = chosen[0]

    print(f"\n  Your selected cities (starting from {CITIES[start_city]}):")
    for i, idx in enumerate(chosen):
        print(f"    [{i}]  {CITIES[idx]}")

    # Build sub-matrix
    nc = len(chosen)
    Dc = [[DIST[chosen[i]][chosen[j]] for j in range(nc)] for i in range(nc)]

    def dist_c(route):
        total  = sum(Dc[route[i]][route[i+1]] for i in range(len(route)-1))
        total += Dc[route[-1]][route[0]]
        return total

    # ── Greedy ────────────────────────────────────────────────────────────
    section("GREEDY NEAREST NEIGHBOR")
    t0      = time.time()
    g_route = greedy_on(Dc, start=0)
    g_time  = (time.time() - t0) * 1000
    g_dist  = dist_c(g_route)

    print("\n  Route found by Greedy:")
    path = " → ".join(CITIES[chosen[c]] for c in g_route)
    path += f" → {CITIES[chosen[0]]}"
    print(f"\n    {path}")
    print(f"\n  Total distance : {g_dist:,} km")
    print(f"  Time taken     : {g_time:.3f} ms")

    # ── B&B ───────────────────────────────────────────────────────────────
    section("BRANCH & BOUND  (Exact Solver)")
    print(f"\n  Solving for {nc} cities — please wait ...\n")

    solver = MiniSolver(Dc, seed_route=g_route, seed_dist=g_dist)
    t0     = time.time()
    bb_route, bb_dist = solver.solve()
    bb_time = time.time() - t0

    print("  Optimal route found by Branch & Bound:")
    path = " → ".join(CITIES[chosen[c]] for c in bb_route)
    path += f" → {CITIES[chosen[0]]}"
    print(f"\n    {path}")
    print(f"\n  Total distance : {bb_dist:,} km")
    print(f"  Time taken     : {bb_time:.4f} s")
    print(f"  Nodes explored : {solver.visited_count:,}")
    print(f"  Nodes pruned   : {solver.pruned_count:,}")

    # ── Comparison ────────────────────────────────────────────────────────
    section("COMPARISON")
    improvement = (g_dist - bb_dist) / g_dist * 100 if g_dist > 0 else 0
    col = 28
    print()
    print(f"  {'Metric':<{col}} {'Greedy':>12}   {'Branch & Bound':>14}")
    print(f"  {'─'*col} {'─'*12}   {'─'*14}")
    print(f"  {'Distance (km)':<{col}} {g_dist:>12,}   {bb_dist:>14,}")
    print(f"  {'Time':<{col}} {g_time:>9.3f} ms   {bb_time:>11.4f}  s")
    print(f"  {'Optimal?':<{col}} {'No':>12}   {'Yes ✓':>14}")
    print(f"  {'─'*col} {'─'*12}   {'─'*14}")
    if improvement > 0:
        print(f"\n  ► B&B saved {g_dist - bb_dist:,} km ({improvement:.1f}% shorter than greedy)")
    else:
        print(f"\n  ► Greedy found the optimal route this time!")

    pause()


# ══════════════════════════════════════════════════════════════════════════
#  MODE 3 — STEP-BY-STEP TRACE  (educational, shows algorithm thinking)
# ══════════════════════════════════════════════════════════════════════════

def mode_trace():
    section("MODE 3 — STEP-BY-STEP TRACE  (Educational)")

    print("""
  Watch the Greedy algorithm make decisions step by step.
  Uses 6 cities so the trace is easy to follow.

  Cities:
    [0] Addis Ababa  [1] Adama  [2] Hawassa
    [3] Shashamane   [4] Arba Minch  [5] Jimma
    """)

    sub   = [0, 7, 4, 10, 11, 5]
    names = [CITIES[i] for i in sub]
    n6    = len(sub)
    D6    = [[DIST[sub[i]][sub[j]] for j in range(n6)] for i in range(n6)]

    print("  ── GREEDY TRACE ──────────────────────────────────────────")
    visited = [False] * n6
    route   = [0]
    visited[0] = True
    total_dist = 0

    print(f"\n  Start at: {names[0]}")
    print(f"  Visited : {names[0]}")

    for step in range(n6 - 1):
        cur = route[-1]
        print(f"\n  Step {step+1}: Currently at {names[cur]}")
        print(f"  Distances to unvisited cities:")

        options = []
        for c in range(n6):
            if not visited[c]:
                print(f"    → {names[c]:<15} {D6[cur][c]:>5} km")
                options.append((D6[cur][c], c))

        options.sort()
        nearest_dist, nearest = options[0]
        print(f"\n  Decision: Drive to {names[nearest]} ({nearest_dist} km) — NEAREST")

        route.append(nearest)
        visited[nearest] = True
        total_dist += nearest_dist

    # Return to start
    return_dist = D6[route[-1]][route[0]]
    total_dist += return_dist
    print(f"\n  Step {n6}: Return to {names[0]} ({return_dist} km)")
    print(f"\n  ── GREEDY RESULT ─────────────────────────────────────────")
    path = " → ".join(names[c] for c in route) + f" → {names[0]}"
    print(f"  Route : {path}")
    print(f"  Total : {total_dist:,} km")

    print(f"\n  ── B&B RESULT (for comparison) ───────────────────────────")
    solver = MiniSolver(D6, seed_route=route, seed_dist=total_dist)
    bb_route, bb_dist = solver.solve()
    bb_path = " → ".join(names[c] for c in bb_route) + f" → {names[0]}"
    print(f"  Route : {bb_path}")
    print(f"  Total : {bb_dist:,} km")
    print(f"\n  Greedy {'found' if total_dist == bb_dist else 'did NOT find'} the optimal route.")
    print(f"  B&B explored {solver.visited_count} nodes, pruned {solver.pruned_count}.")

    pause()


# ══════════════════════════════════════════════════════════════════════════
#  MODE 4 — FULL 15-CITY RUN  (instructor submission output)
# ══════════════════════════════════════════════════════════════════════════

def mode_full():
    section("MODE 4 — FULL 15-CITY RUN  (Instructor Submission)")

    print("""
  This runs the complete project on all 15 Ethiopian cities.
  ⚠  Branch & Bound will take 3–10 minutes for 15 cities.
    """)

    ans = get_choice("Run full 15-city B&B? (Y/N)", ["Y", "N"])
    if ans == "N":
        print("\n  Skipped. Run  python TSP_Project/main.py  for the full report.")
        pause()
        return

    import subprocess, sys
    print("\n  Launching main.py ...\n")
    subprocess.run([sys.executable, "TSP_Project/main.py"])
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════════════

def main():
    while True:
        title("  TSP — Ethiopian Cities  |  Interactive Demo  ")

        print("""
  Choose a mode:

  [1]  Quick Demo        — 5 cities, see ALL routes, instant result
  [2]  Custom Cities     — pick your own cities (4–10), run both algorithms
  [3]  Step-by-Step Trace— watch Greedy make decisions step by step
  [4]  Full 15-City Run  — complete project output (instructor submission)
  [0]  Exit
        """)

        choice = get_choice("Enter choice", ["0","1","2","3","4"])

        if   choice == "1": mode_quick_demo()
        elif choice == "2": mode_custom()
        elif choice == "3": mode_trace()
        elif choice == "4": mode_full()
        elif choice == "0":
            print("\n  Goodbye!\n")
            break


if __name__ == "__main__":
    main()
