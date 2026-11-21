import math, random, json
import cairo

W, H, FPS = 1080, 1920, 30
FONT = "Lilita One"

# ---------- helpers ----------
def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def shade(c, f): return tuple(max(0, min(1, v * f)) for v in c)
def mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.9; return max(0.002, 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2)
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def keys(t, ks):
    """piecewise eased interpolation over [(time, value), ...]; values may be tuples"""
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            e = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple): return tuple(a + (b - a) * e for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * e
    return ks[-1][1]

C = {k: hexc(v) for k, v in dict(
    sky='#8FD3FF', sky2='#C9EDFF', grass='#7BD15A', grass2='#69BF4B', road='#5E6670', walk='#D9D4C7',
    line='#F4F1E8', wall='#F3EBDD', roof='#E8623A', roof2='#C94E2B', glass='#7FB8E0', win='#4E7FA8',
    skin='#F2C29B', hair='#5B3A1E', jacket='#E2453C', pants='#2F5DA8', shoe='#2B2B2B', white='#FFFFFF',
    yellow='#FFD23F', red='#E8473C', green='#3CC46A', dark='#22262E', trunk='#8A5A35', leaf='#4FB548',
    leaf2='#3E9E3B', dog='#C98B4E', dog2='#8E5B2E', concrete='#B9BEC6', water='#4AA8F0', soil='#C98B55',
    soil2='#A86F42', soil3='#8C5A36', night='#2B3566', can='#C9D1DA', metal='#8D96A3', brown='#9B6A3F',
    panel='#2D4A86', sun='#FFC93C', smoke='#F2F2F2', bsmoke='#3A3A3A', rot='#7C7A3A', purple='#8E6CD8',
    orange='#F59A3B', pink='#F27AA6').items()}

def ctx_for(surf):
    cr = cairo.Context(surf)
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    return cr

def fill(cr, c, a=1.0): cr.set_source_rgba(*c, a); cr.fill()
def poly(cr, pts, c, a=1.0, edge=0.10):
    cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    cr.close_path()
    cr.set_source_rgba(*c, a)
    if edge:
        cr.fill_preserve(); cr.set_source_rgba(0, 0, 0, edge * a); cr.set_line_width(1.2); cr.stroke()
    else: cr.fill()
def rrect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()
def circle(cr, x, y, r, c, a=1.0): cr.new_path(); cr.arc(x, y, r, 0, 2 * math.pi); fill(cr, c, a)

def sky(cr, top=None, bot=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *(top or C['sky'])); g.add_color_stop_rgb(1, *(bot or C['sky2']))
    cr.set_source(g); cr.paint()

# ---------- isometric world ----------
class Iso:
    def __init__(self, cr, cx, cy, cz, S, oy=0.47):
        self.cr, self.cx, self.cy, self.cz, self.S, self.oy = cr, cx, cy, cz, S, H * oy
        self.items, self.flat, self.glows, self.after = [], [], [], []
    def P(self, x, y, z=0.0):
        dx, dy, dz = x - self.cx, y - self.cy, z - self.cz
        return (W / 2 + (dx - dy) * 0.8660 * self.S, self.oy + (dx + dy) * 0.5 * self.S - dz * self.S)
    # flat things on ground (drawn first, in order)
    def quad(self, x, y, w, d, c, z=0.0, a=1.0):
        self.flat.append((a, c, [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)]))
    def ground(self, c, ext=400):
        self.quad(self.cx - ext, self.cy - ext, 2 * ext, 2 * ext, c)
    def box(self, x, y, z, w, d, h, c, deco=None, top=None, a=1.0, key=None):
        k = key if key is not None else (x + w / 2 + y + d / 2 + (z + h / 2) * 0.02)
        self.items.append((k, ('box', x, y, z, w, d, h, c, deco, top, a)))
    def custom(self, key, fn): self.items.append((key, ('fn', fn)))
    def draw(self, night=0.0):
        cr = self.cr
        for a, c, pts in self.flat:
            poly(cr, [self.P(*p) for p in pts], c, a, edge=0)
        for k, it in sorted(self.items, key=lambda i: i[0]):
            if it[0] == 'fn': it[1](self); continue
            _, x, y, z, w, d, h, c, deco, top, a = it
            P = self.P
            if h > 0:
                poly(cr, [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], shade(c, 0.80), a)
                poly(cr, [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(c, 0.93), a)
            poly(cr, [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)], top or shade(c, 1.07), a)
            if deco: deco(self, x, y, z, w, d, h)
        if night > 0:
            cr.save(); cr.set_operator(cairo.OPERATOR_MULTIPLY)
            cr.set_source_rgba(*mix((1, 1, 1), C['night'], night), 1); cr.paint(); cr.restore()
            for pts, c, a in self.glows:
                poly(cr, pts, c, a, edge=0)
        for fn in self.after: fn(self)
    # face helpers: face in 'x' (+x side), 'y' (+y side), 't' (top)
    def fpt(self, b, face, u, v):
        x, y, z, w, d, h = b
        if face == 'x': return self.P(x + w, y + u * d, z + v * h)
        if face == 'y': return self.P(x + u * w, y + d, z + v * h)
        return self.P(x + u * w, y + v * d, z + h)
    def frect(self, b, face, u0, v0, u1, v1, c, a=1.0, glow=False, edge=0.06):
        pts = [self.fpt(b, face, u0, v0), self.fpt(b, face, u1, v0), self.fpt(b, face, u1, v1), self.fpt(b, face, u0, v1)]
        f = 0.85 if face == 'x' else 1.0
        poly(self.cr, pts, shade(c, f), a, edge=edge)
        if glow: self.glows.append((pts, C['yellow'], 0.95))

# ---------- props ----------
def windows(rows, cols, color=None, lit=None, mx=0.12, my=0.18):
    color = color or C['win']
    def deco(iso, x, y, z, w, d, h):
        b = (x, y, z, w, d, h)
        for face, n in (('x', max(1, int(cols * d / max(w, d)))), ('y', max(1, int(cols * w / max(w, d))))):
            for r in range(rows):
                for cc in range(n):
                    u0 = (cc + mx) / n; u1 = (cc + 1 - mx) / n
                    v0 = (r + my) / rows; v1 = (r + 1 - my * 0.6) / rows
                    on = lit(r, cc, face) if lit else False
                    iso.frect(b, face, u0, v0, u1, v1, C['yellow'] if on else color, glow=on)
    return deco

def building(iso, x, y, w, d, floors, c, lit=None, glass=False):
    h = floors * 1.3
    if glass:
        iso.box(x, y, 0, w, d, h, C['glass'], deco=windows(floors, 6, color=shade(C['glass'], 1.12), lit=lit, mx=0.04, my=0.06))
    else:
        iso.box(x, y, 0, w, d, h, c, deco=windows(floors, 4, lit=lit))
    return h

def house(iso, x, y, w, d, h, wall=None, roof=None, lit=False, door=True):
    wall = wall or C['wall']; roof = roof or C['roof']
    def deco(iso, X, Y, Z, W_, D, Hh):
        b = (X, Y, Z, W_, D, Hh)
        if door: iso.frect(b, 'x', 0.42, 0.0, 0.62, 0.62, C['brown'])
        iso.frect(b, 'y', 0.2, 0.35, 0.45, 0.75, C['yellow'] if lit else C['win'], glow=lit)
        iso.frect(b, 'y', 0.58, 0.35, 0.83, 0.75, C['yellow'] if lit else C['win'], glow=lit)
        P = iso.P; z0 = Z + Hh; rh = D * 0.45
        poly(iso.cr, [P(X - .15, Y - .1, z0), P(X + W_ + .15, Y - .1, z0), P(X + W_ + .15, Y + D / 2, z0 + rh), P(X - .15, Y + D / 2, z0 + rh)], shade(roof, 0.85))
        poly(iso.cr, [P(X + W_, Y, z0), P(X + W_, Y + D, z0), P(X + W_, Y + D / 2, z0 + rh)], shade(wall, 0.8))
        poly(iso.cr, [P(X - .15, Y + D / 2, z0 + rh), P(X + W_ + .15, Y + D / 2, z0 + rh), P(X + W_ + .15, Y + D + .1, z0), P(X - .15, Y + D + .1, z0)], roof)
    iso.box(x, y, 0, w, d, h, wall, deco=deco)

def tree(iso, x, y, s=1.0, g=1.0):
    if g <= 0: return
    s *= g
    iso.box(x - .15 * s, y - .15 * s, 0, .3 * s, .3 * s, 1.0 * s, C['trunk'])
    iso.box(x - .6 * s, y - .6 * s, 0.9 * s, 1.2 * s, 1.2 * s, 1.0 * s, C['leaf'], key=x + y + 0.05)
    iso.box(x - .35 * s, y - .35 * s, 1.85 * s, .7 * s, .7 * s, .5 * s, C['leaf2'], key=x + y + 0.06)

def car(iso, x, y, c, along='x'):
    if along == 'x':
        iso.box(x, y, 0.15, 2.2, 1.0, 0.5, c); iso.box(x + 0.5, y + 0.05, 0.65, 1.1, 0.9, 0.4, shade(c, 1.1),
            deco=lambda i, *b: (i.frect(b, 'x', .08, .1, .92, .9, C['glass']), i.frect(b, 'y', .1, .1, .9, .9, C['glass'])))
        for dx in (0.3, 1.6):
            iso.box(x + dx, y - .05, 0, .35, 1.1, .3, C['dark'])
    else:
        iso.box(x, y, 0.15, 1.0, 2.2, 0.5, c); iso.box(x + .05, y + .5, 0.65, .9, 1.1, 0.4, shade(c, 1.1),
            deco=lambda i, *b: (i.frect(b, 'x', .1, .1, .9, .9, C['glass']), i.frect(b, 'y', .08, .1, .92, .9, C['glass'])))
        for dy in (0.3, 1.6):
            iso.box(x - .05, y + dy, 0, 1.1, .35, .3, C['dark'])

def person(iso, x, y, z=0.0, phase=None, crouch=0.0, jacket=None, arms_up=0.0, bag=False, s=1.0):
    """small blocky person, ~1.8 units tall, facing +x+y (camera)."""
    j = jacket or C['jacket']; sw = math.sin(phase) * 0.18 if phase is not None else 0
    lz = 0.8 * (1 - 0.45 * crouch) * s
    k = x + y
    iso.box(x - .05 * s, y + .02 * s + sw * s, z, .22 * s, .22 * s, lz, C['pants'], key=k + .001)
    iso.box(x - .05 * s, y + .30 * s - sw * s, z, .22 * s, .22 * s, lz, C['pants'], key=k + .002)
    bz = z + lz
    iso.box(x - .1 * s, y - .02 * s, bz, .34 * s, .58 * s, .62 * s, j, key=k + .003,
            deco=lambda i, *b: i.frect(b, 'x', .45, .05, .55, .95, C['white'], edge=0))
    if bag: iso.box(x - .32 * s, y + .05 * s, bz + .1 * s, .22 * s, .48 * s, .5 * s, C['brown'], key=k - .1)
    au = arms_up
    for yy in (-.17, .56):
        if au > 0:
            iso.box(x - .02 * s, y + yy * s, bz + .45 * s, .16 * s, .16 * s, .55 * s * au + .1 * s, shade(j, .95), key=k + .004)
        else:
            iso.box(x - .02 * s, y + yy * s, bz + .05 * s - sw * .2 * s, .16 * s, .16 * s, .55 * s, shade(j, .95), key=k + .004)
    hz = bz + .62 * s
    def face(i, *b):
        i.frect(b, 'x', .2, .45, .38, .65, C['dark'], edge=0); i.frect(b, 'x', .62, .45, .8, .65, C['dark'], edge=0)
        i.frect(b, 'x', .35, .18, .65, .26, shade(C['skin'], .7), edge=0)
    iso.box(x - .12 * s, y - .02 * s, hz, .46 * s, .58 * s, .5 * s, C['skin'], deco=face, key=k + .005)
    iso.box(x - .14 * s, y - .04 * s, hz + .38 * s, .44 * s, .62 * s, .2 * s, C['hair'], key=k + .006)

def dog(iso, x, y, phase=0.0, along='x', eyes_glow=False, s=1.0, tail=0.0):
    c = C['dog']; sw = math.sin(phase) * .1 * s; k = x + y
    if along == 'x':
        for dx, sg in ((0.05, 1), (0.75, -1)):
            for dy in (0.0, 0.32):
                iso.box(x + dx * s + sg * sw, y + dy * s, 0, .15 * s, .15 * s, .4 * s, C['dog2'], key=k + .001)
        iso.box(x, y - .02 * s, .38 * s, 1.0 * s, .5 * s, .38 * s, c, key=k + .002)
        iso.box(x - .3 * s, y + .14 * s, .6 * s + tail * .05, .32 * s, .12 * s, .1 * s, c, key=k + .0015)
        def face(i, *b):
            col = C['yellow'] if eyes_glow else C['dark']
            i.frect(b, 'x', .12, .55, .3, .78, col, edge=0, glow=eyes_glow); i.frect(b, 'x', .7, .55, .88, .78, col, edge=0, glow=eyes_glow)
            i.frect(b, 'x', .4, .2, .6, .4, C['dark'], edge=0)
        iso.box(x + .85 * s, y - .04 * s, .55 * s, .45 * s, .58 * s, .45 * s, c, deco=face, key=k + .003)
        iso.box(x + .9 * s, y - .06 * s, .95 * s, .15 * s, .15 * s, .15 * s, C['dog2'], key=k + .004)
        iso.box(x + .9 * s, y + .44 * s, .95 * s, .15 * s, .15 * s, .15 * s, C['dog2'], key=k + .004)
    else:
        for dy, sg in ((0.05, 1), (0.75, -1)):
            for dx in (0.0, 0.32):
                iso.box(x + dx * s, y + dy * s + sg * sw, 0, .15 * s, .15 * s, .4 * s, C['dog2'], key=k + .001)
        iso.box(x - .02 * s, y, .38 * s, .5 * s, 1.0 * s, .38 * s, c, key=k + .002)
        def face(i, *b):
            col = C['yellow'] if eyes_glow else C['dark']
            i.frect(b, 'y', .12, .55, .3, .78, col, edge=0, glow=eyes_glow); i.frect(b, 'y', .7, .55, .88, .78, col, edge=0, glow=eyes_glow)
            i.frect(b, 'y', .4, .2, .6, .4, C['dark'], edge=0)
        iso.box(x - .04 * s, y + .85 * s, .55 * s, .58 * s, .45 * s, .45 * s, c, deco=face, key=k + .003)

def can(iso, x, y, z, s=1.0, c=None, glow=0.0):
    c = c or C['can']
    def fn(i):
        cr = i.cr; px, py = i.P(x, y, z); r = .22 * s * i.S * 0.87; hh = .5 * s * i.S
        if glow > 0:
            g = cairo.RadialGradient(px, py - hh / 2, 0, px, py - hh / 2, r * 3)
            g.add_color_stop_rgba(0, 1, .95, .6, .6 * glow); g.add_color_stop_rgba(1, 1, .95, .6, 0)
            cr.set_source(g); cr.arc(px, py - hh / 2, r * 3, 0, 7); cr.fill()
        cr.save(); cr.translate(px, py); cr.scale(1, 0.5); cr.arc(0, 0, r, 0, math.pi); cr.restore()
        cr.line_to(px - r, py - hh); cr.line_to(px + r, py - hh); cr.close_path(); fill(cr, shade(c, .85))
        cr.rectangle(px - r, py - hh * .7, 2 * r, hh * .4); fill(cr, C['red'])
        cr.save(); cr.translate(px, py - hh); cr.scale(1, .5); cr.arc(0, 0, r, 0, 7); cr.restore(); fill(cr, shade(c, 1.1))
    iso.custom(x + y + z * .02, fn)

# ---------- 2D front-view character ----------
def front_char(cr, cx, by, s, expr='smile', arm='down', t=0.0, jacket=None, light=None):
    """cx = center x, by = feet y, s = total height px"""
    j = jacket or C['jacket']
    u = s / 10.0
    def part(x, y, w, h, c, r=0.25):
        rrect(cr, cx + x * u, by - y * u, w * u, h * u, r * u); fill(cr, c)
        rrect(cr, cx + (x + w * .55) * u, by - y * u, w * .45 * u, h * u, r * u); fill(cr, shade(c, .88))
    # legs
    part(-1.25, 3.1, 1.1, 3.0, C['pants']); part(0.15, 3.1, 1.1, 3.0, C['pants'])
    part(-1.4, 0.45, 1.35, 0.45, C['shoe']); part(0.05, 0.45, 1.35, 0.45, C['shoe'])
    # torso
    part(-1.75, 6.1, 3.5, 3.2, j, .5)
    rrect(cr, cx - .08 * u, by - 6.0 * u, .16 * u, 3.0 * u, .05 * u); fill(cr, shade(j, 1.25))
    # arms
    def arm_seg(x, y, w, h, ang, px, py):
        cr.save(); cr.translate(cx + px * u, by - py * u); cr.rotate(ang)
        rrect(cr, x * u, y * u, w * u, h * u, .3 * u); fill(cr, shade(j, .92))
        rrect(cr, (x + .1) * u, (y + h - .7) * u, (w - .2) * u, .7 * u, .3 * u); fill(cr, C['skin'])
        cr.restore()
    wob = math.sin(t * 9) * 0.25
    if arm == 'up':
        arm_seg(-.4, -3.0, .85, 3.0, -0.5 + wob, -1.8, 5.8); arm_seg(-.45, -3.0, .85, 3.0, 0.5 - wob, 1.8, 5.8)
    elif arm == 'nose':
        arm_seg(-.42, 0, .85, 2.9, 0.12, -1.85, 5.9); arm_seg(-.42, 0, .85, 2.4, 2.65, 1.85, 5.6)
    elif arm == 'flash':
        arm_seg(-.42, 0, .85, 2.9, 0.12, -1.85, 5.9); arm_seg(-.42, 0, .85, 2.6, 2.0, 1.85, 5.6)
    else:
        arm_seg(-.42, 0, .85, 2.9, 0.12, -1.85, 5.9); arm_seg(-.42, 0, .85, 2.9, -0.12, 1.85, 5.9)
    # neck + head
    part(-.45, 6.4, .9, .5, shade(C['skin'], .9))
    part(-1.9, 10.0, 3.8, 3.7, C['skin'], .7)
    part(-2.0, 10.25, 4.0, 1.25, C['hair'], .6); part(-2.0, 9.3, .55, 1.6, C['hair'], .2); part(1.45, 9.3, .55, 1.6, C['hair'], .2)
    ey = by - 8.0 * u
    if expr in ('smile', 'O', 'shock', 'sad', 'happy'):
        er = .32 * u if expr != 'shock' else .42 * u
        for ex in (-.85, .85):
            circle(cr, cx + ex * u, ey, er, C['dark']); circle(cr, cx + ex * u + er * .3, ey - er * .3, er * .3, C['white'])
    if expr == 'disgust':
        for ex in (-.85, .85):
            cr.set_source_rgb(*C['dark']); cr.set_line_width(.22 * u)
            cr.move_to(cx + (ex - .35) * u, ey); cr.line_to(cx + (ex + .35) * u, ey); cr.stroke()
    my = by - 7.0 * u
    cr.set_source_rgb(*shade(C['skin'], .45)); cr.set_line_width(.2 * u); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    if expr in ('smile', 'happy'):
        cr.arc(cx, my - .3 * u, .7 * u, .3, math.pi - .3); cr.stroke()
    elif expr in ('O', 'shock'):
        cr.save(); cr.translate(cx, my); cr.scale(1, 1.3); cr.arc(0, 0, .35 * u if expr == 'O' else .5 * u, 0, 7); cr.restore(); fill(cr, C['dark'])
    elif expr == 'sad':
        cr.arc_negative(cx, my + .6 * u, .6 * u, -.4, -math.pi + .4); cr.stroke()
    elif expr == 'disgust':
        cr.move_to(cx - .6 * u, my); cr.curve_to(cx - .2 * u, my - .3 * u, cx + .2 * u, my + .3 * u, cx + .6 * u, my); cr.stroke()
    if arm == 'flash':
        hx, hy = cx + 1.85 * u + math.sin(2.0) * 2.6 * u, by - 5.6 * u + math.cos(2.0) * 2.6 * u * -1
        rrect(cr, hx - .4 * u, hy - .3 * u, 1.2 * u, .6 * u, .1 * u); fill(cr, C['dark'])

# ---------- text overlays ----------
def text_center(cr, txt, x, y, size, fillc, stroke=None, sw=0.0, rot=0.0, scale=1.0, alpha=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(scale, scale)
    cr.set_font_size(size)
    ext = cr.text_extents(txt)
    cr.move_to(-ext.x_advance / 2, size * 0.35)
    cr.text_path(txt)
    if stroke:
        cr.set_source_rgba(*stroke, alpha); cr.set_line_width(sw); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke_preserve()
    cr.set_source_rgba(*fillc, alpha); cr.fill(); cr.restore()
    return ext.x_advance * scale

def fit(cr, txt, size, maxw):
    cr.set_font_size(size); w = cr.text_extents(txt).x_advance
    return size if w <= maxw else size * maxw / w

def caption(cr, t, words):
    cur = None
    for i, w in enumerate(words):
        nxt = words[i + 1]['t0'] if i + 1 < len(words) else w['t1'] + .4
        end = min(nxt, w['t1'] + 0.35)
        if w['t0'] - 0.03 <= t < end: cur = w; break
    if not cur: return
    txt = cur['w'].strip('.,:;?!…"').replace('...', '')
    txt = txt[:1].upper() + txt[1:]
    pop = 1.0 + 0.18 * (1 - eout((t - cur['t0']) / 0.12))
    size = fit(cr, txt, 104, 900)
    col = C['yellow'] if cur['key'] else C['white']
    cr.save(); cr.translate(5, 7)
    text_center(cr, txt, W / 2, 1450, size, (0, 0, 0), stroke=(0, 0, 0), sw=16, scale=pop, alpha=0.35); cr.restore()
    text_center(cr, txt, W / 2, 1450, size, col, stroke=C['dark'], sw=14, scale=pop)

def pill(cr, t, t0, t1, txt, x, y, dot=None, size=46):
    if not (t0 <= t < t1): return
    a = min(1, (t1 - t) / 0.15)
    sc = back((t - t0) / 0.28)
    dot = dot or C['red']
    cr.save(); cr.translate(x, y); cr.scale(sc, sc)
    cr.set_font_size(size); tw = cr.text_extents(txt).x_advance
    w = tw + size * 1.9; h = size * 1.55
    rrect(cr, -w / 2 + 4, -h / 2 + 6, w, h, h / 2); fill(cr, (0, 0, 0), .25 * a)
    rrect(cr, -w / 2, -h / 2, w, h, h / 2); fill(cr, C['white'], a)
    circle(cr, -w / 2 + size * .75, 0, size * .24, dot, a)
    cr.move_to(-w / 2 + size * 1.25, size * .36); cr.text_path(txt); fill(cr, C['dark'], a)
    cr.restore()

def title(cr, t, t0, t1, txt, y=330, size=124, tilt=-0.07, col=None, sub=None):
    if not (t0 <= t < t1): return
    a = min(1, (t1 - t) / 0.15)
    sc = back((t - t0) / 0.32)
    col = col or C['yellow']
    size = fit(cr, txt, size, 960)
    cr.save(); cr.translate(6, 8)
    text_center(cr, txt, W / 2, y, size, (0, 0, 0), stroke=(0, 0, 0), sw=18, rot=tilt, scale=sc, alpha=.3 * a); cr.restore()
    text_center(cr, txt, W / 2, y, size, col, stroke=C['dark'], sw=16, rot=tilt, scale=sc, alpha=a)
    if sub:
        text_center(cr, sub, W / 2, y + size * .85, fit(cr, sub, 50, 940), C['white'], stroke=C['dark'], sw=9, rot=tilt, scale=sc, alpha=a)

def counter(cr, t, t0, t1, txt, label=None, y=250):
    if not (t0 <= t < t1): return
    a = min(1, (t1 - t) / 0.15); sc = back((t - t0) / 0.25)
    text_center(cr, txt, W / 2, y, fit(cr, txt, 150, 980), C['white'], stroke=C['dark'], sw=16, scale=sc, alpha=a)
    if label: text_center(cr, label, W / 2, y + 105, 50, C['white'], stroke=C['dark'], sw=9, scale=sc, alpha=a)
