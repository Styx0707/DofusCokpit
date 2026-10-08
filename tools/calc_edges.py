"""Trouve les cellules CANONIQUES au milieu de chaque bord (N/S/E/O) via la
transfo cellule->ecran validee. But : un point de sortie fiable par direction,
comme N=25/S=459, mais pour E et O -> plus besoin d'apprendre.
"""
MAP_WIDTH = 15
# transfo validee (residu ~1px)
CX = (67.9685, -68.0861, 845.5)
CY = (34.2476, 34.6212, 30.6)
# boite ecran de la zone de jeu
L, T, R, B = 926, 42, 2682, 1093
CXc, CYc = (L + R) / 2, (T + B) / 2   # centre


def grid(cell):
    w = MAP_WIDTH
    loc5 = cell // (2 * w - 1)
    loc6 = cell - loc5 * (2 * w - 1)
    loc7 = loc6 % w
    gy = loc5 - loc7
    gx = (cell - (w - 1) * gy) // w
    return gx, gy


def screen(cell):
    gx, gy = grid(cell)
    return CX[0] * gx + CX[1] * gy + CX[2], CY[0] * gx + CY[1] * gy + CY[2]


pts = [(c, *screen(c)) for c in range(560)]
minX = min(p[1] for p in pts)
maxX = max(p[1] for p in pts)
minY = min(p[2] for p in pts)
maxY = max(p[2] for p in pts)


def nearest(cands, ty):
    return min(cands, key=lambda p: abs(p[2] - ty))


# bord Ouest = X mini ; bord Est = X maxi ; on prend la case dont Y ~ centre
west_band = [p for p in pts if p[1] <= minX + 40]
east_band = [p for p in pts if p[1] >= maxX - 40]
north_band = [p for p in pts if p[2] <= minY + 40]
south_band = [p for p in pts if p[2] >= maxY - 40]

o = nearest(west_band, CYc)
e = nearest(east_band, CYc)
n = min(north_band, key=lambda p: abs(p[1] - CXc))
s = min(south_band, key=lambda p: abs(p[1] - CXc))
print("boite cellules: X[%.0f..%.0f] Y[%.0f..%.0f] centre(%.0f,%.0f)" % (minX, maxX, minY, maxY, CXc, CYc))
print("O (ouest-milieu) : cellule %d -> ecran (%.0f,%.0f)" % (o[0], o[1], o[2]))
print("E (est-milieu)   : cellule %d -> ecran (%.0f,%.0f)" % (e[0], e[1], e[2]))
print("N (nord-milieu)  : cellule %d -> ecran (%.0f,%.0f)" % (n[0], n[1], n[2]))
print("S (sud-milieu)   : cellule %d -> ecran (%.0f,%.0f)" % (s[0], s[1], s[2]))
