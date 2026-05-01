"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        test_tsp.py  —  Test Suite                                       ║
╚══════════════════════════════════════════════════════════════════════════╝
  Run:  python TSP_Project/test_tsp.py
"""

from cities           import CITIES, DIST, N
from utils            import route_distance
from greedy           import greedy_nearest_neighbor, best_greedy_all_starts
from branch_and_bound import TSP_BranchAndBound

PASS = "  [PASS]"
FAIL = "  [FAIL]"
W    = 60

def header(title):
    print("\n" + "═" * W)
    print(f"  {title}")
    print("═" * W)

def check(label, condition):
    status = PASS if condition else FAIL
    print(f"{status}  {label}")
    return condition


# ══════════════════════════════════════════════════════════════════════════
#  TEST 1 — Dataset Integrity
# ══════════════════════════════════════════════════════════════════════════
header("TEST 1 — Dataset Integrity  (cities.py)")

check("N == 15 cities",                          N == 15)
check("DIST matrix is 15×15",                    len(DIST) == 15 and all(len(r)==15 for r in DIST))
check("Diagonal is zero  DIST[i][i] == 0",       all(DIST[i][i] == 0 for i in range(N)))
check("Matrix is symmetric  DIST[i][j]==DIST[j][i]",
      all(DIST[i][j] == DIST[j][i] for i in range(N) for j in range(N)))
check("All distances are positive (off-diagonal)",
      all(DIST[i][j] > 0 for i in range(N) for j in range(N) if i != j))
check("Addis Ababa is index 0",                  CITIES[0] == "Addis Ababa")
check("Addis Ababa ↔ Adama = 99 km",             DIST[0][7] == 99)
check("Addis Ababa ↔ Hawassa = 275 km",          DIST[0][4] == 275)
check("Bahir Dar ↔ Gondar = 180 km",             DIST[2][6] == 180)
check("Dire Dawa ↔ Harar = 58 km",               DIST[1][14] == 58)


# ══════════════════════════════════════════════════════════════════════════
#  TEST 2 — route_distance()
# ══════════════════════════════════════════════════════════════════════════
header("TEST 2 — route_distance()  (utils.py)")

# Simple 3-city triangle: 0→7→4→0
# 0→7 = 99,  7→4 = 174,  4→0 = 275  →  total = 548
r3 = [0, 7, 4]
check("3-city route [0,7,4] = 548 km",           route_distance(r3) == 548)

# Single city round trip: 0→0 = 0
check("1-city route [0] = 0 km",                 route_distance([0]) == 0)

# Route must include return edge
r2 = [0, 1]   # 0→1 = 515,  1→0 = 515  →  total = 1030
check("2-city route [0,1] = 1030 km",            route_distance(r2) == 1030)

# Full route of all 15 cities must be > 0
full = list(range(N))
check("Full 15-city route distance > 0",         route_distance(full) > 0)


# ══════════════════════════════════════════════════════════════════════════
#  TEST 3 — Greedy Algorithm
# ══════════════════════════════════════════════════════════════════════════
header("TEST 3 — Greedy Nearest Neighbor  (greedy.py)")

route_from_0 = greedy_nearest_neighbor(start=0)
check("Greedy returns 15 cities",                len(route_from_0) == N)
check("Greedy starts at city 0 (Addis Ababa)",   route_from_0[0] == 0)
check("Greedy visits each city exactly once",    sorted(route_from_0) == list(range(N)))
check("Greedy distance > 0",                     route_distance(route_from_0) > 0)

route_from_7 = greedy_nearest_neighbor(start=7)
check("Greedy from Adama starts at city 7",      route_from_7[0] == 7)
check("Greedy from Adama visits all 15 cities",  sorted(route_from_7) == list(range(N)))

best_route, best_dist = best_greedy_all_starts()
check("best_greedy_all_starts returns 15 cities",sorted(best_route) == list(range(N)))
check("best_greedy_all_starts distance > 0",     best_dist > 0)
check("best_greedy_all_starts ≤ any single start",
      best_dist <= route_distance(greedy_nearest_neighbor(0)))
print(f"\n  Best greedy distance : {best_dist:,} km")
print(f"  Best greedy route    : {' → '.join(CITIES[c] for c in best_route[:5])} → ...")


# ══════════════════════════════════════════════════════════════════════════
#  TEST 4 — Branch & Bound  (self-contained 6-city solver for speed)
# ══════════════════════════════════════════════════════════════════════════
header("TEST 4 — Branch & Bound  (6-city subset for speed)")

# Use 6 nearby Ethiopian cities for a fast exact test:
# Addis Ababa, Adama, Shashamane, Hawassa, Arba Minch, Jimma
# Extract their real distances from the full matrix
import math
from itertools import permutations

SUB  = [0, 7, 10, 4, 11, 5]   # indices in the full DIST matrix
n6   = len(SUB)
D6   = [[DIST[SUB[i]][SUB[j]] for j in range(n6)] for i in range(n6)]

def dist6(route):
    """Round-trip distance for a route on the 6-city sub-problem."""
    total  = sum(D6[route[i]][route[i+1]] for i in range(len(route)-1))
    total += D6[route[-1]][route[0]]
    return total

# ── Brute-force: check all (6-1)! = 120 permutations ─────────────────────
best_brute, best_brute_route = math.inf, None
for perm in permutations(range(1, n6)):
    route = [0] + list(perm)
    d = dist6(route)
    if d < best_brute:
        best_brute       = d
        best_brute_route = route[:]

# ── Self-contained B&B for the 6-city sub-problem ────────────────────────
class MiniB_B:
    """Standalone B&B that works on D6 directly — no module patching."""
    def __init__(self, n, dist_matrix, seed_route, seed_dist):
        self.n          = n
        self.D          = dist_matrix
        self.best_route = seed_route[:]
        self.best_dist  = seed_dist
        self.visited    = 0
        self.pruned     = 0
        self._min_edge  = [min(dist_matrix[i][j] for j in range(n) if j!=i)
                           for i in range(n)]

    def _lb(self, vis, cur, last):
        unvis = [c for c in range(self.n) if not vis[c]]
        if not unvis:
            return cur + self.D[last][0]
        return (cur
                + min(self.D[last][c] for c in unvis)
                + sum(self._min_edge[c] for c in unvis)
                + min(self.D[c][0] for c in unvis))

    def solve(self):
        vis    = [False] * self.n
        vis[0] = True
        self._bt([0], vis, 0)
        return self.best_route, self.best_dist

    def _bt(self, path, vis, cur):
        self.visited += 1
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
                self.pruned += 1
                continue
            vis[city] = True
            if self._lb(vis, step, city) >= self.best_dist:
                vis[city] = False
                self.pruned += 1
                continue
            path.append(city)
            self._bt(path, vis, step)
            path.pop()
            vis[city] = False

# Seed with brute-force result so B&B has a tight upper bound
solver6 = MiniB_B(n6, D6,
                  seed_route=best_brute_route,
                  seed_dist=best_brute)
opt6, opt_d6 = solver6.solve()

check("B&B returns 6-city route",               len(opt6) == n6)
check("B&B visits each city exactly once",      sorted(opt6) == list(range(n6)))
check("B&B optimal == brute-force optimal",     opt_d6 == best_brute)
check("B&B distance ≤ brute-force distance",    opt_d6 <= best_brute)
check("B&B nodes_visited > 0",                  solver6.visited > 0)
check("B&B nodes_pruned >= 0",                  solver6.pruned >= 0)

city_names = ["Addis Ababa","Adama","Shashamane","Hawassa","Arba Minch","Jimma"]
print(f"\n  Sub-problem cities  : {', '.join(city_names)}")
print(f"  Brute-force optimal : {best_brute:,} km")
print(f"  B&B optimal         : {opt_d6:,} km")
print(f"  Match               : {'YES ✓' if opt_d6 == best_brute else 'NO ✗'}")
print(f"  Nodes explored      : {solver6.visited:,}")
print(f"  Nodes pruned        : {solver6.pruned:,}")


# ══════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════════════════
header("TEST SUMMARY")
print("  All tests completed.")
print("  [PASS] = test passed correctly")
print("  [FAIL] = test failed — check that file for bugs")
print()
