"""Trouve la BONNE geometrie cellule->ecran a partir des 5 points reels.

On teste plusieurs mapWidth ; pour chacun on calcule la grille (gx,gy) de la
cellule, puis on ajuste par moindres carres l'affine  ecran = affine(gx,gy)
(l'etape pixel iso etant lineaire, elle est absorbee par l'affine). On garde le
mapWidth dont le residu est le plus faible. Si le meilleur residu reste gros,
la FORMULE DE GRILLE elle-meme est fausse.
"""

# 5 couples reels (cellule de sortie minee -> ecran du soleil releve)
SAMPLES = [
    (434, 2679, 1023),   # 7903 [23,-45] E
    (318, 2679, 748),    # 7908 [24,-45] E
    (25,  2276, 62),     # 8047 [27,-40] N
    (459, 2139, 1096),   # 7909 [24,-44] S
    (44,  912,  133),    # 7927 [27,-41] O
]


def cell_to_grid(cell, w):
    loc5 = cell // (w * 2 - 1)
    loc6 = cell - loc5 * (w * 2 - 1)
    loc7 = loc6 % w
    gy = loc5 - loc7
    gx = (cell - (w - 1) * gy) // w
    return gx, gy


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _solve3(M, v):
    d = _det3(M)
    if abs(d) < 1e-9:
        return None
    out = []
    for col in range(3):
        Mc = [r[:] for r in M]
        for r in range(3):
            Mc[r][col] = v[r]
        out.append(_det3(Mc) / d)
    return out


def fit_affine(pts, target):
    # normal equations A^T A x = A^T b, A rows = [gx,gy,1]
    ATA = [[0.0] * 3 for _ in range(3)]
    ATb = [0.0, 0.0, 0.0]
    for (gx, gy), t in zip(pts, target):
        row = [gx, gy, 1.0]
        for i in range(3):
            ATb[i] += row[i] * t
            for j in range(3):
                ATA[i][j] += row[i] * row[j]
    return _solve3(ATA, ATb)


def residual(w):
    grids = [cell_to_grid(c, w) for c, sx, sy in SAMPLES]
    xs = [sx for c, sx, sy in SAMPLES]
    ys = [sy for c, sx, sy in SAMPLES]
    cx = fit_affine(grids, xs)
    cy = fit_affine(grids, ys)
    if cx is None or cy is None:
        return None
    err = 0.0
    for (gx, gy), sx, sy in zip(grids, xs, ys):
        px = cx[0] * gx + cx[1] * gy + cx[2]
        py = cy[0] * gx + cy[1] * gy + cy[2]
        err += (px - sx) ** 2 + (py - sy) ** 2
    return err ** 0.5, cx, cy, grids


print("mapWidth | residu (px total) | grilles")
best = None
for w in range(10, 20):
    r = residual(w)
    if r is None:
        continue
    err, cx, cy, grids = r
    print(f"  w={w:2d} : {err:8.1f}   {grids}")
    if best is None or err < best[0]:
        best = (err, w, cx, cy)

print()
if best:
    err, w, cx, cy = best
    print(f"MEILLEUR : mapWidth={w}  residu={err:.1f}px")
    print("  ecranX = %.4f*gx + %.4f*gy + %.1f" % tuple(cx))
    print("  ecranY = %.4f*gx + %.4f*gy + %.1f" % tuple(cy))
    print("  verif :")
    for c, sx, sy in SAMPLES:
        gx, gy = cell_to_grid(c, w)
        px = round(cx[0] * gx + cx[1] * gy + cx[2])
        py = round(cy[0] * gx + cy[1] * gy + cy[2])
        print(f"    cell {c}: releve ({sx},{sy}) predit ({px},{py})")
