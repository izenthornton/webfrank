#!/usr/bin/env python3
"""Render the site's lunar point-mesh backgrounds.

Same recipe as the pitch deck backdrops and the Moonlight event covers: a
starfield, a sky that lifts toward the horizon, and a lidar-style dot mesh over
value-noise terrain with craters, drawn far to near so hills hide what is
behind them. A red route crosses the mesh between a rover and a pin.

    python3 tools/render_scenes.py            # writes img/brand/scene-*.webp, stars.png

Requires numpy and Pillow. Everything is procedural; there is no source art.
The seeds and waypoints are fixed, so a re-run reproduces the same landscape.
The hero's flag is an HTML element pinned to the route's end; if the hero
route changes, copy the "pin top" percentages this prints into css/site.css.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "brand")

# Brand kit (June 2026)
DEEP = (13, 17, 55)        # Deep Space   #0D1137
INDIGO = (26, 35, 80)      # Orbit Indigo #1A2350
RED = (230, 57, 70)        # Signal Red   #E63946
WHITE = (255, 255, 255)    # Lunar White
STAR = (200, 203, 232)     # Starlight    #C8CBE8

SS = 2                     # supersample factor; Pillow shapes have no anti-aliasing
DZ = DX = 0.062            # mesh spacing, world units


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def value_noise(x, z, seed):
    g = np.random.default_rng(seed).uniform(-1, 1, (256, 256))
    xi, zi = np.floor(x).astype(int), np.floor(z).astype(int)
    xf, zf = x - xi, z - zi
    u, v = xf * xf * (3 - 2 * xf), zf * zf * (3 - 2 * zf)
    a = g[xi % 256, zi % 256]
    b = g[(xi + 1) % 256, zi % 256]
    c = g[xi % 256, (zi + 1) % 256]
    e = g[(xi + 1) % 256, (zi + 1) % 256]
    return a + (b - a) * u + (c - a) * v + (a - b - c + e) * u * v


def catmull_rom(pts, n=60):
    """Smooth curve through the waypoints, n samples per leg."""
    p = np.array([pts[0]] + list(pts) + [pts[-1]], dtype=float)
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                              + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-2])
    return np.array(out)


def render(name, width, height, horizon, focal, cam_h, offset, craters, route,
           arrived, star_seed, z_far=17.0, quality=80):
    """Draw one scene and save it as img/brand/<name>.webp.

    offset shifts the noise lattice so each scene is a different stretch of
    ground. route is a list of (x, z) waypoints ending at the pin.
    arrived=False parks the rover at the start and leaves a bare pin for the
    page to label; True parks it at the pin, under a plain red flag.
    """
    W, H = width * SS, height * SS
    cx = width / 2.0

    def px(v):
        return v * SS

    def ground(x, z):
        h = 0.30 * value_noise(x * 0.22 + 40 + offset, z * 0.22 + 40, 1)
        h += 0.11 * value_noise(x * 0.7 + 10 + offset, z * 0.7 + 10, 2)
        h += 0.035 * value_noise(x * 2.3 + offset, z * 2.3, 3)
        for ccx, ccz, R, dep in craters:
            rr = np.sqrt((x - ccx) ** 2 + (z - ccz) ** 2) / R
            h = h - dep * np.clip(1 - rr ** 2, 0, None) + 0.32 * dep * np.exp(-((rr - 1.0) / 0.22) ** 2)
        return h

    def project(x, z, h):
        return cx + focal * x / z, horizon + focal * (cam_h - h) / z

    # sky: Deep Space at the top edge, lifted Orbit Indigo at the horizon
    yy = np.arange(H) / SS
    t = np.clip(yy / horizon, 0, 1) ** 2.2
    arr = np.zeros((H, W, 3), dtype=np.float32)
    for c in range(3):
        arr[:, :, c] = (DEEP[c] + (INDIGO[c] + 14 - DEEP[c]) * t)[:, None]
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)

    rng = np.random.default_rng(star_seed)
    for _ in range(int(width * horizon / 9000)):
        x, y = rng.uniform(0, width), rng.uniform(0, horizon + 20)
        r = rng.choice([0.9, 1.2, 1.6, 2.4], p=[0.5, 0.3, 0.15, 0.05])
        d.ellipse([px(x - r), px(y - r), px(x + r), px(y + r)], fill=mix(DEEP, STAR, rng.uniform(0.25, 0.85)))

    # route samples, bucketed by mesh row so the painter's pass hides them behind hills
    z_near = focal * cam_h / (height - horizon) * 0.82
    zs = np.arange(z_far, z_near, -DZ)
    path = catmull_rom(route)
    ph = ground(path[:, 0], path[:, 1])
    psx, psy = project(path[:, 0], path[:, 1], ph + 0.015)
    prow = np.clip(((z_far - path[:, 1]) / DZ).astype(int) + 1, 0, len(zs) - 1)
    waypoints = {int(np.argmin(np.abs(path[:, 0] - wx) + np.abs(path[:, 1] - wz))) for wx, wz in route[1:-1]}
    pin_top = None

    def draw_route(row):
        nonlocal pin_top
        for k in np.nonzero(prow == row)[0]:
            z = path[k, 1]
            w = float(np.clip(focal * 0.008 / z, 0.9, 2.0))
            if k + 1 < len(path):
                d.line([px(psx[k]), px(psy[k]), px(psx[k + 1]), px(psy[k + 1])], fill=RED, width=int(px(w * 2)))
            d.ellipse([px(psx[k] - w), px(psy[k] - w), px(psx[k] + w), px(psy[k] + w)], fill=RED)
            if k in waypoints:
                r = w * 1.5
                d.ellipse([px(psx[k] - r), px(psy[k] - r), px(psx[k] + r), px(psy[k] + r)], fill=WHITE)
            if k == len(path) - 1:                       # the pin at the route's end
                top = psy[k] - height * 0.115
                d.line([px(psx[k]), px(psy[k]), px(psx[k]), px(top)], fill=RED, width=int(px(2.4)))
                d.ellipse([px(psx[k] - 4), px(psy[k] - 4), px(psx[k] + 4), px(psy[k] + 4)], fill=RED)
                d.ellipse([px(psx[k] - 1.6), px(psy[k] - 1.6), px(psx[k] + 1.6), px(psy[k] + 1.6)], fill=WHITE)
                if arrived:
                    d.rectangle([px(psx[k]), px(top), px(psx[k] + height * 0.062), px(top + height * 0.034)], fill=RED)
                pin_top = (psx[k], top)
            if k == (len(path) - 1 if arrived else 0):   # the rover
                s = focal * 0.19 / z                     # body width, px
                bx, by = psx[k] - s * 0.62, psy[k] + s * 0.05
                wheel = mix(DEEP, STAR, 0.95)
                d.rounded_rectangle([px(bx - s * 0.56), px(by - s * 0.30), px(bx - s * 0.40), px(by + s * 0.06)], px(s * 0.03), fill=wheel)
                d.rounded_rectangle([px(bx + s * 0.40), px(by - s * 0.30), px(bx + s * 0.56), px(by + s * 0.06)], px(s * 0.03), fill=wheel)
                d.rounded_rectangle([px(bx - s * 0.5), px(by - s * 0.56), px(bx + s * 0.5), px(by - s * 0.08)], px(s * 0.09), fill=WHITE)
                d.rectangle([px(bx - s * 0.10), px(by - s * 0.78), px(bx + s * 0.10), px(by - s * 0.55)], fill=RED)

    # mesh, far row first; each row first fills everything below its profile
    x_half = (width / 2 + 60) * z_far / focal
    xs = np.arange(-x_half, x_half, DX)
    for i, z in enumerate(zs):
        xr = xs + ((DX / 2) if i % 2 else 0.0)
        h = ground(xr, np.full_like(xr, z))
        sx, sy = project(xr, z, h)
        d.polygon([(px(a), px(b)) for a, b in zip(sx, sy)] + [(px(sx[-1]), H + 10), (px(sx[0]), H + 10)], fill=DEEP)
        r = float(np.clip(focal * 0.0046 / z, 1.15, 4.6))
        fade = float(np.clip(1.0 - (z - z_near) / (z_far - z_near), 0, 1))
        level = 0.20 + 0.72 * fade ** 1.25
        lit = np.clip(0.80 + 1.5 * np.gradient(h, xr), 0.42, 1.25)
        vis = (sx > -10) & (sx < width + 10) & (sy < height + 10)
        for ax, ay, l in zip(sx[vis], sy[vis], lit[vis]):
            d.ellipse([px(ax - r), px(ay - r), px(ax + r), px(ay + r)], fill=mix(DEEP, STAR, min(1.0, level * l)))
        draw_route(i)

    img = img.resize((width, height), Image.LANCZOS)
    out = os.path.join(OUT_DIR, name + ".webp")
    img.save(out, "WEBP", quality=quality, method=6)
    print(f"{name}.webp  {width}x{height}  {os.path.getsize(out) // 1024} KB  "
          f"horizon {100 * horizon / height:.1f}%  "
          f"pin top {100 * pin_top[0] / width:.2f}% x, {100 * pin_top[1] / height:.2f}% y")


def stars(name, size, count, seed):
    """Transparent star tile for the fixed page background."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        x, y = rng.uniform(4, size - 4), rng.uniform(4, size - 4)
        r = rng.choice([0.9, 1.2, 1.6, 2.4], p=[0.5, 0.3, 0.15, 0.05])
        a = int(255 * rng.uniform(0.25, 0.85))
        d.ellipse([S / size * (x - r), S / size * (y - r), S / size * (x + r), S / size * (y + r)], fill=STAR + (a,))
    img = img.resize((size, size), Image.LANCZOS)
    out = os.path.join(OUT_DIR, name + ".png")
    img.save(out, optimize=True)
    print(f"{name}.png  {size}x{size}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    # Home hero: the rover sets out bottom left and the route runs to a pin on
    # the far ground. The page hangs the "1 KM / NO HUMAN IN THE LOOP" flag on it.
    render("scene-hero", 2400, 900, horizon=300, focal=1900.0, cam_h=0.9, offset=0.0,
           craters=[(3.4, 6.4, 1.25, 0.42), (-3.0, 4.6, 0.8, 0.26), (-1.9, 9.0, 1.5, 0.40),
                    (5.2, 10.4, 1.9, 0.5), (-5.6, 12.0, 2.2, 0.5), (0.6, 13.2, 1.3, 0.3)],
           route=[(-1.75, 4.3), (-0.9, 4.7), (-0.1, 5.0), (-0.5, 5.7), (0.4, 6.4), (1.3, 7.2), (2.05, 7.5)],
           arrived=False, star_seed=5)
    # Page end, behind the contact block and footer: the rover has arrived at its flag.
    render("scene-ground", 2400, 760, horizon=250, focal=1900.0, cam_h=0.9, offset=23.0,
           craters=[(-4.2, 6.0, 1.3, 0.4), (2.6, 4.4, 0.7, 0.22), (4.4, 9.6, 1.7, 0.45),
                    (-1.2, 11.4, 1.6, 0.4), (-6.5, 12.5, 2.0, 0.5)],
           route=[(-1.6, 2.3), (-1.0, 3.2), (-0.2, 3.8), (-0.6, 4.6), (0.3, 5.3), (1.0, 6.0), (1.7, 6.8)],
           arrived=True, star_seed=11)
    stars("stars", 1200, 190, 5)
