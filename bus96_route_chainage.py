import json
from shapely.geometry import LineString, Point
from pyproj import Transformer
from geographiclib.geodesic import Geodesic

ROUTE = "bus_96_busrouter_sg.geojson"
STOPS = "bus_96_stops.geojson"
TERMINAL = "17009"          # Clementi Int: start and end of the loop
TOL = 40.0                  # max stop-to-road offset (m) for a valid candidate

# 1. Load data and project WGS84 lon/lat -> SVY21 metres
to_svy21 = Transformer.from_crs(4326, 3414, always_xy=True)
route_ll = json.load(open(ROUTE))["features"][0]["geometry"]["coordinates"]
route = LineString([to_svy21.transform(lon, lat) for lon, lat in route_ll])
stops = json.load(open(STOPS))["features"]

# 2. Cumulative chainage at each route vertex
pts = list(route.coords)
cum = [0.0]
for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
    cum.append(cum[-1] + ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

def candidates(P):
    """Perpendicular projection of P onto every segment within TOL m.
    Returns (chainage, offset, side) per pass, keeping the closest per pass."""
    out = []
    for k, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            continue
        t = max(0.0, min(1.0, ((P[0] - ax) * dx + (P[1] - ay) * dy) / L2))
        fx, fy = ax + t * dx, ay + t * dy
        off = ((P[0] - fx) ** 2 + (P[1] - fy) ** 2) ** 0.5
        if off <= TOL:
            cross = dx * (P[1] - ay) - dy * (P[0] - ax)
            out.append((cum[k] + t * L2 ** 0.5, off, "L" if cross > 0 else "R"))
    passes = []                                   # group hits >200 m apart as separate passes
    for c in sorted(out):
        if passes and c[0] - passes[-1][-1][0] < 200:
            passes[-1].append(c)
        else:
            passes.append([c])
    return [min(p, key=lambda c: c[1]) for p in passes]

# 3. Chainage per stop: left-hand-traffic rule picks the pass
rows = []
for f in stops:
    code, label = f["properties"]["bus_stop_code"], f["properties"]["label"]
    if code == TERMINAL:
        rows.append((0.0, code, label, None))
        continue
    P = to_svy21.transform(*f["geometry"]["coordinates"])
    left = [c for c in candidates(P) if c[2] == "L"]
    best = min(left, key=lambda c: c[1])
    rows.append((best[0], code, label, best[1]))

# 4. Order by chainage, close the loop, difference consecutive chainages
rows.sort()
rows.append((route.length, TERMINAL, "Clementi Int", None))
for i, (a, b) in enumerate(zip(rows, rows[1:]), 1):
    print(f"{i:2d} {a[2]} -> {b[2]}: {b[0]-a[0]:8.1f} m  (cum {b[0]:8.1f})")
print(f"Loop (SVY21): {route.length:.2f} m")

# 5. Cross-check: geodesic length of the same route line
geo = sum(Geodesic.WGS84.Inverse(a[1], a[0], b[1], b[0])["s12"]
          for a, b in zip(route_ll, route_ll[1:]))
print(f"Loop (WGS84 geodesic): {geo:.2f} m")
