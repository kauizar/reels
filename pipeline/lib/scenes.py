import math, random, json
import cairo
from engine import *

WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes.json')))
def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

# ---------- shared bits ----------
def clouds(cr, t, n=5, seed=3, alpha=1.0, y0=120, y1=700):
    r = random.Random(seed)
    for i in range(n):
        x = (r.uniform(0, W) + t * r.uniform(8, 20)) % (W + 400) - 200
        y = r.uniform(y0, y1); s = r.uniform(.7, 1.3)
        for dx, dy, rr in ((0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 15, 50)):
            circle(cr, x + dx * s, y + dy * s, rr * s, C['white'], .95 * alpha)

def stars(cr, seed=5, a=1.0):
    r = random.Random(seed)
    for _ in range(90): circle(cr, r.uniform(0, W), r.uniform(0, 900), r.uniform(1.5, 3.5), C['white'], a * r.uniform(.4, 1))

def night_sky(cr, moon=True):
    sky(cr, hexc('#141A3A'), hexc('#2E3B78')); stars(cr)
    if moon: circle(cr, 820, 330, 70, hexc('#FFF3C4')); circle(cr, 850, 310, 70, hexc('#141A3A'), .0)

ROAD = 14.0
def city_ents(seed=1, special=None, rng=4, low=()):
    r = random.Random(seed); ents = []
    special = special or {}
    pal = [hexc(c) for c in ('#F3EBDD', '#F6D7B0', '#DDE8F0', '#F2C6C2', '#E8E3F4')]
    bpal = [hexc(c) for c in ('#D7DCE3', '#E9D9C4', '#C9D6E3', '#F0E2C8')]
    for bx in range(-rng, rng):
        for by in range(-rng, rng):
            if (bx, by) in special: ents.append(('special', bx, by)); continue
            ox, oy = bx * ROAD + 2.0, by * ROAD + 2.0
            for lx in (0, 5.5):
                for ly in (0, 5.5):
                    x, y = ox + lx, oy + ly; k = r.random()
                    if (bx, by) in low and .55 <= k < .85: k = .2
                    if k < .55:
                        ents.append(('house', x + .5, y + .7, 3.6, 3.4, r.uniform(1.9, 2.4), r.choice(pal), r.random()))
                        ents.append(('tree', x + 4.3, y + 4.4, r.uniform(.6, .8)))
                    elif k < .85:
                        ents.append(('bld', x + .2, y + .2, 4.6, 4.6, r.randint(3, 9), r.choice(bpal), r.random() < .3))
                    else:
                        for _ in range(3): ents.append(('tree', x + r.uniform(1, 4), y + r.uniform(1, 4), r.uniform(.7, 1)))
    return ents

def roads(iso, rng=4, green=0.0, cracks=None):
    iso.ground(C['grass'])
    for k in range(-rng, rng + 1):
        c = k * ROAD
        iso.quad(c - 1.9, -rng * ROAD, 3.8, 2 * rng * ROAD, C['walk'], z=0.005)
        iso.quad(-rng * ROAD, c - 1.9, 2 * rng * ROAD, 3.8, C['walk'], z=0.005)
    for k in range(-rng, rng + 1):
        c = k * ROAD
        iso.quad(c - 1.5, -rng * ROAD, 3.0, 2 * rng * ROAD, C['road'], z=0.01)
        iso.quad(-rng * ROAD, c - 1.5, 2 * rng * ROAD, 3.0, C['road'], z=0.01)
        for j in range(-rng * 7, rng * 7):
            iso.quad(c - .08, j * 2.0, .16, 1.0, C['line'], z=0.012)
            iso.quad(j * 2.0, c - .08, 1.0, .16, C['line'], z=0.012)
    if green > 0:
        r = random.Random(9)
        for _ in range(140):
            k = r.randint(-rng, rng) * ROAD; p = r.uniform(-rng * ROAD, rng * ROAD); s = r.uniform(.5, 2.0) * green
            if r.random() < .5: iso.quad(k - 1.4 + r.uniform(0, 2), p, s, s * 1.4, C['grass2'], z=0.015)
            else: iso.quad(p, k - 1.4 + r.uniform(0, 2), s * 1.4, s, C['grass2'], z=0.015)

def vine_deco(base, g, seed):
    r = random.Random(seed); cols = [(r.uniform(0, .8), r.uniform(.1, .2), r.uniform(.4, 1.0)) for _ in range(5)]
    def deco(iso, x, y, z, w, d, h):
        if base: base(iso, x, y, z, w, d, h)
        b = (x, y, z, w, d, h)
        for i, (u, uw, hmax) in enumerate(cols):
            v = g * hmax
            if v > 0.02: iso.frect(b, 'x' if i % 2 else 'y', u, 0, u + uw, v, C['leaf2'], edge=0)
    return deco

def draw_ents(iso, ents, specials=None, lit=None, green=0.0, R=60):
    for e in ents:
        if e[0] == 'special':
            if specials: specials(iso, e[1], e[2]); continue
        x, y = e[1], e[2]
        if abs(x - iso.cx) + abs(y - iso.cy) > R: continue
        if e[0] == 'house':
            on = lit(x, y) if lit else False
            house(iso, x, y, e[3], e[4], e[5], wall=e[6], lit=on)
            if green > 0:
                iso.box(x - .1, y + e[4] - .3, 0, .4, .4, e[5] * green * .8, C['leaf2'])
        elif e[0] == 'bld':
            fl = e[5]
            lf = (lambda r_, c_, f_, x=x, y=y: lit(x + c_ * .3, y + r_ * .2)) if lit else None
            if green > 0:
                base = windows(fl, 4, lit=lf) if not e[7] else windows(fl, 6, color=shade(C['glass'], 1.12), lit=lf, mx=.04, my=.06)
                iso.box(x, y, 0, e[3], e[4], fl * 1.3, C['glass'] if e[7] else e[6], deco=vine_deco(base, green, int(x * 7 + y)))
                if green > .4: tree_at(iso, x + e[3] / 2, y + e[4] / 2, fl * 1.3, .9 * ease((green - .4) / .6))
            else:
                building(iso, x, y, e[3], e[4], fl, e[6], lit=lf, glass=e[7])
        elif e[0] == 'tree':
            tree(iso, x, y, e[3] * (1 + green * .9))

def tree_at(iso, x, y, z, s):
    if s <= 0: return
    iso.box(x - .15 * s, y - .15 * s, z, .3 * s, .3 * s, .8 * s, C['trunk'])
    iso.box(x - .7 * s, y - .7 * s, z + .7 * s, 1.4 * s, 1.4 * s, 1.1 * s, C['leaf'])

def puff(iso, x, y, z, s, c, a=1.0):
    iso.box(x - s / 2, y - s / 2, z, s, s, s, c, a=a, key=x + y + z * .02 + 50)

# ======================= SCENES =======================
CITY = city_ents(1, low={(0, 0), (-1, 0), (0, -1)})

def s1(cr, t):
    if t < 1.66:
        sky(cr); clouds(cr, t, 4)
        e = eout(t / 1.6)
        front_char(cr, W / 2, 2350 - e * 120, 1700 + e * 120, 'smile', t=t)
        return
    tt = (t - 1.66) / 3.1
    S = keys(t, [(1.66, 330), (2.6, 120), (4.9, 26)]); cz = keys(t, [(1.66, 1.6), (3.0, 0.6), (4.9, 0)])
    sky(cr); clouds(cr, t, 4)
    iso = Iso(cr, 0.9, 0.9, cz, S, oy=keys(t, [(1.66, .5), (4.9, .52)]))
    roads(iso); draw_ents(iso, CITY, R=80)
    car(iso, 3.3, -0.6, C['purple'], 'y'); car(iso, -9, 0.3, C['orange'])
    person(iso, 0.6, 0.6)
    iso.draw()

def mansion(iso, bx, by):
    ox, oy = bx * ROAD + 2, by * ROAD + 2
    iso.quad(ox, oy, 11, 11, hexc('#9DE07A'), z=.003)
    iso.quad(ox + 1, oy + 7.2, 5.2, 3, C['water'], z=.02)
    iso.quad(ox + .8, oy + 7.0, 5.6, .2, C['white'], z=.025)
    def deco(i, x, y, z, w, d, h):
        b = (x, y, z, w, d, h)
        for u in (.08, .3, .55, .77):
            i.frect(b, 'x', u, .2, u + .15, .8, C['glass'])
            i.frect(b, 'y', u, .2, u + .15, .8, C['glass'])
    iso.box(ox + .5, oy + .5, 0, 8, 5.8, 2.6, C['white'], deco=deco)
    iso.box(ox + 2.2, oy + 1.5, 2.6, 5, 3.8, 2.1, hexc('#ECECEC'), deco=deco)
    for k in range(4): tree(iso, ox + 10.2, oy + 1 + k * 2.6, .8)

def mall(iso, bx, by):
    ox, oy = bx * ROAD + 2, by * ROAD + 2
    def deco(i, x, y, z, w, d, h):
        b = (x, y, z, w, d, h)
        i.frect(b, 'x', .05, .05, .95, .55, C['glass']); i.frect(b, 'y', .05, .05, .95, .55, C['glass'])
        i.frect(b, 'x', .35, 0, .65, .45, shade(C['glass'], .7))
    iso.box(ox, oy, 0, 11, 11, 4.5, hexc('#E7E2F2'), deco=deco)
    def sign(i):
        p = i.P(ox + 11, oy + 5.5, 5.4)
        cr = i.cr; sz = i.S * 1.25
        cr.save(); cr.translate(*p); cr.transform(cairo.Matrix(1, -0.577, 0, 1, 0, 0))
        text_center(cr, 'SHOPPING', 0, 0, sz, C['yellow'], stroke=C['dark'], sw=sz * .12); cr.restore()
    iso.custom(ox + oy + 30, sign)

def s2(cr, t):
    sp = {(1, 1): mansion, (2, 0): mall}
    def spec(iso, bx, by): sp[(bx, by)](iso, bx, by)
    ents = city_ents(1, special=sp, low={(0, 0), (2, 1), (1, 2), (2, 2), (3, 0), (3, 1), (1, 0)})
    cx = keys(t, [(5.2, 6), (7.4, 10), (8.3, 21), (9.2, 21), (9.6, 18), (11.1, 30), (11.6, 33.5), (13.6, 34.5), (16.2, 22)])
    cy = keys(t, [(5.2, 6), (7.4, 10), (8.3, 21), (9.2, 21), (9.6, 14), (11.1, 14), (11.6, 7.5), (13.6, 7.5), (16.2, 12)])
    S = keys(t, [(5.2, 24), (7.4, 26), (8.3, 52), (9.2, 55), (9.6, 62), (11.1, 62), (11.6, 40), (13.6, 42), (16.2, 21)])
    sky(cr); clouds(cr, t, 5)
    iso = Iso(cr, cx, cy, 0, S)
    roads(iso); draw_ents(iso, ents, specials=spec, R=70)
    carx = keys(t, [(9.3, 10), (11.3, 34)])
    car(iso, carx, 13.3, C['red'])
    if 7.6 < t < 9.4: person(iso, 21.5, 22.5, arms_up=1.0)
    if 11.2 < t < 13.8:
        px = keys(t, [(11.3, 38.5), (13.6, 35.3)])
        person(iso, px, 12.5, phase=t * 9)
    iso.draw(night=keys(t, [(13.8, 0), (16.1, .35)]))

def plant_scene(cr, t):
    sky(cr); clouds(cr, t, 3)
    iso = Iso(cr, keys(t, [(16.1, 3), (21, 4)]), 2, 4, keys(t, [(16.1, 44), (21, 52)]), oy=.6)
    iso.ground(C['grass'])
    iso.quad(-6, 9, 30, 4, C['road'], z=.01)
    iso.box(0, 0, 0, 9, 7, 4, hexc('#C7CCD4'), deco=windows(2, 6))
    iso.box(9.5, 1, 0, 3, 5, 2.5, hexc('#D9DDE3'))
    for i, cx in enumerate((1.5, 5.5)):
        for k in range(5):
            iso.box(cx, -2.5, 4 + (k - 1) * 1.6 if k else 0, 1.4, 1.4, 4 if k == 0 else 1.6, C['white'] if k % 2 else C['red'])
    for cx2 in (-5, -1.5):
        iso.box(cx2, 2, 0, 3, 3, 5, hexc('#E3E6EA')); iso.box(cx2 + .3, 2.3, 5, 2.4, 2.4, 1.2, hexc('#D4D8DE'))
    stop = 18.3
    for ch, cx in enumerate((2.2, 6.2)):
        for k in range(10):
            born = 16.0 + k * 0.28 + ch * .13
            while born + 2.8 < t: born += 2.8
            if born > stop or born > t: continue
            age = t - born
            puff(iso, cx + age * .6, -1.8 + age * .2, 12 + age * 2.2, .9 + age * .5, C['smoke'], a=clamp(1 - age / 2.8))
    for k in range(3):
        tower = k
    iso.draw()

def dusk_city(cr, t):
    sky(cr, hexc('#2A2F66'), hexc('#F08C5A'))
    iso = Iso(cr, 10, 10, 0, 22, oy=.5)
    wave = keys(t, [(21.0, 0), (22.2, 90)])
    lit = lambda x, y: (abs(x - 10) + abs(y - 10)) > wave and ((int(x * 3 + y * 7)) % 5 != 0)
    roads(iso); draw_ents(iso, CITY, lit=lit, R=80)
    iso.draw(night=.65)

def dark_char(cr, t):
    sky(cr, hexc('#0E1330'), hexc('#1C2450'))
    sw = math.sin(t * 2.2) * .25
    cr.save(); cr.translate(W / 2 + 120, 980)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 900)
    g.add_color_stop_rgba(0, 1, .96, .7, .55); g.add_color_stop_rgba(1, 1, .96, .7, 0)
    cr.move_to(0, 0); cr.arc(0, 0, 900, -0.25 + sw - math.pi / 2 + 1.0, 0.25 + sw - math.pi / 2 + 1.0); cr.close_path()
    cr.set_source(g); cr.fill(); cr.restore()
    front_char(cr, W / 2, 1900, 1300, 'O', arm='flash', t=t)

def gen_yard(cr, t, land=26.4, lights=27.0, night=.55, smoke=False, flicker=False):
    sky(cr, hexc('#1B2350'), hexc('#3B4C8C')) if night > .3 else sky(cr)
    iso = Iso(cr, 3.5, 2.5, .5, keys(t, [(land - .3, 85), (land + 2.5, 98)]) if land else 95, oy=.55)
    iso.ground(C['grass']); iso.quad(-4, 9, 20, 3, C['road'], z=.01)
    on = t > lights and not (flicker and math.sin(t * 23) > .3)
    house(iso, 0, 0, 5, 4.5, 2.6, lit=on)
    gz = 0
    if t < land + .5:
        p = prog(t, land - .6, land); gz = (1 - p * p) * 12
        if t > land: gz = abs(math.sin((t - land) * 9)) * .4 * (1 - prog(t, land, land + .5))
    sx = math.sin(t * 40) * .06 if smoke else 0
    def gdeco(i, *b):
        i.frect(b, 'x', .1, .3, .5, .8, C['dark']); i.frect(b, 'y', .15, .5, .85, .8, hexc('#2D7F3E'))
    iso.box(6.0 + sx, 2.2, gz, 1.6, 1.1, 1.0, hexc('#F2B33D'), deco=gdeco)
    if on and t > lights:
        iso.after.append(lambda i: None)
    if smoke:
        for k in range(12):
            born = 79.3 + k * .25
            if born > t: continue
            age = t - born
            if age > 2.5: continue
            puff(iso, 6.3 + age * .4, 2.5, 1.2 + age * 1.5, .4 + age * .45, C['bsmoke'], a=clamp(1 - age / 2.5) * .9)
    iso.draw(night=night)
    if t > land and t < land + .6:
        p = prog(t, land, land + .6); x, y = iso.P(6.8, 2.75, 0)
        for k in range(8):
            a = k / 8 * 6.28
            circle(cr, x + math.cos(a) * 120 * p, y + math.sin(a) * 50 * p, 18 * (1 - p), C['white'], .8 * (1 - p))

def s3(cr, t):
    if t < 21.0: plant_scene(cr, t)
    elif t < 22.3: dusk_city(cr, t)
    elif t < 26.2: dark_char(cr, t)
    else: gen_yard(cr, t)

# ---------- S4 supermarket ----------
PROD = [hexc(c) for c in ('#E8473C', '#F59A3B', '#FFD23F', '#7BD15A', '#F27AA6', '#FFFFFF')]
def market(cr, t):
    sky(cr, hexc('#EEF2F5'), hexc('#DCE3EA'))
    rot = prog(t, 29.3, 32.0)
    iso = Iso(cr, keys(t, [(28.65, 3), (35.4, 5)]), 5, 1, keys(t, [(28.65, 88), (35.4, 98)]), oy=.5)
    for i in range(-8, 16):
        for j in range(-8, 16):
            iso.quad(i * 2, j * 2, 2, 2, hexc('#E9ECEF') if (i + j) % 2 else hexc('#D7DCE1'))
    r = random.Random(4)
    for row in range(4):
        y0 = row * 4.0
        cols = [r.choice(PROD) for _ in range(30)]
        def deco(i, x, y, z, w, d, h, cols=cols):
            b = (x, y, z, w, d, h)
            for lv in range(3):
                for k in range(10):
                    c = mix(cols[lv * 10 + k], C['rot'], rot * (.6 + .4 * ((k * 7 + lv) % 3) / 2))
                    i.frect(b, 'y', k / 10 + .01, lv / 3 + .06, (k + 1) / 10 - .01, lv / 3 + .26, c, edge=.1)
        iso.box(-2, y0, 0, 10, 1.2, 2.4, C['white'], deco=deco)
    iso.draw()
    if t > 31.0:
        a = prog(t, 31.0, 32.0)
        for k in range(26):
            px, py = iso.P(-2 + (k % 13) * .8, (k // 13) * 4 + 1.5, 1.5)
            ang = t * 7 + k * 1.7
            circle(cr, px + math.cos(ang) * 40, py + math.sin(ang * 1.3) * 25 - 60, 7, C['dark'], a)
        cr.set_line_width(9); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(7):
            x0 = 160 + k * 130; ph = (t * .8 + k * .37) % 1
            cr.set_source_rgba(*hexc('#8FBF3A'), a * (1 - ph) * .9)
            for s_ in range(14):
                yy = 1150 - ph * 500 - s_ * 18
                xx = x0 + math.sin(s_ * .7 + t * 4) * 18
                (cr.move_to if s_ == 0 else cr.line_to)(xx, yy)
            cr.stroke()

def nose_char(cr, t):
    sky(cr, hexc('#D9E8C4'), hexc('#B5CF8C'))
    front_char(cr, W / 2, 1950, 1450, 'disgust', arm='nose', t=t)
    cr.set_line_width(12); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(5):
        ph = (t * .9 + k * .2) % 1; x0 = 150 + k * 190
        cr.set_source_rgba(*hexc('#6F9E2A'), (1 - ph) * .8)
        for s_ in range(12):
            yy = 900 - ph * 500 - s_ * 22; xx = x0 + math.sin(s_ * .8 + t * 4) * 22
            (cr.move_to if s_ == 0 else cr.line_to)(xx, yy)
        cr.stroke()

def cans_aisle(cr, t):
    sky(cr, hexc('#EEF2F5'), hexc('#DCE3EA'))
    iso = Iso(cr, keys(t, [(37.3, 1.5), (41.9, 1.8)]), 2, 1.2, keys(t, [(37.3, 115), (41.9, 150)]), oy=.5)
    for i in range(-8, 12):
        for j in range(-8, 12):
            iso.quad(i * 2, j * 2, 2, 2, hexc('#E9ECEF') if (i + j) % 2 else hexc('#D7DCE1'))
    g = prog(t, 38.9, 39.6)
    for row in range(2):
        y0 = row * 3.5
        iso.box(-3, y0, 0, 9, 1.2, .15, C['white']); iso.box(-3, y0, 1.1, 9, 1.2, .1, C['white']); iso.box(-3, y0, 2.2, 9, 1.2, .1, C['white'])
        for lv in range(3):
            for k in range(14):
                can(iso, -2.7 + k * .62, y0 + .6, .15 + lv * 1.05, s=1.0, glow=g)
    iso.draw()

def s4(cr, t):
    if t < 35.4: market(cr, t)
    elif t < 37.3: nose_char(cr, t)
    else: cans_aisle(cr, t)

# ---------- S5 water cutaway (2D side view) ----------
def s5(cr, t):
    zoom = keys(t, [(41.85, 2.3), (44.4, 2.3), (45.2, 1.0), (51.5, 1.0), (52.3, 1.55), (55.5, 1.6)])
    fx = keys(t, [(41.85, 860), (44.4, 860), (45.2, W / 2), (51.5, W / 2), (52.3, 820), (55.5, 820)])
    fy = keys(t, [(41.85, 760), (44.4, 760), (45.2, 960), (51.5, 960), (52.3, 760), (55.5, 760)])
    raining = t > 51.6
    sky(cr, hexc('#7E93A8') if raining else C['sky'], hexc('#B9C6D2') if raining else C['sky2'])
    cr.save(); cr.translate(W / 2, 960); cr.scale(zoom, zoom); cr.translate(-fx, -fy)
    if not raining: clouds(cr, t, 3, y0=200, y1=500)
    # soil layers
    cr.rectangle(-500, 880, 2100, 40); fill(cr, C['grass'])
    for i, (y, c) in enumerate(((920, C['soil']), (1150, C['soil2']), (1400, C['soil3']))):
        cr.rectangle(-500, y, 2100, 900); fill(cr, c)
    # reservoir
    rrect(cr, 40, 780, 320, 160, 20); fill(cr, C['concrete']); cr.rectangle(60, 800, 280, 120); fill(cr, C['water'])
    # pipe path
    path = [(200, 940), (200, 1180), (520, 1180), (900, 1180), (900, 880)]
    cr.set_line_width(34); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.move_to(*path[0]); [cr.line_to(*p) for p in path[1:]]; cr.set_source_rgb(*C['metal']); cr.stroke()
    cr.set_line_width(16); cr.move_to(*path[0]); [cr.line_to(*p) for p in path[1:]]; cr.set_source_rgb(*shade(C['metal'], .6)); cr.stroke()
    flow = t < 47.8
    if t < 49:
        a = 1 if flow else clamp(1 - (t - 47.8) / .8)
        cr.set_line_width(12); cr.set_dash([28, 26], -(min(t, 47.8) * 160) % 54)
        cr.move_to(*path[0]); [cr.line_to(*p) for p in path[1:]]; cr.set_source_rgba(*C['water'], a); cr.stroke(); cr.set_dash([])
    # pump
    rrect(cr, 450, 1120, 140, 120, 14); fill(cr, hexc('#5A6472')); circle(cr, 520, 1180, 34, C['metal'])
    if t > 47.8:
        p = back((t - 47.8) / .3); cr.set_line_width(22 * p); cr.set_source_rgb(*C['red']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(470, 1140); cr.line_to(570, 1220); cr.move_to(570, 1140); cr.line_to(470, 1220); cr.stroke()
    # house
    hx = 700
    rrect(cr, hx, 640, 320, 245, 6); fill(cr, C['wall'])
    cr.move_to(hx - 30, 650); cr.line_to(hx + 160, 520); cr.line_to(hx + 350, 650); cr.close_path(); fill(cr, C['roof'])
    rrect(cr, hx + 30, 700, 90, 80, 6); fill(cr, C['win']); rrect(cr, hx + 200, 760, 70, 125, 6); fill(cr, C['brown'])
    # faucet on left wall
    cr.rectangle(hx - 70, 735, 70, 20); fill(cr, C['metal']); cr.rectangle(hx - 75, 735, 20, 45); fill(cr, C['metal'])
    cr.rectangle(hx - 60, 720, 30, 15); fill(cr, C['red'])
    if 43.9 < t < 45:
        p = prog(t, 44.05, 44.7); circle(cr, hx - 65, 790 + p * 70, 8, C['water'], 1 - prog(t, 44.6, 44.8))
    elif t < 43.9:
        circle(cr, hx - 65, 788, 5 + 3 * prog(t, 42.6, 43.9), C['water'])
    # bottles
    if t > 49.6:
        for k in range(6):
            bt = 49.8 + k * .18
            if t < bt: continue
            p = back((t - bt) / .3); bx = hx - 300 + (k % 3) * 46; by = 880 - (k // 3) * 88
            cr.save(); cr.translate(bx, by); cr.scale(p, p)
            rrect(cr, -18, -80, 36, 80, 10); fill(cr, C['water'], .7); cr.rectangle(-8, -96, 16, 18); fill(cr, C['panel'])
            cr.restore()
    if raining:
        rp = prog(t, 51.6, 52.4)
        cr.set_line_width(4); cr.set_source_rgba(*hexc('#DDEBFF'), .8 * rp)
        r = random.Random(2)
        for k in range(110):
            x = r.uniform(300, 1300); y = (r.uniform(0, 600) + t * 900) % 620 + 0
            if y > 640: continue
            cr.move_to(x, y); cr.line_to(x - 8, y + 34)
        cr.stroke()
        # gutter + tank
        cr.rectangle(hx + 330, 640, 14, 120); fill(cr, C['metal'])
        rrect(cr, hx + 300, 760, 120, 125, 10); fill(cr, hexc('#3F8FD6'))
        lvl = prog(t, 52, 55)
        cr.rectangle(hx + 310, 875 - lvl * 105, 100, lvl * 105); fill(cr, C['water'])
        if t > 53.8:
            p = back((t - 53.8) / .35); px, py = hx - 120, 860
            cr.save(); cr.translate(px, py); cr.scale(p, p)
            for k in range(5):
                fh = 30 + 18 * math.sin(t * 15 + k)
                cr.move_to(-50 + k * 25, 25); cr.line_to(-38 + k * 25, 25 - fh); cr.line_to(-26 + k * 25, 25); fill(cr, C['orange'])
            rrect(cr, -70, -60, 140, 70, 10); fill(cr, C['metal']); cr.rectangle(-60, -58, 120, 14); fill(cr, C['water'])
            for k in range(4):
                ph = (t * 1.5 + k * .25) % 1
                circle(cr, -40 + k * 27, -70 - ph * 90, 10 * (1 - ph) + 3, C['white'], .7 * (1 - ph))
            cr.restore()
    cr.restore()

# ---------- S6 night dogs / fort ----------
def packs(iso, t, seed=3):
    r = random.Random(seed)
    for p in range(7):
        along = 'x' if p % 2 == 0 else 'y'
        lane = r.choice((0, ROAD)) + r.uniform(-.8, .3)
        start = r.uniform(-24, -4); sp = r.uniform(3.5, 5)
        pos = start + (t - 55) * sp
        for d in range(4):
            off = d * 1.6 + r.uniform(-.3, .3); side = r.uniform(-.7, .7)
            if along == 'x': dog(iso, pos - off, lane + side, phase=t * 14 + d, along='x', eyes_glow=True, s=1.7)
            else: dog(iso, lane + side, pos - off, phase=t * 14 + d, along='y', eyes_glow=True, s=1.7)

def fort(iso, t, x0, y0, wall_h, gate=0.0, lock=0.0, lit=True, gate_open=0.0):
    house(iso, x0 + 2.2, y0 + 2.2, 4.4, 3.8, 2.4, lit=lit)
    if wall_h > 0:
        wc = hexc('#B8A58C')
        iso.box(x0, y0, 0, 10, .4, wall_h, wc)
        iso.box(x0, y0, 0, .4, 10, wall_h, wc)
        iso.box(x0 + 9.6, y0, 0, .4, 10, wall_h, wc)
        iso.box(x0, y0 + 9.6, 0, 3.6, .4, wall_h, wc)
        iso.box(x0 + 6.4, y0 + 9.6, 0, 3.6, .4, wall_h, wc)
        if gate > 0:
            gw = 2.8 * (1 - gate_open)
            iso.box(x0 + 3.6, y0 + 9.65, 0, gw, .3, wall_h * gate * .95, C['brown'],
                    deco=(lambda i, *b: i.frect(b, 'y', .45, .4, .55, .6, C['yellow'], edge=.2)) if lock > 0 else None)

def s6(cr, t):
    night_sky(cr)
    if t < 62.1:
        iso = Iso(cr, keys(t, [(55.5, 5), (62, 8)]), 7, 0, keys(t, [(55.5, 34), (62, 42)]), oy=.52)
        roads(iso); draw_ents(iso, CITY, lit=lambda x, y: (int(x * 5 + y * 3)) % 11 == 0, R=80)
        packs(iso, t); iso.draw(night=.72)
        return
    iso = Iso(cr, 5, 6, 0, keys(t, [(62.1, 70), (67.6, 88)]), oy=.55)
    iso.ground(C['grass']); iso.quad(-10, 11.5, 30, 3, C['road'], z=.01)
    wh = 1.8 * eout(prog(t, 63.6, 65.2))
    fort(iso, t, 0, 0, wh, gate=eout(prog(t, 65.8, 66.3)), lock=prog(t, 66.6, 66.7))
    person(iso, 4.0, 7.0)
    if t < 64.5:
        for d in range(3): dog(iso, keys(t, [(62.1, -6), (64.5, 2)]) - d * 1.8, 12.5 + d * .4, phase=t * 14 + d, eyes_glow=True)
    iso.draw(night=.6)
    if t > 66.6:
        p = back((t - 66.6) / .3); x, y = iso.P(5.0, 10, 1.8)
        cr.save(); cr.translate(x, y - 40); cr.scale(p, p)
        cr.set_line_width(12); cr.set_source_rgb(*C['yellow']); cr.arc(0, -30, 26, math.pi, 0); cr.stroke()
        rrect(cr, -36, -30, 72, 56, 10); fill(cr, C['yellow']); circle(cr, 0, 0, 8, C['dark']); cr.restore()

# ---------- S7 dog friend ----------
def heart(cr, x, y, s, c=None, a=1.0):
    c = c or C['red']
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(0, 30); cr.curve_to(-60, -10, -30, -55, 0, -25); cr.curve_to(30, -55, 60, -10, 0, 30)
    cr.close_path(); cr.set_source_rgba(*c, a); cr.fill(); cr.restore()

def s7(cr, t):
    sky(cr); clouds(cr, t, 4)
    S = keys(t, [(67.6, 60), (70.4, 85), (73.2, 110), (76.5, 125), (79.1, 130)])
    cx = keys(t, [(67.6, 3), (70.4, 4.6), (79.1, 4.8)]); cy = keys(t, [(67.6, 10), (70.4, 10.4), (79.1, 10.4)])
    iso = Iso(cr, cx, cy, .5, S, oy=.55)
    iso.ground(C['grass']); iso.quad(-15, 11.5, 40, 3, C['road'], z=.01)
    fort(iso, t, 0, 0, 1.8, gate=1, lock=0, lit=False, gate_open=eout(prog(t, 68.6, 69.4)))
    crouch = ease(prog(t, 72.8, 73.4))
    person(iso, 4.9, 9.6, crouch=crouch)
    dx = keys(t, [(67.6, -8), (70.2, 4.3)])
    walking = t < 70.2
    sit = 0.0
    dog(iso, dx, 11.2, phase=t * 14 if walking else 0, along='x', s=1.0, tail=math.sin(t * 20) * 3 if t > 75 else 0)
    if t > 73.3:
        can(iso, 5.6, 11.1, 0, s=1.1)
    iso.draw()
    hx, hy = iso.P(5.2, 11.4, 1.6)
    if t > 75.0:
        p = back((t - 75.0) / .35); heart(cr, hx, hy - 60 - 30 * math.sin(t * 3), p * 1.3)
    if t > 77.0:
        a = prog(t, 77.0, 77.3)
        cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(3):
            ph = (t * 1.6 + k / 3) % 1
            cr.set_source_rgba(*C['white'], a * (1 - ph)); cr.arc(hx + 30, hy + 10, 40 + ph * 160, -0.9, -0.1); cr.stroke()

# ---------- S8 ----------
def gas_station(cr, t):
    sky(cr, hexc('#B7C4CF'), hexc('#E2E6EA'))
    iso = Iso(cr, 4, 3.5, 1.5, keys(t, [(82.2, 78), (86.6, 90)]), oy=.52)
    iso.ground(hexc('#A9C98E')); iso.quad(-6, -6, 22, 20, hexc('#9BA3AC'), z=.005)
    for px in (0, 8):
        for py in (0, 6): iso.box(px, py, 0, .5, .5, 4, C['white'])
    for px in (2.5, 5.5):
        iso.box(px, 2.5, 0, 1, .8, 1.8, C['red'], deco=lambda i, *b: i.frect(b, 'x', .2, .55, .8, .85, C['dark']))
    iso.box(-.5, -.5, 4, 9.5, 7.5, .6, C['white'], deco=lambda i, *b: i.frect(b, 'x', 0, .1, 1, .9, C['red'], edge=0))
    car(iso, 2.6, 4.6, hexc('#6E8BA6'))
    iso.draw()
    if t > 84.4:
        x, y = iso.P(3.7, 5.1, 1.0); p = back((t - 84.4) / .3)
        cr.set_line_width(30 * p); cr.set_source_rgb(*C['red']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(x - 90, y - 90); cr.line_to(x + 90, y + 90); cr.move_to(x + 90, y - 90); cr.line_to(x - 90, y + 90); cr.stroke()

def solar_house(cr, t, t_drop=87.0, energy=89.1, S0=None):
    sky(cr); clouds(cr, t, 4)
    iso = Iso(cr, 3.5, 2.8, 1.5, S0 or keys(t, [(86.6, 80), (91.05, 95)]), oy=.55)
    iso.ground(C['grass'])
    def deco(i, *b):
        i.frect(b, 'x', .4, 0, .6, .6, C['brown']); i.frect(b, 'y', .2, .35, .45, .75, C['win']); i.frect(b, 'y', .6, .35, .85, .75, C['win'])
    iso.box(0, 0, 0, 6, 5, 2.8, C['wall'], deco=deco, top=hexc('#C9C2B4'))
    n = 0
    for gx in range(3):
        for gy in range(2):
            bt = t_drop + n * .3; n += 1
            if t < bt: continue
            p = prog(t, bt, bt + .35); z = 2.85 + (1 - p * p) * 8
            def pd(i, *b):
                for u in (.33, .66): i.frect(b, 't', u - .01, 0, u + .01, 1, hexc('#8FB2E8'), edge=0)
            iso.box(.4 + gx * 1.8, .4 + gy * 2.2, z, 1.6, 2.0, .12, C['panel'], deco=pd, top=C['panel'])
    def bd(i, *b): i.frect(b, 'x', .3, .7, .7, .85, C['green'])
    iso.box(6.6, 1.8, 0, .9, 1.4, 1.3, hexc('#E7EAEE'), deco=bd)
    iso.draw()
    if t > energy:
        a = prog(t, energy, energy + .3)
        p0 = iso.P(5.5, 3, 2.95); p1 = iso.P(7.0, 2.5, 1.3)
        cr.set_line_width(14); cr.set_source_rgba(*C['yellow'], a); cr.set_dash([30, 20], -t * 200)
        cr.move_to(*p0); cr.line_to(p0[0] + 60, p0[1] + 40); cr.line_to(*p1); cr.stroke(); cr.set_dash([])

def s8(cr, t):
    if t < 82.2: gen_yard(cr, t, land=0, lights=0, night=0, smoke=True, flicker=True)
    elif t < 86.6: gas_station(cr, t)
    else: solar_house(cr, t)

# ---------- S9 ----------
def pantry(cr, t):
    sky(cr, hexc('#F3E9DA'), hexc('#E3D5BF'))
    iso = Iso(cr, 2, 0, 1.4, keys(t, [(91.05, 140), (94.3, 155)]), oy=.5)
    iso.ground(hexc('#CDB89A'))
    iso.box(-1.5, -.6, 0, 7, 1.0, .1, C['brown']); iso.box(-1.5, -.6, 1.2, 7, 1.0, .1, C['brown']); iso.box(-1.5, -.6, 2.4, 7, 1.0, .1, C['brown'])
    total = 30; left = int(total * (1 - prog(t, 91.6, 94.2)))
    for idx in range(left):
        lv, k = divmod(idx, 10)
        can(iso, -1.2 + k * .6, -.1, .1 + lv * 1.2, s=.95)
    iso.draw()

def truck_x(cr, t):
    sky(cr, hexc('#B7C4CF'), hexc('#E2E6EA'))
    iso = Iso(cr, 3.5, .7, 1.2, 85, oy=.55)
    iso.ground(hexc('#A9C98E')); iso.quad(-20, -1.5, 50, 4, C['road'], z=.01)
    iso.box(0, -.5, .4, 5, 2.2, 2.6, C['white']); iso.box(5.1, -.4, .4, 1.8, 2.0, 1.8, C['red'],
        deco=lambda i, *b: i.frect(b, 'x', .1, .5, .9, .9, C['glass']))
    for wx in (.6, 3.6, 5.6): iso.box(wx, -.6, 0, .8, 2.4, .6, C['dark'])
    iso.draw()
    x, y = iso.P(3.5, .6, 1.6); p = back((t - 94.5) / .3)
    cr.set_line_width(34 * p); cr.set_source_rgb(*C['red']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(x - 150, y - 150); cr.line_to(x + 150, y + 150); cr.move_to(x + 150, y - 150); cr.line_to(x - 150, y + 150); cr.stroke()

def garden_store(cr, t):
    sky(cr); clouds(cr, t, 3)
    iso = Iso(cr, 5, 3.5, 1.2, keys(t, [(96.8, 78), (99.2, 92)]), oy=.55)
    iso.ground(C['grass']); iso.quad(-10, 8, 30, 3, C['road'], z=.01)
    def deco(i, *b): i.frect(b, 'x', .1, .05, .9, .75, C['glass']); i.frect(b, 'y', .1, .05, .9, .75, C['glass'])
    iso.box(0, 0, 0, 7, 5, 3, hexc('#E6F2DD'), deco=deco)
    iso.box(0, 0, 3, 7, 5, .7, C['green'])
    r = random.Random(7)
    iso.box(7.6, 1, 0, 1.4, 3, 1.0, C['brown'])
    for k in range(10):
        iso.box(7.7 + (k % 2) * .65, 1.1 + (k // 2) * .55, 1.0, .5, .45, .55, r.choice(PROD))
    person(iso, 9.6, 6.0, phase=t * 9 if t < 98 else None)
    iso.draw()

def farm_plots(iso, t, g0, crops=True):
    for row in range(3):
        for k in range(5):
            iso.quad(-1 + k * 1.6, row * 2.4, 1.1, 1.8, C['soil2'], z=.01)
    if not crops: return
    specs = [('feijao', g0), ('milho', g0 + .7), ('mandioca', g0 + 1.4)]
    for row, (kind, st) in enumerate(specs):
        g = eout(prog(t, st, st + 1.5))
        if g <= 0: continue
        for k in range(5):
            x, y = -1 + k * 1.6 + .25, row * 2.4 + .3
            if kind == 'feijao':
                iso.box(x, y, 0, .6, 1.2, .5 * g, C['leaf'])
            elif kind == 'milho':
                iso.box(x + .15, y + .3, 0, .3, .3, 1.8 * g, C['leaf2']); iso.box(x + .1, y + .25, 1.2 * g, .4, .4, .5 * g, C['yellow'])
            else:
                iso.box(x, y, 0, .7, 1.2, .9 * g, hexc('#5DBB55'))

def backyard(cr, t):
    sky(cr); clouds(cr, t, 4)
    iso = Iso(cr, 4, 3.5, .3, keys(t, [(99.2, 88), (105.7, 102)]), oy=.55)
    iso.ground(C['grass'])
    farm_plots(iso, t, 101.4)
    person(iso, 7.5, 7.5, crouch=.6 if 100 < t < 101.5 else 0)
    iso.draw()

def s9(cr, t):
    if t < 94.3: pantry(cr, t)
    elif t < 96.75: truck_x(cr, t)
    elif t < 99.2: garden_store(cr, t)
    else: backyard(cr, t)

# ---------- S10 ----------
def s10(cr, t):
    g = ease(prog(t, 106.6, 114.8))
    if t < 114.9:
        sky(cr); clouds(cr, t, 4)
        iso = Iso(cr, keys(t, [(105.7, 6), (114.9, 9)]), 6, 0, keys(t, [(105.7, 22), (114.9, 30)]), oy=.52)
        roads(iso, green=g); draw_ents(iso, CITY, green=g, R=80)
        iso.draw()
        # cracks
        r = random.Random(11); cr.set_line_width(5); cr.set_source_rgba(*C['dark'], .6 * g)
        for _ in range(40):
            k = r.randint(-3, 3) * ROAD; p = r.uniform(-40, 40)
            pts = [(k + r.uniform(-1, 1), p), (k + r.uniform(-1, 1), p + 1), (k + r.uniform(-1, 1), p + 2)] if r.random() < .5 else \
                  [(p, k + r.uniform(-1, 1)), (p + 1, k + r.uniform(-1, 1)), (p + 2, k + r.uniform(-1, 1))]
            q = [iso.P(x, y, .02) for x, y in pts]
            cr.move_to(*q[0]); [cr.line_to(*qq) for qq in q[1:]]; cr.stroke()
        return
    sky(cr); clouds(cr, t, 4)
    px = keys(t, [(114.9, 0), (118.05, 7)])
    iso = Iso(cr, px + 1.0, .3, .6, keys(t, [(114.9, 95), (118.05, 75)]), oy=.55)
    roads(iso, green=1); draw_ents(iso, CITY, green=1, R=45)
    person(iso, px, -.6, phase=t * 9, bag=True)
    dog(iso, px - 2.2, .4, phase=t * 14)
    iso.draw()

# ---------- S11 farm ----------
def farm(iso, t, celebrate=False):
    iso.ground(hexc('#86D663'))
    iso.quad(-30, 12, 70, 3, hexc('#C9A877'), z=.01)
    house(iso, 0, 0, 5, 4.5, 2.6, wall=hexc('#F6E3C3'), roof=hexc('#C9503A'))
    def pd(i, *b): i.frect(b, 't', .48, 0, .52, 1, hexc('#8FB2E8'), edge=0)
    for k in range(3): iso.box(6.2 + k * 1.3, -1.5, 0, 1.1, 1.6, .12, C['panel'], deco=pd)
    # well
    iso.box(-4, 6, 0, 1.6, 1.6, .9, C['concrete']); iso.quad(-3.8, 6.2, 1.2, 1.2, C['water'], z=.92)
    iso.box(-4, 6, .9, .15, .15, 1.4, C['brown']); iso.box(-2.55, 7.45, .9, .15, .15, 1.4, C['brown'])
    iso.box(-4.2, 5.8, 2.3, 2.0, 2.0, .2, C['roof'])
    # garden
    def fp(): pass
    for row in range(3):
        for k in range(4):
            iso.quad(6 + k * 1.5, 4 + row * 2.2, 1.0, 1.6, C['soil2'], z=.01)
            iso.box(6.15 + k * 1.5, 4.3 + row * 2.2, 0, .7, 1.0, .5 + .3 * (row % 2), C['leaf'] if row != 1 else C['leaf2'])
    # coop
    house(iso, -5, -1, 2.4, 2.2, 1.2, wall=hexc('#E9C27A'), roof=hexc('#B04A35'), door=False)
    for k in range(4):
        jz = abs(math.sin(t * 8 + k)) * .4 if celebrate else 0
        cx, cy = -5.5 + k * .9, 2.2 + (k % 2) * .6
        iso.box(cx, cy, jz, .4, .5, .35, C['white']); iso.box(cx + .25, cy + .1, jz + .3, .2, .3, .2, C['white'])
        iso.box(cx + .35, cy + .18, jz + .38, .12, .14, .08, C['red'])
    for k, (tx, ty) in enumerate(((-8, -4), (12, -3), (-9, 10), (14, 9), (3, -6))): tree(iso, tx, ty, 1.1)

def icon(cr, kind, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if kind == 'torneira':
        rrect(cr, -70, -30, 110, 34, 10); fill(cr, C['metal']); rrect(cr, 15, -30, 30, 80, 10); fill(cr, C['metal'])
        rrect(cr, -30, -60, 40, 30, 8); fill(cr, C['red']); circle(cr, 30, 70, 9, C['water'])
    elif kind == 'poco':
        rrect(cr, -60, -10, 120, 70, 10); fill(cr, C['concrete']); cr.rectangle(-48, -10, 96, 12); fill(cr, C['water'])
        cr.rectangle(-55, -80, 10, 70); cr.rectangle(45, -80, 10, 70); fill(cr, C['brown'])
        cr.move_to(-75, -75); cr.line_to(0, -115); cr.line_to(75, -75); cr.close_path(); fill(cr, C['roof'])
    elif kind == 'usina':
        rrect(cr, -70, -20, 140, 80, 6); fill(cr, hexc('#9AA3AE')); cr.rectangle(-50, -100, 26, 80); cr.rectangle(10, -80, 26, 60); fill(cr, hexc('#7C8590'))
        circle(cr, -37, -115, 18, C['smoke']); circle(cr, -20, -132, 14, C['smoke'])
    elif kind == 'sol':
        cr.set_line_width(12); cr.set_source_rgb(*C['sun']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(8):
            a = k * math.pi / 4; cr.move_to(math.cos(a) * 62, math.sin(a) * 62); cr.line_to(math.cos(a) * 90, math.sin(a) * 90)
        cr.stroke(); circle(cr, 0, 0, 48, C['sun'])
    elif kind == 'mercado':
        rrect(cr, -70, -40, 140, 100, 6); fill(cr, C['white']); cr.rectangle(-75, -70, 150, 34); fill(cr, C['red'])
        for k in range(4): cr.rectangle(-75 + k * 37.5, -70, 18, 34)
        fill(cr, C['white']); rrect(cr, -20, 0, 40, 60, 4); fill(cr, C['glass'])
    elif kind == 'horta':
        rrect(cr, -80, 10, 160, 45, 8); fill(cr, C['soil2'])
        for k in range(4):
            cx = -58 + k * 39; circle(cr, cx, 0, 20, C['leaf']); circle(cr, cx - 10, -12, 14, C['leaf2'])
    elif kind == 'cidade':
        for k, (bx, bh) in enumerate(((-75, 90), (-35, 140), (10, 110), (50, 70))):
            cr.rectangle(bx, 60 - bh, 36, bh); fill(cr, hexc('#8FA3B8') if k % 2 else hexc('#6E829A'))
    elif kind == 'cachorro':
        rrect(cr, -55, -50, 110, 100, 30); fill(cr, C['dog'])
        rrect(cr, -70, -55, 30, 60, 12); rrect(cr, 40, -55, 30, 60, 12); fill(cr, C['dog2'])
        circle(cr, -20, -10, 9, C['dark']); circle(cr, 20, -10, 9, C['dark']); circle(cr, 0, 15, 12, C['dark'])
    cr.restore()

SWAPS = [('torneira', 'poco', 'POÇO'), ('usina', 'sol', 'SOL'), ('mercado', 'horta', 'HORTA'), ('cidade', 'cachorro', 'CACHORRO')]
def s11(cr, t):
    sky(cr); clouds(cr, t, 4)
    S = keys(t, [(118.05, 22), (120.6, 52), (128, 58)])
    iso = Iso(cr, keys(t, [(118.05, 2), (120.6, 2.5)]), keys(t, [(118.05, 8), (120.6, 4.5)]), 0, S, oy=.66)
    farm(iso, t)
    person(iso, 2.5, 7.0); dog(iso, 4.0, 8.0, tail=math.sin(t * 20) * 3)
    iso.draw()
    times = [wt('Poço'), wt('sol', 121), wt('horta'), wt('cachorro', 125)]
    for i, (a, b, lbl) in enumerate(SWAPS):
        t0 = times[i]; t1 = times[i + 1] if i + 1 < 4 else 128.0
        if not (t0 <= t < t1): continue
        p = back((t - t0) / .3); cy = 640
        cr.save(); cr.translate(W / 2, cy); cr.scale(p, p)
        rrect(cr, -440 + 8, -170 + 12, 880, 340, 50); fill(cr, (0, 0, 0), .2)
        rrect(cr, -440, -170, 880, 340, 50); fill(cr, C['white'])
        sw = prog(t, t0 + .25, t0 + .6)
        icon(cr, a, -250, 0, 1.25);
        cr.set_line_width(22); cr.set_source_rgb(*C['dark']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(-70, 0); cr.line_to(-70 + 140 * sw, 0); cr.stroke()
        if sw > .9:
            cr.move_to(40, -35); cr.line_to(75, 0); cr.line_to(40, 35); cr.stroke()
        icon(cr, b, 250, 0, 1.25 * back(prog(t, t0 + .45, t0 + .8)))
        if a in ('torneira', 'usina', 'mercado', 'cidade'):
            cr.set_line_width(12); cr.set_source_rgba(*C['red'], .85)
            cr.move_to(-330, -80); cr.line_to(-170, 80); cr.stroke()
        cr.restore()

# ---------- S12 quick cuts ----------
def obj_shot(cr, t, kind, bg):
    sky(cr, shade(bg, 1.15), bg)
    iso = Iso(cr, -1.3, .1, 1.1, 165, oy=.5) if kind == 'ferramentas' else Iso(cr, 0, 0, .8, 135, oy=.5)
    iso.ground(shade(bg, .9))
    if kind == 'galinheiro':
        house(iso, -1.6, -1.4, 3, 2.6, 1.5, wall=hexc('#E9C27A'), roof=hexc('#B04A35'), door=False)
        for k in range(3):
            cx, cy = -1.3 + k * 1.0, 1.7; jz = abs(math.sin(t * 9 + k)) * .2
            iso.box(cx, cy, jz, .45, .55, .4, C['white']); iso.box(cx + .28, cy + .1, jz + .33, .22, .32, .22, C['white'])
            iso.box(cx + .38, cy + .2, jz + .42, .12, .14, .08, C['red'])
    elif kind == 'lenha':
        for lv in range(3):
            for k in range(4 - lv):
                iso.box(-1.5 + k * .8 + lv * .4, -1, lv * .55, .7, 2.4, .55, C['brown'], top=hexc('#E3B77E'))
    elif kind == 'ferramentas':
        def tools(i, *bb):
            f = lambda *a: i.frect(bb, 'x', *a, edge=.15)
            f(.08, .25, .14, .85, C['brown']); f(.02, .75, .22, .88, C['metal'])            # martelo
            f(.32, .15, .38, .7, C['brown']); f(.27, .05, .43, .25, C['metal'])             # pa
            f(.52, .35, .72, .6, C['metal']); f(.72, .4, .8, .56, C['red'])                 # serrote
            f(.86, .3, .92, .82, C['metal']); f(.83, .78, .95, .9, C['metal'])             # chave
        iso.box(-2, -1.3, 0, .3, 2.8, 2.4, hexc('#A87A4F'), deco=tools)
        iso.box(-1.7, -1.3, 0, 1.0, 2.8, .45, hexc('#C79A68'))
    elif kind == 'livros':
        for k, c in enumerate((C['red'], C['panel'], C['green'], C['orange'], C['purple'])):
            iso.box(-1 + (k % 2) * .1, -.8, k * .3, 2.0, 1.5, .28, c, top=hexc('#F4EFE3'))
    elif kind == 'radio':
        def rd(i, *b):
            i.frect(b, 'x', .08, .2, .5, .85, C['dark']); i.frect(b, 'x', .6, .55, .9, .8, hexc('#FFE08A'))
            i.frect(b, 'x', .62, .2, .72, .4, C['metal']); i.frect(b, 'x', .78, .2, .88, .4, C['metal'])
        iso.box(-1.0, -1.6, 0, 1.6, 3.0, 1.6, hexc('#C0503A'), deco=rd)
        iso.box(-.4, 0, 1.6, .08, .08, 1.8, C['metal'])
    iso.draw()
    if kind == 'radio':
        x, y = iso.P(-.36, .04, 3.4); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(3):
            ph = (t * 1.3 + k / 3) % 1; cr.set_source_rgba(*C['white'], 1 - ph)
            cr.arc(x, y, 30 + ph * 170, -2.4, -.7); cr.stroke()

def s12(cr, t):
    cuts = [(wt('Galinheiro'), 'galinheiro', hexc('#BFE3A8')), (wt('Lenha'), 'lenha', hexc('#F1D3A8')),
            (wt('Ferramentas'), 'ferramentas', hexc('#C9D8EE')), (wt('Livros'), 'livros', hexc('#F2C9D6')),
            (wt('Rádio'), 'radio', hexc('#FFE3A3'))]
    cur = cuts[0]
    for c in cuts:
        if t >= c[0] - .05: cur = c
    obj_shot(cr, t, cur[1], cur[2])

# ---------- S13 ----------
def confetti(cr, t, t0):
    r = random.Random(12); el = t - t0
    for k in range(160):
        x = r.uniform(0, W); v = r.uniform(250, 520); y = -50 - r.uniform(0, 900) + el * v
        if y > H: continue
        ang = el * r.uniform(3, 8) + k
        cr.save(); cr.translate(x + math.sin(el * 3 + k) * 30, y); cr.rotate(ang)
        cr.rectangle(-11, -6, 22, 12); fill(cr, r.choice(PROD + [C['panel'], C['green']])); cr.restore()

def s13(cr, t):
    sky(cr); clouds(cr, t, 4)
    iso = Iso(cr, 2.5, 5.5, 0, 62, oy=.6)
    farm(iso, t, celebrate=True)
    jz = abs(math.sin(t * 7)) * .6
    person(iso, 2.5, 7.0, z=jz, arms_up=1.0)
    iso.draw()
    dz = abs(math.sin(t * 7 + 1.2)) * .5   # dog drawn on top, jumping
    iso3 = Iso(cr, 2.5, 5.5, -dz, 62, oy=.6)
    dog(iso3, 4.0, 8.0, tail=math.sin(t * 25) * 3)
    iso3.draw()
    confetti(cr, t, 134.1)

# ---------- S14 ----------
def s14(cr, t):
    if t < 142.2:
        sky(cr, hexc('#10152E'), hexc('#1D2547'))
        S = keys(t, [(137.9, 80), (142.2, 130)])
        iso = Iso(cr, 0, 0, .9, S, oy=.52)
        iso.ground(hexc('#5B4636'))
        iso.box(-2.5, -2.5, 0, 5, 5, .2, hexc('#7B5A3E'), key=-100)
        shake = math.sin(t * 50) * .03 if t > 140.9 else 0
        def rd(i, *b):
            i.frect(b, 'x', .08, .2, .5, .85, C['dark'])
            on = t > 140.9 and math.sin(t * 18) > 0
            i.frect(b, 'x', .6, .55, .9, .8, hexc('#FFE08A') if on else hexc('#7A6A40'), glow=on)
            i.frect(b, 'x', .62, .2, .72, .4, C['metal']); i.frect(b, 'x', .78, .2, .88, .4, C['metal'])
        iso.box(-1.0 + shake, -1.6, .2, 1.6, 3.0, 1.6, hexc('#C0503A'), deco=rd)
        iso.box(-.4 + shake, 0, 1.8, .08, .08, 1.8, C['metal'])
        iso.draw(night=.55)
        g = cairo.RadialGradient(W / 2, 900, 50, W / 2, 900, 800)
        g.add_color_stop_rgba(0, 1, .85, .5, .18); g.add_color_stop_rgba(1, 0, 0, 0, 0); cr.set_source(g); cr.paint()
        if t > 140.9:
            x, y = iso.P(-.36, .04, 3.6)
            cr.set_line_width(7); cr.set_line_join(cairo.LINE_JOIN_ROUND)
            r = random.Random(int(t * 15))
            for k in range(4):
                a0 = -2.6 + k * .5; cr.set_source_rgba(*C['white'], .9)
                cr.move_to(x, y)
                for s_ in range(1, 7):
                    rr = s_ * 40; a = a0 + r.uniform(-.25, .25)
                    cr.line_to(x + math.cos(a) * rr, y + math.sin(a) * rr)
                cr.stroke()
        return
    if t < 143.6:
        sky(cr, hexc('#0B0F22'), hexc('#1A1F3D'))
        g = cairo.RadialGradient(W / 2, 1500, 50, W / 2, 1500, 900)
        g.add_color_stop_rgba(0, 1, .8, .45, .45); g.add_color_stop_rgba(1, 0, 0, 0, 0); cr.set_source(g); cr.paint()
        e = eout(prog(t, 142.2, 143.4))
        front_char(cr, W / 2, 2300 - e * 80, 1650 + e * 150, 'shock', t=t)
        return
    sky(cr, hexc('#0B0F22'), hexc('#1A1F3D')); stars(cr, a=.6)

# ======================= TIMELINE =======================
SCENES = [(0, 5.2, s1), (5.2, 16.15, s2), (16.15, 28.65, s3), (28.65, 41.85, s4), (41.85, 55.5, s5),
          (55.5, 67.6, s6), (67.6, 79.1, s7), (79.1, 91.05, s8), (91.05, 105.7, s9), (105.7, 118.05, s10),
          (118.05, 128.0, s11), (128.0, 134.1, s12), (134.1, 137.9, s13), (137.9, 147.5, s14)]
END = 147.5

def fmt_count(t):
    v = 8e9 * (1 - eout(prog(t, 0.4, 4.4))) ** 3
    n = max(1, int(v))
    return f"{n:,}".replace(',', '.')

def overlays(cr, t):
    G, R, Y = C['green'], C['red'], C['yellow']
    if t < 5.2:
        n = fmt_count(t); counter(cr, t, 0.3, 5.2, n, 'PESSOA' if n == '1' else 'PESSOAS')
    counter(cr, t, 5.25, 7.6, 'DIA 1')
    for a in ('Mansão', 'Carro', 'Shopping'):
        t0 = wt(a, 5); pill(cr, t, t0 + .2, t0 + 1.8, 'DE GRAÇA', W / 2, 560, G)
    pill(cr, t, 16.4, 21.0, 'SEM OPERADORES', W / 2, 520, R)
    counter(cr, t, 18.3, 21.0, 'DIA 2')
    pill(cr, t, 21.0, 22.3, 'APAGÃO', W / 2, 520, R)
    for i, a in enumerate(('Geladeira', 'internet', 'elevador')):
        t0 = wt(a, 20); pill(cr, t, t0, 26.2, a.upper(), 300, 300 + i * 115, R)
    title(cr, t, wt('gerador', 26), 28.65, 'GERADOR')
    counter(cr, t, 28.8, 35.4, 'DIA 7')
    pill(cr, t, wt('apodrece'), 35.4, 'APODRECE', W / 2, 520, R)
    pill(cr, t, wt('enlatados') + .2, 41.85, 'DURA ANOS', W / 2, 560, G)
    title(cr, t, wt('enlatados'), 41.85, 'ENLATADOS', y=380)
    pill(cr, t, wt('bombas'), 49.7, 'BOMBAS PARADAS', W / 2, 330, R)
    pill(cr, t, wt('garrafa'), 51.6, 'ÁGUA DE GARRAFA', W / 2, 330, G)
    title(cr, t, wt('chuva', 50), 55.5, 'CAPTAÇÃO DE CHUVA', y=300, size=100)
    pill(cr, t, wt('matilhas'), 62.1, 'MATILHAS', W / 2, 360, R)
    title(cr, t, wt('forte'), 67.6, 'FORTE', y=330)
    for i, a in enumerate(('muro', 'portão', 'tudo')):
        t0 = wt(a, 64); pill(cr, t, t0, 67.6, ('MURO', 'PORTÃO', 'TRANCADO')[i], W / 2, 520 + i * 110, G)
    pill(cr, t, wt('parceiro'), 79.1, 'PARCEIRO', W / 2, 420, G)
    counter(cr, t, 79.3, 82.2, 'MÊS 6')
    pill(cr, t, wt('Gasolina'), 86.6, 'GASOLINA ESTRAGA', W / 2, 420, R)
    title(cr, t, wt('painéis'), 91.05, 'ENERGIA SOLAR', y=330)
    counter(cr, t, 91.2, 94.3, 'ANO 2')
    pill(cr, t, 94.4, 96.75, 'SEM ENTREGAS', W / 2, 420, R)
    pill(cr, t, wt('sementes'), 101.6, 'SEMENTES', W / 2, 420, G)
    for i, a in enumerate(('Feijão', 'milho', 'mandioca')):
        t0 = wt(a, 100); pill(cr, t, t0, 104.0, a.upper(), W / 2, 330 + i * 110, G)
    title(cr, t, wt('agricultor'), 105.7, 'AGRICULTOR', y=330)
    pill(cr, t, wt('engolida'), 114.9, 'NATUREZA VOLTANDO', W / 2, 400, G)
    pill(cr, t, wt('embora'), 118.05, 'VAI EMBORA', W / 2, 400, Y)
    pill(cr, t, wt('fazenda'), 120.85, 'FAZENDA', W / 2, 420, G)
    title(cr, t, 127.1, 128.0, 'AUTOSSUFICIENTE', y=300, size=100)
    for a in ('Galinheiro', 'Lenha', 'Ferramentas', 'Livros', 'Rádio'):
        t0 = wt(a, 127); nxt = {'Galinheiro': wt('Lenha'), 'Lenha': wt('Ferramentas'), 'Ferramentas': wt('Livros'), 'Livros': wt('Rádio'), 'Rádio': 134.1}[a]
        pill(cr, t, t0, nxt, ('RÁDIO LIGADO' if a == 'Rádio' else a.upper()), W / 2, 420, G)
    title(cr, t, 134.25, 137.9, 'PARABÉNS!', y=360, size=150, sub='Você sobreviveu ao fim da humanidade')
    counter(cr, t, 138.0, 140.8, 'ANO 3')
    if t >= 143.6:
        p = t - 143.6
        title(cr, t, 143.6, 999, 'COMENTE', y=720, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 143.85), 143.85, 999, '"RÁDIO"', y=900, size=170, tilt=-.07)
        if t > 144.2:
            text_center(cr, 'se você responderia', W / 2, 1080, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - 144.2) / .3))
        pill(cr, t, 144.6, 999, 'PARTE 2?', W / 2, 1260, Y, size=60)
    if t < 143.6: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    overlays(cr, t)
