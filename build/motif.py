"""The twelve-point mark: the N=12 logarithmic Fekete configuration on S^2,
which is the icosahedron. Drawn from the real vertex coordinates at build time,
never hand-authored, so it stays honest about what it depicts."""
import math

PHI = (1 + 5 ** 0.5) / 2
TILT_X, TILT_Y = 0.55, 0.42


def vertices():
    v = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            v += [(0, s1, s2 * PHI), (s1, s2 * PHI, 0), (s1 * PHI, 0, s2)]
    n = math.sqrt(1 + PHI * PHI)
    return [tuple(c / n for c in p) for p in v]


def _rotate(p):
    x, y, z = p
    y, z = y * math.cos(TILT_X) - z * math.sin(TILT_X), y * math.sin(TILT_X) + z * math.cos(TILT_X)
    x, z = x * math.cos(TILT_Y) + z * math.sin(TILT_Y), -x * math.sin(TILT_Y) + z * math.cos(TILT_Y)
    return x, y, z


def edges(v):
    """Two vertices of a unit icosahedron are adjacent iff their distance is the
    minimum one; 1.06 sits safely between that and the next distance."""
    return [(i, j) for i in range(12) for j in range(i + 1, 12)
            if math.dist(v[i], v[j]) < 1.06]


def svg(size=30, radius=42, klass="motif"):
    v = vertices()
    e = edges(v)
    p = [_rotate(q) for q in v]
    xy = [(50 + radius * x, 50 - radius * y, z) for x, y, z in p]
    out = [f'<circle cx="50" cy="50" r="{radius}" fill="none" stroke="currentColor"'
           ' stroke-width=".4" opacity=".18"/>']
    for i, j in e:                                    # far edges fade, near ones hold
        x1, y1, z1 = xy[i]; x2, y2, z2 = xy[j]
        op = 0.13 + 0.30 * ((z1 + z2) / 2 + 1) / 2
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
                   f' stroke="currentColor" stroke-width=".5" opacity="{op:.2f}"/>')
    for x, y, z in xy:                                # the twelve points themselves
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.5 + 1.1 * (z + 1) / 2:.2f}"'
                   f' fill="currentColor" opacity="{0.45 + 0.55 * (z + 1) / 2:.2f}"/>')
    return (f'<svg class="{klass}" viewBox="0 0 100 100" width="{size}" height="{size}"'
            f' aria-hidden="true">{"".join(out)}</svg>')


def document(radius=38, ink="#2A3F63", paper="#FCFBF8"):
    """Standalone file (favicon, or an asset for the CV title page)."""
    body = svg(size=100, radius=radius, klass="").split(">", 1)[1].rsplit("<", 1)[0]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<rect width="100" height="100" fill="{paper}"/>'
            f'<g color="{ink}">{body}</g></svg>')


if __name__ == "__main__":
    v = vertices()
    print(f"{len(v)} vertices, {len(edges(v))} edges")
    print(svg())
