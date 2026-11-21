"""Realism layer: textured lit globe (numpy), iso with cast shadows + gradient faces, film post FX."""
import sys, math
sys.path.insert(0, '/home/claude/vid')
import numpy as np
import cairo
from engine import *

# ---------------- noise / textures ----------------
def fbm(w, h, octaves=6, seed=0, base=4):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        gx, gy = base * 2 ** o, max(2, base * 2 ** o // 2)
        g = rng.standard_normal((gy + 1, gx)).astype(np.float32)
        xs = np.linspace(0, gx, w, endpoint=False); ys = np.linspace(0, gy, h)
        x0 = np.floor(xs).astype(int); fx = (xs - x0)[None, :]; x1 = (x0 + 1) % gx
        y0 = np.clip(np.floor(ys).astype(int), 0, gy - 1); fy = (ys - y0)[:, None]; y1 = y0 + 1
        fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
        a = g[y0][:, x0]; b = g[y0][:, x1]; c = g[y1][:, x0]; d = g[y1][:, x1]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        tot += amp; amp *= 0.5
    return out / tot

TW, TH = 1024, 512
LAT = np.linspace(90, -90, TH)[:, None] * np.ones((1, TW))
_n = fbm(TW, TH, 7, seed=5, base=6); _n = (_n - _n.mean()) / _n.std() * .35
_d = fbm(TW, TH, 5, seed=11); _d = (_d - _d.mean()) / _d.std() * .35
_c = fbm(TW, TH, 6, seed=21, base=6); _c = (_c - _c.mean()) / _c.std() * .35
ALAT = np.abs(LAT)

def palette(land, ice, n, d):
    """returns HxWx3 float colors"""
    img = np.zeros((TH, TW, 3), np.float32)
    depth = np.clip(-n * 3, 0, 1)[..., None]
    ocean = (1 - depth) * np.array([0.10, 0.36, 0.62]) + depth * np.array([0.03, 0.12, 0.32])
    dry = np.clip(1 - np.abs(np.abs(LAT) - 24) / 14, 0, 1) * np.clip(d * 2 + .5, 0, 1)
    green = np.array([0.20, 0.42, 0.16]) * (1 - .3 * n[..., None]) + np.array([0.06, 0.06, 0.0]) * d[..., None]
    sand = np.array([0.72, 0.60, 0.40]) * (1 + .15 * d[..., None])
    mount = np.clip((n - .25) * 3, 0, 1)[..., None]
    landc = green * (1 - dry[..., None]) + sand * dry[..., None]
    landc = landc * (1 - mount) + np.array([0.45, 0.38, 0.30]) * mount
    img = np.where(land[..., None], landc, ocean)
    img = np.where(ice[..., None], np.array([0.92, 0.95, 0.98]) - .05 * d[..., None], img)
    return np.clip(img, 0, 1).astype(np.float32)

LAND_A = _n > np.quantile(_n, 0.68)
_n = _n - np.quantile(_n, 0.68)
ICE_A = (ALAT > 72 + 6 * _d) | ((ALAT > 62) & LAND_A & (LAT < 0))
TEX_A = palette(LAND_A, ICE_A, _n, _d)
# "stopped earth": water collects at the poles, one equatorial supercontinent
LAND_B = ALAT < (38 + 22 * _d)
ICE_B = np.zeros_like(LAND_B)
TEX_B = palette(LAND_B, ICE_B, np.where(LAND_B, np.abs(_n) + .05, -np.abs(_n) - .2), _d)
# switch moment per pixel: equator first, poles last  (0..1)
SWITCH = np.clip(ALAT / 90 + .08 * _d, 0, 1)
FREEZE_ORD = np.clip(1 - ALAT / 90 + .12 * _d, 0, 1)
CLOUD = np.clip((_c - 0.1) * 2.6, 0, 1) * .9

def globe_tex(mig):
    if mig <= 0: return TEX_A
    if mig >= 1: return TEX_B
    m = (SWITCH < mig)[..., None]
    return np.where(m, TEX_B, TEX_A)

# ---------------- globe renderer ----------------
_grid_cache = {}
def _grid(R):
    if R not in _grid_cache:
        n = 2 * R
        ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
        x = (xs + .5 - R) / R; y = (ys + .5 - R) / R
        r2 = x * x + y * y
        _grid_cache[R] = (x, y, r2)
    return _grid_cache[R]

def render_globe(R, lon0=0.0, tilt=0.35, sun=(-.6, -.35, .72), mig=0.0, clouds=0.85, cloud_lon=0.0,
                 night=0.04, term_glow=0.0, wind=0.0, freeze=0.0, bright=1.0, tint=(1, 1, 1), haze=None, hot=None):
    """returns cairo ImageSurface (ARGB32) of size 2R with a lit textured globe"""
    x, y, r2 = _grid(R)
    inside = r2 <= 1.0
    z = np.sqrt(np.clip(1 - r2, 0, 1))
    # rotate view by tilt around x axis
    ct, st = math.cos(tilt), math.sin(tilt)
    yy = y * ct - z * st; zz = y * st + z * ct
    lat = np.degrees(np.arcsin(np.clip(-yy, -1, 1)))
    lon = np.degrees(np.arctan2(x, zz)) + lon0
    u = ((lon % 360) / 360 * TW).astype(np.int32) % TW
    v = np.clip(((90 - lat) / 180 * TH).astype(np.int32), 0, TH - 1)
    col = globe_tex(mig)[v, u]
    if freeze > 0:
        fz = (FREEZE_ORD[v, u] < freeze)[..., None]
        ice = np.array([0.86, 0.92, 0.98]) - 0.08 * CLOUD[v, u][..., None]
        col = np.where(fz, ice, col)
    if clouds > 0:
        cu = (((lon + cloud_lon) % 360) / 360 * TW).astype(np.int32) % TW
        if wind > 0:
            cu = (cu + (wind * 40 * np.sin(np.radians(lat) * 3)).astype(np.int32)) % TW
        ca = CLOUD[v, cu][..., None] * clouds
        col = col * (1 - ca) + ca * 0.97
    if haze:
        hl0, hlo0, hrad, hs = haze
        la0, lo0r = math.radians(hl0), math.radians(hlo0)
        lr, lor = np.radians(lat), np.radians(lon)
        cd = np.sin(lr) * math.sin(la0) + np.cos(lr) * math.cos(la0) * np.cos(lor - lo0r)
        dd = np.degrees(np.arccos(np.clip(cd, -1, 1)))
        hf = (np.clip((hrad - dd) / 25, 0, 1) * hs)[..., None]
        hn = (0.5 + 0.5 * CLOUD[v, u])[..., None]
        col = col * (1 - hf) + hf * np.array([0.36, 0.29, 0.22]) * (0.8 + 0.4 * hn)
    if hot:
        hl0, hlo0, hrad, hs = hot
        la0, lo0r = math.radians(hl0), math.radians(hlo0)
        lr, lor = np.radians(lat), np.radians(lon)
        cd = np.sin(lr) * math.sin(la0) + np.cos(lr) * math.cos(la0) * np.cos(lor - lo0r)
        dd = np.degrees(np.arccos(np.clip(cd, -1, 1)))
        hotf = (np.clip(1 - dd / hrad, 0, 1) ** 1.5 * hs)[..., None]
    sx, sy, sz = sun; sl = math.sqrt(sx * sx + sy * sy + sz * sz); sx, sy, sz = sx / sl, sy / sl, sz / sl
    ndl = x * sx + y * sy + z * sz
    diff = np.clip(ndl, 0, 1)[..., None]
    light = night + (1 - night) * diff ** 0.8
    out = col * light
    # specular on water
    hx, hy, hz = sx, sy, sz + 1; hl = math.sqrt(hx * hx + hy * hy + hz * hz)
    spec = np.clip((x * hx + y * hy + z * hz) / hl, 0, 1) ** 140
    water = (col[..., 2] > col[..., 0] + .15)[..., None]
    out = out + water * spec[..., None] * 0.22
    if term_glow > 0:
        band = np.clip(1 - np.abs(ndl) / 0.07, 0, 1)[..., None] ** 1.5
        out = out + band * term_glow * np.array([0.45, 0.2, 0.04])
    # limb darkening + atmosphere tint
    limb = np.clip(1 - r2, 0, 1)[..., None] ** 0.25
    out = out * (0.55 + 0.45 * limb) + (1 - limb) * np.array([0.25, 0.45, 0.9]) * 0.35 * diff
    out = out * bright * np.array(tint)
    if hot: out = out + hotf * np.array([1.0, 0.55, 0.15])
    out = np.clip(out, 0, 1)
    a = np.clip((1 - r2) * R * 0.7, 0, 1) * inside
    img = np.zeros((2 * R, 2 * R, 4), np.uint8)
    img[..., 0] = (out[..., 2] * a * 255).astype(np.uint8)
    img[..., 1] = (out[..., 1] * a * 255).astype(np.uint8)
    img[..., 2] = (out[..., 0] * a * 255).astype(np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    surf = cairo.ImageSurface.create_for_data(memoryview(bytearray(img.tobytes())), cairo.FORMAT_ARGB32, 2 * R, 2 * R)
    return surf

def draw_globe(cr, cx, cy, R, sun=(-.6, -.35, .72), atmo=1.0, **kw):
    sl = math.sqrt(sum(s * s for s in sun))
    # atmosphere glow, brighter on the lit side
    gx, gy = cx + sun[0] / sl * R * .12, cy + sun[1] / sl * R * .12
    g = cairo.RadialGradient(gx, gy, R * .95, gx, gy, R * 1.22)
    g.add_color_stop_rgba(0, .45, .7, 1, .55 * atmo); g.add_color_stop_rgba(1, .45, .7, 1, 0)
    cr.set_source(g); cr.arc(gx, gy, R * 1.25, 0, 7); cr.fill()
    s = render_globe(int(R), sun=sun, **kw)
    cr.set_source_surface(s, cx - int(R), cy - int(R)); cr.paint()

def globe_point(cx, cy, R, lat, lon, lon0=0.0, tilt=0.35):
    """screen position of lat/lon on the globe (None if hidden)"""
    la, lo = math.radians(lat), math.radians(lon - lon0)
    X = math.cos(la) * math.sin(lo); Yw = -math.sin(la); Z = math.cos(la) * math.cos(lo)
    ct, st = math.cos(tilt), math.sin(tilt)
    y = Yw * ct + Z * st; z = -Yw * st + Z * ct
    return (cx + X * R, cy + y * R, z)

# ---------------- space background ----------------
_rng = np.random.default_rng(3)
STARS = [(float(_rng.uniform(0, W)), float(_rng.uniform(0, H)), float(_rng.uniform(.6, 2.6)), float(_rng.uniform(.3, 1))) for _ in range(380)]
def space(cr, t=0.0, sun_at=None):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, .02, .03, .07); g.add_color_stop_rgb(1, .04, .05, .11)
    cr.set_source(g); cr.paint()
    for x, y, r, a in STARS:
        tw = .75 + .25 * math.sin(t * 2 + x)
        circle(cr, x, y, r, (1, 1, 1), a * tw)
    if sun_at:
        x, y, r = sun_at
        g = cairo.RadialGradient(x, y, 0, x, y, r * 6)
        g.add_color_stop_rgba(0, 1, .98, .9, 1); g.add_color_stop_rgba(.12, 1, .9, .6, .9); g.add_color_stop_rgba(.4, 1, .7, .3, .25); g.add_color_stop_rgba(1, 1, .6, .2, 0)
        cr.set_source(g); cr.arc(x, y, r * 6, 0, 7); cr.fill()

# ---------------- realistic iso ----------------
class IsoR(Iso):
    def __init__(self, *a, light=(1.1, 0.35), shadow=.28, warm=None, **k):
        super().__init__(*a, **k); self.light, self.shadow_a, self.warm = light, shadow, warm
    def draw(self, night=0.0):
        cr = self.cr; P = self.P
        for a, c, pts in self.flat:
            poly(cr, [P(*p) for p in pts], c, a, edge=0)
        # cast shadows
        lx, ly = self.light
        cr.set_source_rgba(0.05, 0.06, 0.12, self.shadow_a)
        for k, it in self.items:
            if it[0] != 'box': continue
            _, x, y, z, w, d, h, c, deco, top, a = it
            if h <= 0.02 or a < .5: continue
            hh = z + h
            pts = [(x, y), (x + w, y), (x + w, y + d), (x, y + d)]
            sh = pts + [(px - lx * hh, py - ly * hh) for px, py in pts]
            if z > 0.05: sh = [(px - lx * z, py - ly * z) for px, py in pts] + [(px - lx * hh, py - ly * hh) for px, py in pts]
            scr = [P(px, py, 0.003) for px, py in sh]
            hull = _hull(scr)
            cr.move_to(*hull[0]); [cr.line_to(*q) for q in hull[1:]]; cr.close_path(); cr.fill()
        for k, it in sorted(self.items, key=lambda i: i[0]):
            if it[0] == 'fn': it[1](self); continue
            _, x, y, z, w, d, h, c, deco, top, a = it
            if h > 0:
                _gface(cr, [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], shade(c, 0.74), a)
                _gface(cr, [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(c, 0.92), a)
            tp = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
            tc = top or shade(c, 1.08)
            g = cairo.LinearGradient(tp[0][0], tp[0][1], tp[2][0], tp[2][1])
            g.add_color_stop_rgba(0, *shade(tc, 1.06), a); g.add_color_stop_rgba(1, *shade(tc, .96), a)
            cr.move_to(*tp[0]); [cr.line_to(*q) for q in tp[1:]]; cr.close_path(); cr.set_source(g); cr.fill()
            if deco: deco(self, x, y, z, w, d, h)
        if night > 0:
            cr.save(); cr.set_operator(cairo.OPERATOR_MULTIPLY)
            cr.set_source_rgba(*mix((1, 1, 1), C['night'], night), 1); cr.paint(); cr.restore()
            for pts, c, a in self.glows: poly(cr, pts, c, a, edge=0)
        for fn in self.after: fn(self)

def _gface(cr, pts, c, a):
    g = cairo.LinearGradient(pts[3][0], pts[3][1], pts[0][0], pts[0][1])
    g.add_color_stop_rgba(0, *shade(c, 1.05), a); g.add_color_stop_rgba(.8, *c, a); g.add_color_stop_rgba(1, *shade(c, .72), a)
    cr.move_to(*pts[0]); [cr.line_to(*q) for q in pts[1:]]; cr.close_path(); cr.set_source(g); cr.fill()

def _hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3: return pts
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

# ---------------- post FX ----------------
_grain = []
for i in range(6):
    n = (np.random.default_rng(100 + i).standard_normal((H // 2, W // 2)) * 18 + 128).clip(0, 255).astype(np.uint8)
    img = np.zeros((H // 2, W // 2, 4), np.uint8); img[..., 0] = img[..., 1] = img[..., 2] = n; img[..., 3] = 255
    _grain.append(cairo.ImageSurface.create_for_data(memoryview(bytearray(img.tobytes())), cairo.FORMAT_ARGB32, W // 2, H // 2))

def post(cr, t, vignette=.42, grain=.09, warm=0.0):
    if warm:
        cr.save(); cr.set_operator(cairo.OPERATOR_SOFT_LIGHT); cr.set_source_rgba(1, .6, .3, warm); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, H * .32, W / 2, H / 2, H * .75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, vignette)
    cr.set_source(g); cr.paint()
    cr.save(); cr.set_operator(cairo.OPERATOR_OVERLAY); cr.scale(2, 2)
    cr.set_source_surface(_grain[int(t * 30) % 6], 0, 0); cr.paint_with_alpha(grain); cr.restore()

def sky_r(cr, top, mid, bot, sun=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(.55, *mid); g.add_color_stop_rgb(1, *bot)
    cr.set_source(g); cr.paint()
    if sun:
        x, y, r, col = sun
        g = cairo.RadialGradient(x, y, 0, x, y, r * 7)
        g.add_color_stop_rgba(0, 1, .97, .85, 1); g.add_color_stop_rgba(.14, *col, .85); g.add_color_stop_rgba(1, *col, 0)
        cr.set_source(g); cr.arc(x, y, r * 7, 0, 7); cr.fill()


# ---------------- asteroid (lumpy textured rock) ----------------
_rk = fbm(512, 256, 6, seed=33, base=5); _rk = (_rk - _rk.mean()) / _rk.std()
_rng2 = np.random.default_rng(8)
RLAT = np.linspace(90, -90, 256)[:, None] * np.ones((1, 512)); RLON = np.linspace(0, 360, 512, endpoint=False)[None, :] * np.ones((256, 1))
_rk2 = fbm(512, 256, 4, seed=34, base=24); _rk2 = (_rk2 - _rk2.mean()) / _rk2.std()
ROCK = 0.42 + 0.07 * _rk + 0.03 * _rk2
for _ in range(40):
    cla, clo, cr_ = _rng2.uniform(-70, 70), _rng2.uniform(0, 360), _rng2.uniform(4, 16)
    dlon = (RLON - clo + 180) % 360 - 180
    d = np.sqrt((RLAT - cla) ** 2 + (dlon * np.cos(np.radians(cla))) ** 2) / cr_
    ROCK = ROCK - 0.09 * np.clip(1 - d, 0, 1) ** .7 + 0.035 * np.clip(1 - np.abs(d - 1) * 3, 0, 1)
ROCK = np.clip(ROCK, 0.1, 0.8)
_lump = [(_rng2.uniform(.015, .045), _rng2.integers(2, 6), _rng2.uniform(0, 6.28)) for _ in range(5)]

def render_rock(R, rot=0.0, sun=(-.6, -.5, .6), heat=0.0):
    n = 2 * R
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (xs + .5 - R) / R; y = (ys + .5 - R) / R
    th = np.arctan2(y, x); rr = np.sqrt(x * x + y * y)
    lim = 0.86 + sum(a * np.sin(k * th + p + rot * .3) for a, k, p in _lump)
    inside = rr <= lim
    rn = np.clip(rr / lim, 0, 1)
    xx, yy = x / lim, y / lim
    z = np.sqrt(np.clip(1 - rn * rn, 0, 1))
    lat = np.degrees(np.arcsin(np.clip(-yy, -1, 1)))
    lon = np.degrees(np.arctan2(xx, z)) + rot
    u = ((lon % 360) / 360 * 512).astype(np.int32) % 512
    v = np.clip(((90 - lat) / 180 * 256).astype(np.int32), 0, 255)
    alb = ROCK[v, u]
    # bump: finite differences of the texture
    ub = (u + 2) % 512; vb = np.clip(v + 2, 0, 255)
    gx = (ROCK[v, ub] - alb) * 2.5; gy = (ROCK[vb, u] - alb) * 2.5
    nx, ny, nz = xx + gx, yy + gy, z
    nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-6
    sx, sy, sz = sun; sl = math.sqrt(sx * sx + sy * sy + sz * sz)
    dif = np.clip((nx * sx + ny * sy + nz * sz) / nl / sl, 0, 1)
    shade_ = 0.06 + 0.94 * dif
    col = np.stack([alb * 1.0, alb * .9, alb * .8], -1) * shade_[..., None]
    if heat > 0:
        rim = np.clip(1 - z, 0, 1)[..., None] ** 2
        col = col + heat * rim * np.array([1.2, .55, .15]) + heat * .25 * np.array([1, .4, .1])
    col = np.clip(col, 0, 1)
    a = inside.astype(np.float32) * np.clip((lim - rr) * R * .8, 0, 1)
    img = np.zeros((n, n, 4), np.uint8)
    img[..., 0] = (col[..., 2] * a * 255).astype(np.uint8); img[..., 1] = (col[..., 1] * a * 255).astype(np.uint8)
    img[..., 2] = (col[..., 0] * a * 255).astype(np.uint8); img[..., 3] = (a * 255).astype(np.uint8)
    return cairo.ImageSurface.create_for_data(memoryview(bytearray(img.tobytes())), cairo.FORMAT_ARGB32, n, n)

def draw_rock(cr, cx, cy, R, **kw):
    R = max(8, int(R))
    s = render_rock(R, **kw); cr.set_source_surface(s, cx - R, cy - R); cr.paint()
