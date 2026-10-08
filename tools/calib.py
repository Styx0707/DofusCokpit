"""Transformation cellule -> pixel ecran, calee par 3 couples reels (sans numpy).

Affine : ecranX = a*px+b*py+c ; ecranY = d*px+e*py+f, resolue par Cramer 3x3.
"""
import json

MAP_WIDTH = 14
CW, CH = 43, 21


def cell_to_grid(cell):
    loc5 = cell // (MAP_WIDTH * 2 - 1)
    loc6 = cell - loc5 * (MAP_WIDTH * 2 - 1)
    loc7 = loc6 % MAP_WIDTH
    gy = loc5 - loc7
    gx = (cell - (MAP_WIDTH - 1) * gy) // MAP_WIDTH
    return gx, gy


def cell_to_pixel(cell):
    gx, gy = cell_to_grid(cell)
    return (gx - gy) * CW, (gx + gy) * CH


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _solve3(M, v):
    d = _det3(M)
    out = []
    for col in range(3):
        Mc = [row[:] for row in M]
        for r in range(3):
            Mc[r][col] = v[r]
        out.append(_det3(Mc) / d)
    return out


# couples reels (cellule de sortie minee -> ecran du soleil releve)
samples = [
    (434, 2679, 1023),   # map 7903 [23,-45] E
    (318, 2679, 748),    # map 7908 [24,-45] E
    (25, 2276, 62),      # map 8047 [27,-40] N
]

M, vx, vy = [], [], []
for cell, sx, sy in samples:
    px, py = cell_to_pixel(cell)
    M.append([px, py, 1])
    vx.append(sx)
    vy.append(sy)
CX = _solve3(M, vx)
CY = _solve3(M, vy)
print("ecranX = %.4f*px + %.4f*py + %.1f" % tuple(CX))
print("ecranY = %.4f*px + %.4f*py + %.1f" % tuple(CY))


def cell_to_screen(cell):
    px, py = cell_to_pixel(cell)
    return round(CX[0] * px + CX[1] * py + CX[2]), round(CY[0] * px + CY[1] * py + CY[2])


print("\n=== residus points de calage (doivent etre ~0) ===")
for cell, sx, sy in samples:
    print(f"  cell {cell}: releve ({sx},{sy}) predit {cell_to_screen(cell)}")

print("\n=== VALIDATION : ou devraient tomber ces soleils ? ===")
for name, cell in [("Sud c459", 459), ("Sud c457", 457), ("Nord c25", 25),
                   ("Nord c23", 23), ("Ouest c280", 280)]:
    print(f"  {name} -> {cell_to_screen(cell)}")

print("\n=== sorties minees -> ecran (echantillon) ===")
try:
    exits = json.load(open("/srv/data/map_exits.json"))
    for mid, dirs in list(exits.items())[:14]:
        print("  map %s : %s" % (mid, " ".join(
            "%s:c%s->%s" % (d, c, cell_to_screen(c)) for d, c in dirs.items())))
except Exception as e:
    print("map_exits.json ?", e)
