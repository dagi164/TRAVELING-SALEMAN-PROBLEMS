"""
╔══════════════════════════════════════════════════════════════════════════╗
║        TRAVELING SALESMAN PROBLEM (TSP)  —  Q8                          ║
║        File 1 of 5  :  cities.py                                        ║
║        Section      :  1. INTRODUCTION                                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  This file introduces the problem, the dataset, and the data model.     ║
║  It contains:                                                            ║
║    • Problem introduction & real-world scenario                         ║
║    • 15 Ethiopian city names                                             ║
║    • 15×15 symmetric road distance matrix (km)                          ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────┐
  │  1. INTRODUCTION                                                    │
  │                                                                     │
  │  The Traveling Salesman Problem (TSP) is one of the most famous     │
  │  problems in computer science and combinatorial optimization.        │
  │                                                                     │
  │  Problem Statement:                                                 │
  │    Given a list of cities and the road distances between them,      │
  │    find the SHORTEST possible route that:                           │
  │      • visits every city exactly once, and                          │
  │      • returns to the starting city.                                │
  │                                                                     │
  │  Real-World Scenario (Ethiopian Context):                           │
  │    A delivery truck starts from Addis Ababa and must deliver        │
  │    goods to 14 other major Ethiopian cities, then return to         │
  │    Addis Ababa.  What is the shortest possible road route?          │
  │                                                                     │
  │  Why is it hard?                                                    │
  │    For n cities, there are (n-1)!/2 possible routes.               │
  │    For n=15: over 43 billion routes to check in the worst case.     │
  │    We need smart algorithms to find the best route efficiently.     │
  │                                                                     │
  │  Two Approaches Used in This Project:                               │
  │    1. Greedy Nearest Neighbor  — fast approximation  O(n²)         │
  │    2. Backtracking + Branch & Bound — exact solution  O(n!)        │
  └─────────────────────────────────────────────────────────────────────┘

  Data Model
  ──────────
  CITIES[i]   →  name of Ethiopian city i
  DIST[i][j]  →  road distance in km between city i and city j
                 Symmetric : DIST[i][j] == DIST[j][i]
                 No loops  : DIST[i][i] == 0
  N           →  total number of cities (15)
"""

# ══════════════════════════════════════════════════════════════════════════
#  CITY NAMES  —  15 Ethiopian cities from all regions
# ══════════════════════════════════════════════════════════════════════════

CITIES = [
    "Addis Ababa",   #  0  Capital, center of Ethiopia
    "Dire Dawa",     #  1  Major eastern city
    "Bahir Dar",     #  2  Capital of Amhara, Lake Tana
    "Mekelle",       #  3  Capital of Tigray
    "Hawassa",       #  4  Capital of Sidama, Lake Hawassa
    "Jimma",         #  5  Major south-western city
    "Gondar",        #  6  Historic northern city
    "Adama",         #  7  Oromia, close to Addis Ababa
    "Dessie",        #  8  North-eastern Amhara
    "Jijiga",        #  9  Capital of Somali region
    "Shashamane",    # 10  Southern crossroads town
    "Arba Minch",    # 11  Southern Nations, near lakes
    "Axum",          # 12  Ancient northern city, Tigray
    "Nekemte",       # 13  Western Oromia
    "Harar",         # 14  Historic walled eastern city
]

N = len(CITIES)   # 15 — always derived from the list, never hard-coded

# ══════════════════════════════════════════════════════════════════════════
#  DISTANCE MATRIX  (km)  —  approximate Ethiopian road distances
#
#  Representation: 2D adjacency matrix (list of lists)
#  Reading example:
#    DIST[0][7]  →  Addis Ababa ↔ Adama   =   99 km
#    DIST[0][4]  →  Addis Ababa ↔ Hawassa =  275 km
#    DIST[2][6]  →  Bahir Dar   ↔ Gondar  =  180 km
#
#  Column labels:
#    ADD  DDW  BHD  MEK  HAW  JIM  GON  ADM  DES  JIJ  SHA  ARB  AXU  NEK  HAR
# ══════════════════════════════════════════════════════════════════════════

DIST = [
    #      0     1     2     3     4     5     6     7     8     9    10    11    12    13    14
    [    0,  515,  578,  783,  275,  346,  738,   99,  401,  632,  250,  505, 1005,  331,  526],  #  0 Addis Ababa
    [  515,    0, 1093, 1298,  790,  861, 1253,  416,  916,  117,  765, 1020, 1520,  846,   58],  #  1 Dire Dawa
    [  578, 1093,    0,  600,  853,  346,  180,  677,  299, 1210,  828, 1083,  780,  330, 1104],  #  2 Bahir Dar
    [  783, 1298,  600,    0, 1058,  951,  320,  882,  384, 1415, 1033, 1288,  240,  935, 1309],  #  3 Mekelle
    [  275,  790,  853, 1058,    0,  335, 1013,  174,  676,  907,   75,  230, 1280,  606,  801],  #  4 Hawassa
    [  346,  861,  346,  951,  335,    0,  526,  445,  645,  978,  310,  565, 1171,  237,  872],  #  5 Jimma
    [  738, 1253,  180,  320, 1013,  526,    0,  837,  439, 1370,  988, 1243,  520,  510, 1264],  #  6 Gondar
    [   99,  416,  677,  882,  174,  445,  837,    0,  500,  533,  149,  404, 1104,  430,  427],  #  7 Adama
    [  401,  916,  299,  384,  676,  645,  439,  500,    0, 1033,  651,  906,  624,  732,  927],  #  8 Dessie
    [  632,  117, 1210, 1415,  907,  978, 1370,  533, 1033,    0,  882, 1137, 1637,  963,  175],  #  9 Jijiga
    [  250,  765,  828, 1033,   75,  310,  988,  149,  651,  882,    0,  255, 1255,  581,  776],  # 10 Shashamane
    [  505, 1020, 1083, 1288,  230,  565, 1243,  404,  906, 1137,  255,    0, 1510,  836, 1031],  # 11 Arba Minch
    [ 1005, 1520,  780,  240, 1280, 1171,  520, 1104,  624, 1637, 1255, 1510,    0, 1155, 1531],  # 12 Axum
    [  331,  846,  330,  935,  606,  237,  510,  430,  732,  963,  581,  836, 1155,    0,  857],  # 13 Nekemte
    [  526,   58, 1104, 1309,  801,  872, 1264,  427,  927,  175,  776, 1031, 1531,  857,    0],  # 14 Harar
]
