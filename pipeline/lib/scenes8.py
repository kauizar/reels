import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
import scenes as v1
from scenes import confetti, PROD
sys.path.append('/home/claude/vid3'); sys.path.append('/home/claude/vid4')
import scenes3 as v3
from scenes3 import arrow, thermo

SPEED = 1.045          # narration was sped up; scenes are timed in original narration seconds
WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes8.json')))
def merge(first, last, disp, after=0.0):
    i = next(k for k, w in enumerate(WORDS) if w['t0'] >= after and w['w'].strip('.,') == first)
    j = next(k for k in range(i + (1 if first == last else 0), len(WORDS)) if WORDS[k]['w'].strip('.,') == last)
    WORDS[i] = dict(WORDS[i], w=disp, key=True, t1=WORDS[j]['t1']); del WORDS[i + 1:j + 1]
merge('one', 'twenty', '120 °C'); merge('minus', 'fifty', '−150 °C', after=28)

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

GREY, GREY2, GREY3 = hexc('#9A9A98'), hexc('#7E7E7C'), hexc('#B4B4B0')
GOLD = hexc('#E0A92E')

# ---------- moon helpers ----------
def moon_ground(iso, seed=1, ext=60, n=40):
    iso.ground(GREY)
    r = random.Random(seed)
    craters = [(r.uniform(-ext / 2, ext / 2), r.uniform(-ext / 2, ext / 2), r.uniform(.8, 4.5)) for _ in range(n)]
    def draw(i):
        cr = i.cr
        for x, y, rad in craters:
            if abs(x - i.cx) + abs(y - i.cy) > 40: continue
            px, py = i.P(x, y, 0); rx = rad * i.S * .87; ry = rad * i.S * .5
            cr.save(); cr.translate(px, py); cr.scale(1, ry / rx)
            g = cairo.RadialGradient(-rx * .2, -rx * .25, rx * .1, 0, 0, rx); g.add_color_stop_rgb(0, *GREY2); g.add_color_stop_rgb(.8, *hexc('#8A8A88')); g.add_color_stop_rgb(1, *GREY3)
            cr.set_source(g); cr.arc(0, 0, rx, 0, 7); cr.fill()
            cr.set_line_width(rx * .08); cr.set_source_rgba(.85, .85, .82, .8); cr.arc(0, 0, rx * 1.02, .2, math.pi - .2); cr.stroke()
            cr.set_source_rgba(.25, .25, .25, .35); cr.arc(0, 0, rx * 1.0, math.pi + .2, 2 * math.pi - .2); cr.stroke()
            cr.restore()
    iso.custom(-1000, draw)
    for _ in range(14):
        x, y = r.uniform(-ext / 3, ext / 3), r.uniform(-ext / 3, ext / 3); s = r.uniform(.3, 1.2)
        iso.box(x, y, 0, s * 1.3, s, s * .7, GREY3)

def astronaut(iso, x, y, z=0.0, phase=None, crouch=0.0, arms_up=0.0, s=1.0):
    W_, G_ = hexc('#F2F2F0'), hexc('#C9CCD2')
    sw = math.sin(phase) * .2 if phase is not None else 0; k = x + y
    lz = .8 * (1 - .45 * crouch) * s
    iso.box(x - .05 * s, y + .02 * s + sw * s, z, .26 * s, .26 * s, lz, W_, key=k + .001)
    iso.box(x - .05 * s, y + .32 * s - sw * s, z, .26 * s, .26 * s, lz, W_, key=k + .002)
    bz = z + lz
    iso.box(x - .4 * s, y + .02 * s, bz + .05 * s, .3 * s, .56 * s, .62 * s, G_, key=k - .1)
    iso.box(x - .12 * s, y - .04 * s, bz, .4 * s, .66 * s, .66 * s, W_, key=k + .003,
            deco=lambda i, *b: (i.frect(b, 'x', .3, .4, .7, .7, C['red'], edge=.1), i.frect(b, 'x', .3, .2, .7, .32, hexc('#3B82D6'), edge=.1)))
    for yy in (-.2, .62):
        if arms_up > 0: iso.box(x - .02 * s, y + yy * s, bz + .5 * s, .18 * s, .18 * s, .55 * s * arms_up + .1 * s, W_, key=k + .004)
        else: iso.box(x - .02 * s, y + yy * s, bz + .05 * s - sw * .2 * s, .18 * s, .18 * s, .58 * s, W_, key=k + .004)
    hz = bz + .66 * s
    iso.box(x - .14 * s, y - .06 * s, hz, .5 * s, .7 * s, .55 * s, W_, key=k + .005,
            deco=lambda i, *b: i.frect(b, 'x', .12, .2, .88, .8, GOLD, edge=.1))

def lander(iso, x, y, door=0.0):
    foil = hexc('#D9A43A')
    for dx, dy in ((-.6, -.6), (3.4, -.6), (-.6, 3.4), (3.4, 3.4)):
        iso.box(x + dx, y + dy, 0, .2, .2, 1.6, C['metal'])
        iso.box(x + dx - .3, y + dy - .3, 0, .8, .8, .08, C['metal'])
    iso.box(x, y, 1.0, 3.2, 3.2, 1.6, foil, deco=lambda i, *b: [i.frect(b, f, u, .1, u + .08, .9, shade(foil, .8), edge=0) for f in ('x', 'y') for u in (.2, .5, .8)])
    def cab(i, *b):
        i.frect(b, 'x', .3, .1, .7, .8 * (1 - door) + .1, hexc('#3A3F48'))
        i.frect(b, 'y', .2, .55, .45, .8, hexc('#1E2229')); i.frect(b, 'y', .55, .55, .8, .8, hexc('#1E2229'))
    iso.box(x + .3, y + .3, 2.6, 2.6, 2.6, 1.8, hexc('#C9CED6'), deco=cab)

def earth_in_sky(cr, x=860, y=360, R=110):
    draw_globe(cr, x, y, R, lon0=200, tilt=.3, sun=(-.8, -.2, .5), clouds=.7)

EARTH = [False]
def moon_sky(cr, t, earth=True):
    space(cr, t)
    EARTH[0] = earth

def moon_disk(cr, cx, cy, R, rot=0.0):
    g = cairo.RadialGradient(cx - R * .3, cy - R * .3, R * .1, cx, cy, R)
    g.add_color_stop_rgb(0, *hexc('#E2E2DE')); g.add_color_stop_rgb(.7, *hexc('#A8A8A4')); g.add_color_stop_rgb(1, *hexc('#5E5E5C'))
    cr.set_source(g); cr.arc(cx, cy, R, 0, 7); cr.fill()
    r = random.Random(5)
    cr.save(); cr.arc(cx, cy, R, 0, 7); cr.clip()
    for k in range(60):
        a = r.uniform(0, 6.28) + rot; d = r.uniform(0, .95) * R; rr = r.uniform(.02, .12) * R
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        circle(cr, x, y, rr, hexc('#8E8E8A'), .7); cr.set_line_width(rr * .15); cr.set_source_rgba(1, 1, 1, .3); cr.arc(x, y, rr, 3.6, 5.6); cr.stroke()
    for k in range(5):
        a = r.uniform(0, 6.28) + rot; d = r.uniform(.2, .7) * R
        circle(cr, cx + math.cos(a) * d, cy + math.sin(a) * d, r.uniform(.12, .25) * R, hexc('#7A7A78'), .45)
    cr.restore()

def visor(cr, t, o2, scratches=0.0):
    space(cr, t)
    cx, cy, R = W / 2, 900, 470
    g = cairo.RadialGradient(cx, cy, R * .9, cx, cy, R * 1.25); g.add_color_stop_rgb(0, *hexc('#F2F2F0')); g.add_color_stop_rgb(1, *hexc('#9A9C A0'.replace(' ', '')))
    cr.set_source(g); cr.arc(cx, cy, R * 1.25, 0, 7); cr.fill()
    g = cairo.LinearGradient(cx - R, cy - R, cx + R, cy + R); g.add_color_stop_rgb(0, *hexc('#E6B44A')); g.add_color_stop_rgb(.5, *hexc('#8A5A14')); g.add_color_stop_rgb(1, *hexc('#3A2A0A'))
    cr.set_source(g); cr.arc(cx, cy, R, 0, 7); cr.fill()
    cr.save(); cr.arc(cx, cy, R, 0, 7); cr.clip()
    cr.rectangle(cx - R, cy + 80, 2 * R, R); fill(cr, hexc('#C9A66A'), .5)
    g = cairo.LinearGradient(cx - R, cy - R, cx, cy); g.add_color_stop_rgba(0, 1, 1, 1, .5); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(g); cr.arc(cx - R * .3, cy - R * .4, R * .6, 0, 7); cr.fill()
    if scratches > 0:
        r = random.Random(4); n = int(30 * scratches)
        cr.set_line_width(3); cr.set_source_rgba(1, 1, 1, .7)
        for k in range(n):
            x, y = cx + r.uniform(-R, R) * .8, cy + r.uniform(-R, R) * .8; a = r.uniform(0, 3.14); L = r.uniform(40, 200)
            cr.move_to(x, y); cr.line_to(x + math.cos(a) * L, y + math.sin(a) * L); cr.stroke()
    cr.restore()
    if o2 is not None:
        rrect(cr, cx - 300, cy + 220, 600, 50, 25); fill(cr, (0, 0, 0), .5)
        col = C['green'] if o2 > .5 else (C['yellow'] if o2 > .25 else C['red'])
        rrect(cr, cx - 294, cy + 226, 588 * o2, 38, 19); fill(cr, col)
        text_center(cr, f"O2  {o2 * 6:.1f} H", cx, cy + 160, 64, C['white'], stroke=C['dark'], sw=8)

def lava_tube(cr, t, speed=1.0):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#1A1A1C')); g.add_color_stop_rgb(1, *hexc('#0A0A0C')); cr.set_source(g); cr.paint()
    cx, cy = W / 2, 960
    for k in range(14, 0, -1):
        ph = ((k - (t * speed) % 1) / 14)
        rx, ry = 40 + ph ** 2 * 1400, 30 + ph ** 2 * 1100
        cr.save(); cr.translate(cx, cy); cr.scale(1, ry / rx)
        circle(cr, 0, 0, rx, shade(hexc('#4A4642'), .4 + .6 * ph))
        circle(cr, 0, 0, rx * .93, shade(hexc('#3A3632'), .35 + .5 * ph))
        cr.restore()
    g = cairo.RadialGradient(cx, cy, 10, cx, cy, 700); g.add_color_stop_rgba(0, 1, .95, .8, .35); g.add_color_stop_rgba(1, 1, .95, .8, 0); cr.set_source(g); cr.paint()

def ice_cave(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#05070C')); g.add_color_stop_rgb(1, *hexc('#0E1420')); cr.set_source(g); cr.paint()
    ang = math.sin(t * 1.2) * .6 - .2
    bx, by = W / 2 - 120, 1500
    cr.save(); cr.translate(bx, by)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 1300); g.add_color_stop_rgba(0, 1, 1, .95, .5); g.add_color_stop_rgba(1, 1, 1, .95, 0)
    cr.move_to(0, 0); cr.arc(0, 0, 1300, -math.pi / 2 + ang - .3, -math.pi / 2 + ang + .3); cr.close_path(); cr.set_source(g); cr.fill()
    cr.restore()
    r = random.Random(3)
    for k in range(220):
        x, y = r.uniform(0, W), r.uniform(300, 1400)
        a = math.atan2(y - by, x - bx) + math.pi / 2
        lit = max(0, 1 - abs(a - ang) / .35)
        if lit <= 0: continue
        tw = .5 + .5 * math.sin(t * 9 + k)
        s = r.uniform(4, 12)
        cr.set_source_rgba(.75, .92, 1, lit * tw); cr.move_to(x, y - s); cr.line_to(x + s * .4, y); cr.line_to(x, y + s); cr.line_to(x - s * .4, y); cr.close_path(); cr.fill()
    front_char(cr, bx, 1900, 600, 'O', arm='flash', t=t, jacket=hexc('#F2F2F0'))
    hx, hy, hr = bx, 1900 - 8.2 * 60, 165
    g = cairo.RadialGradient(hx - 50, hy - 60, 10, hx, hy, hr); g.add_color_stop_rgba(0, 1, 1, 1, .35); g.add_color_stop_rgba(1, .8, .9, 1, .12)
    cr.set_source(g); cr.arc(hx, hy, hr, 0, 7); cr.fill(); cr.set_line_width(10); cr.set_source_rgba(.95, .95, .95, .9); cr.arc(hx, hy, hr, 0, 7); cr.stroke()

def dust_macro(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#1A1A1C')); g.add_color_stop_rgb(1, *hexc('#2A2A2C')); cr.set_source(g); cr.paint()
    z = 1 + .4 * prog(t, 73.9, 81.8)
    r = random.Random(7)
    for k in range(26):
        x = (r.uniform(0, W) + t * r.uniform(-20, 20)); y = r.uniform(200, 1700) + math.sin(t + k) * 20
        s = r.uniform(40, 140) * z; rot = t * r.uniform(-.4, .4) + k
        n = r.randint(5, 8)
        cr.save(); cr.translate(x, y); cr.rotate(rot)
        pts = [(math.cos(i / n * 6.28) * s * r.uniform(.4, 1.1), math.sin(i / n * 6.28) * s * r.uniform(.4, 1.1)) for i in range(n)]
        g = cairo.LinearGradient(-s, -s, s, s); g.add_color_stop_rgb(0, *hexc('#D9D9D4')); g.add_color_stop_rgb(1, *hexc('#5A5A58'))
        cr.move_to(*pts[0]); [cr.line_to(*p) for p in pts[1:]]; cr.close_path(); cr.set_source(g); cr.fill()
        cr.restore()

# ======================= SCENES (timed in original narration seconds) =======================
def s1(cr, t):
    if t < 2.3:
        space(cr, t); earth_in_sky(cr, 200, 300, 90)
        R = 300 + 3000 * ease(prog(t, .2, 2.3)) ** 2
        moon_disk(cr, W / 2, 1100 + R * .6, R, rot=t * .05)
        post(cr, t, grain=.06); return
    moon_sky(cr, t)
    iso = IsoR(cr, 1, 1, .8, keys(t, [(2.3, 140), (7.3, 105)]), oy=.6, light=(1.6, .6), shadow=.4)
    moon_ground(iso)
    crouch = 1 - ease(prog(t, 4.6, 5.6))
    astronaut(iso, 1, 1, crouch=crouch)
    iso.draw(); post(cr, t)

def s2(cr, t):
    if t < 14.39:
        visor(cr, t, 1 - .6 * prog(t, 9.0, 14.3)); post(cr, t); return
    moon_sky(cr, t)
    px = keys(t, [(14.39, -7), (19.8, 4.8)])
    iso = IsoR(cr, px + 2, 2, 1.2, 60, oy=.6, light=(1.6, .6), shadow=.4)
    moon_ground(iso, seed=2)
    lander(iso, 7.5, 0.5, door=prog(t, 19.0, 19.8))
    if t < 20.5:
        hop = abs(math.sin((t - 14.39) * 2.6))
        astronaut(iso, px, 2.2, z=hop * 1.4)
    iso.draw()
    if t > 15.0:
        x, y = iso.P(px, 2.4, 0)
        cr.save(); cr.translate(x, y); cr.scale(1, .3); circle(cr, 0, 0, 60, (0, 0, 0), .25); cr.restore()
    post(cr, t)

def s3(cr, t):
    if t < 31.96:
        moon_sky(cr, t, earth=False)
        cxw = keys(t, [(21.7, -4), (31.9, 10)])
        iso = IsoR(cr, cxw, 3, 0, 46, oy=.55, light=(2.6, 1.0), shadow=.55)
        moon_ground(iso, seed=3)
        iso.draw()
        bx = keys(t, [(21.7, 700), (31.9, -200)])
        cr.move_to(bx, 0); cr.line_to(bx + 500, 0); cr.line_to(bx + 300, H); cr.line_to(bx - 200, H); cr.close_path()
        g = cairo.LinearGradient(bx - 200, 0, bx + 500, 0); g.add_color_stop_rgba(0, 0, 0, .02, 0); g.add_color_stop_rgba(.4, 0, 0, .02, .75); g.add_color_stop_rgba(1, 0, 0, .02, .85)
        cr.set_source(g); cr.fill(); cr.rectangle(bx + 500, 0, W, H); cr.set_source_rgba(0, 0, .02, .85); cr.fill()
        if t > 23.86: thermo(cr, 200, 1200, .2 + .75 * prog(t, 24.0, 27.5), C['red'], prog(t, 23.86, 24.2))
        if t > 28.34: thermo(cr, W - 200, 1200, .6 - .55 * prog(t, 28.5, 31.0), hexc('#3B82D6'), prog(t, 28.34, 28.7))
        post(cr, t); return
    lava_tube(cr, t * .8); post(cr, t)

def s4(cr, t):
    if t < 46.39:
        space(cr, t)
        heat = ease(prog(t, 42.8, 45.5))
        g = cairo.RadialGradient(W / 2, 1000, 50, W / 2, 1000, 700); g.add_color_stop_rgba(0, 1, .5, .1, .5 * heat); g.add_color_stop_rgba(1, 1, .4, .1, 0); cr.set_source(g); cr.paint()
        draw_rock(cr, W / 2, 1000, 300, rot=t * 8, sun=(-.6, -.5, .6), heat=heat * 1.2)
        if t > 44.0:
            r = random.Random(1)
            for k in range(14):
                ph = (t * .6 + k / 14) % 1; x = W / 2 + r.uniform(-220, 220) + math.sin(t * 2 + k) * 20; y = 760 - ph * 600
                a = (1 - ph) * prog(t, 44.0, 44.6)
                circle(cr, x - 14, y, 18, hexc('#7FD3FF'), a); circle(cr, x + 14, y, 18, hexc('#7FD3FF'), a)
        post(cr, t); return
    moon_sky(cr, t)
    iso = IsoR(cr, 2, 2, .8, 72, oy=.6, light=(1.6, .6), shadow=.4)
    moon_ground(iso, seed=4)
    iso.box(-1, -1, 0, 1.6, 1.6, 1.6, hexc('#B8BEC8'), deco=lambda i, *b: i.frect(b, 'x', .2, .3, .8, .7, hexc('#FF8A3A'), glow=False))
    iso.box(1.2, -.8, 0, .9, .9, 1.8, hexc('#E2E6EC'), deco=lambda i, *b: i.frect(b, 'x', .2, .6, .8, .8, hexc('#3B82D6')))
    for k in range(4):
        st = 46.6 + k * .5
        if t < st: continue
        p = ease(prog(t, st, st + .4))
        iso.box(-1 + k * 1.3, 2.6, .5, 1.1 * p + .05, 1.6, .1, C['panel'])
    astronaut(iso, 3.6, .6)
    iso.draw(); post(cr, t)

def s5(cr, t):
    if t < 57.78:
        moon_sky(cr, t, earth=False)
        cxw = keys(t, [(50.4, -10), (57.7, 10)])
        iso = IsoR(cr, cxw, cxw * .3, 0, 32, oy=.55, light=(4.0, 1.6), shadow=.6)
        moon_ground(iso, seed=5, ext=90, n=70)
        r = random.Random(9)
        for k in range(25):
            x, y = r.uniform(-30, 30), r.uniform(-30, 30); s = r.uniform(1, 3)
            iso.box(x, y, 0, s, s, s * .8, GREY3)
        iso.draw()
        post(cr, t, vignette=.6); return
    ice_cave(cr, t); post(cr, t)

def s6(cr, t):
    moon_sky(cr, t)
    iso = IsoR(cr, 1.5, 1.5, .8, 74, oy=.6, light=(1.6, .6), shadow=.35)
    moon_ground(iso, seed=6)
    g = ease(prog(t, 66.5, 71.0))
    for row in range(3):
        for k in range(4):
            iso.box(-.6 + k * 1.0, -.6 + row * 1.2, .05, .6, .8, .1 + .9 * g * (1 - .2 * row), hexc('#4FB548'))
    astronaut(iso, 4.2, 3.6, arms_up=1 if 71.9 < t < 73.0 else 0)
    iso.draw()
    inf = eout(prog(t, 65.6, 66.8))
    if inf > 0:
        cx, cy = iso.P(1.0, 1.0, 0)
        R = 330 * inf
        cr.save(); cr.translate(cx, cy); cr.scale(1, .95)
        g2 = cairo.RadialGradient(-R * .3, -R * .5, 10, 0, -R * .3, R * 1.1); g2.add_color_stop_rgba(0, 1, .6, 1, .35); g2.add_color_stop_rgba(1, .7, .5, 1, .12)
        cr.arc(0, 0, R, math.pi, 2 * math.pi); cr.close_path(); cr.set_source(g2); cr.fill()
        cr.set_line_width(4); cr.set_source_rgba(1, 1, 1, .6); cr.arc(0, 0, R, math.pi, 2 * math.pi); cr.stroke()
        cr.restore()
    if 72.0 < t < 73.8: text_center(cr, '!', W / 2 + 280, 700, 220, C['yellow'], stroke=C['dark'], sw=14, scale=back((t - 72.0) / .3))
    post(cr, t)

def s7(cr, t):
    if t < 81.81: dust_macro(cr, t); post(cr, t); return
    if t < 84.62: visor(cr, t, None, scratches=prog(t, 81.9, 84.0)); post(cr, t); return
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#D9DEE6')); g.add_color_stop_rgb(1, *hexc('#9AA3AE')); cr.set_source(g); cr.paint()
    sh = math.sin(t * 40) * 8
    cr.save(); cr.translate(sh, 0)
    iso = IsoR(cr, 1, 1, .8, 120, oy=.55, light=(-1.0, -.4), shadow=.2)
    iso.ground(hexc('#C9CED6'))
    iso.box(-2.5, -2.5, 0, .3, 6, 3.5, hexc('#B8BEC8')); iso.box(-2.5, -2.5, 0, 6, .3, 3.5, hexc('#AAB0BA'))
    px = 1 + math.sin(t * 6) * 1.2
    astronaut(iso, px, 1, phase=t * 14)
    iso.draw()
    r = random.Random(int(t * 12))
    for k in range(30):
        circle(cr, W / 2 + r.uniform(-400, 400), r.uniform(700, 1400), r.uniform(10, 40), (.6, .6, .58), r.uniform(.2, .6))
    cr.restore(); post(cr, t)

def s8(cr, t):
    moon_sky(cr, t)
    iso = IsoR(cr, 2, 2, .8, 60, oy=.6, light=(3.0, 1.2), shadow=.45)
    moon_ground(iso, seed=8)
    lander(iso, -2, -2)
    iso.box(3, 1, 0, 1.2, 1.2, 1.4, hexc('#E2E6EC'))
    iso.draw()
    p = ease(prog(t, 92.0, 95.5))
    cr.save(); cr.set_operator(cairo.OPERATOR_MULTIPLY); cr.set_source_rgba(*mix((1, 1, 1), hexc('#1A2240'), p * .9), 1)
    cr.rectangle(0, 0, W, H); cr.fill(); cr.restore()
    if p > .5:
        for (x, y) in (iso.P(-.5, -.5, 3), iso.P(3.6, 1.6, 1.6)):
            g = cairo.RadialGradient(x, y, 5, x, y, 160); g.add_color_stop_rgba(0, 1, .9, .6, .8); g.add_color_stop_rgba(1, 1, .9, .6, 0); cr.set_source(g); cr.arc(x, y, 160, 0, 7); cr.fill()
    if t > 97.3:
        lv = 1 - .85 * prog(t, 97.5, 102.5)
        rrect(cr, W / 2 - 110, 1200, 220, 380, 24); fill(cr, hexc('#2A2F38'))
        rrect(cr, W / 2 - 40, 1170, 80, 40, 10); fill(cr, hexc('#2A2F38'))
        col = C['green'] if lv > .5 else (C['yellow'] if lv > .25 else C['red'])
        rrect(cr, W / 2 - 90, 1220 + 340 * (1 - lv), 180, 340 * lv, 16); fill(cr, col)
    post(cr, t)

def s9(cr, t):
    if t < 109.35:
        space(cr, t, sun_at=(-80, 1700, 50))
        moon_disk(cr, 230, 1300, 150)
        draw_globe(cr, 820, 560, 200, lon0=200, tilt=.3, sun=(-.8, .4, .5), clouds=.7)
        p = prog(t, 105.9, 108.9)
        if p > 0:
            x0, y0, x1, y1 = 330, 1200, 700, 690
            x, y = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
            cr.set_line_width(6); cr.set_dash([18, 14]); cr.set_source_rgba(.6, .9, 1, .6); cr.move_to(x0, y0); cr.line_to(x, y); cr.stroke(); cr.set_dash([])
            g = cairo.RadialGradient(x, y, 0, x, y, 60); g.add_color_stop_rgba(0, .7, .95, 1, 1); g.add_color_stop_rgba(1, .7, .95, 1, 0); cr.set_source(g); cr.arc(x, y, 60, 0, 7); cr.fill()
            text_center(cr, f"{1.3 * p:.1f} S", W / 2, 1000, 120, C['white'], stroke=C['dark'], sw=12)
        post(cr, t, grain=.06); return
    moon_sky(cr, t)
    iso = IsoR(cr, 1.5, 1.5, 2.6, 90, oy=.58, light=(1.6, .6), shadow=.35)
    moon_ground(iso, seed=9)
    lander(iso, 0, 0)
    def dish(i):
        x, y = i.P(1.5, 1.5, 5.6); r = 1.2 * i.S
        i.cr.save(); i.cr.translate(x, y); i.cr.rotate(-.5); i.cr.scale(1, .45)
        g = cairo.RadialGradient(-r * .3, -r * .3, 5, 0, 0, r); g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, *hexc('#9AA3AE'))
        i.cr.set_source(g); i.cr.arc(0, 0, r, 0, 7); i.cr.fill(); i.cr.restore()
    iso.box(1.4, 1.4, 4.4, .2, .2, 1.2, C['metal'])
    iso.custom(100, dish)
    astronaut(iso, 3.2, 2.2, z=4.4)
    iso.draw()
    if t > 110.9:
        x, y = iso.P(1.5, 1.5, 6.2); cr.set_line_width(8)
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1; cr.set_source_rgba(.6, .95, 1, 1 - ph); cr.arc(x, y, 40 + ph * 300, -2.6, -.5); cr.stroke()
    post(cr, t)

def s10(cr, t):
    cuts = [(wt('Oxygen', 112), 'o'), (wt('Ice', 113), 'i'), (wt('Greenhouse', 114), 'g'), (wt('Batteries', 115), 'b'), (wt('Radio', 116), 'r')]
    cur = cuts[0][1]
    for t0, k in cuts:
        if t >= t0 - .05: cur = k
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(math.sin(t * 3) * .04); cr.scale(1.06, 1.06); cr.translate(-W / 2, -H / 2)
    if cur == 'o': s4(cr, 48.5 + (t - 112.69))
    elif cur == 'i': ice_cave(cr, t); post(cr, t)
    elif cur == 'g': s6(cr, 72.8)
    elif cur == 'b': s8(cr, 99.0 + (t - 115.94) * 3)
    else: s9(cr, 111.5 + (t - 116.76))
    cr.restore()

def s11(cr, t):
    moon_sky(cr, t)
    iso = IsoR(cr, 1, 1, 1.0, 100, oy=.6, light=(1.6, .6), shadow=.4)
    moon_ground(iso, seed=1)
    astronaut(iso, 1, 1, z=abs(math.sin((t - 117.8) * 1.6)) * 1.6, arms_up=1)
    iso.draw()
    r = random.Random(12); el = t - 117.86
    for k in range(120):
        x = r.uniform(0, W); v = r.uniform(80, 160); y = -50 - r.uniform(0, 600) + el * v
        cr.save(); cr.translate(x + math.sin(el + k) * 20, y); cr.rotate(el * r.uniform(1, 2) + k)
        cr.rectangle(-11, -6, 22, 12); fill(cr, r.choice(PROD + [C['panel'], C['green']])); cr.restore()
    post(cr, t)

def s12(cr, t):
    moon_sky(cr, t)
    iso = IsoR(cr, 1.5, 1.5, 2.0, keys(t, [(121.2, 90), (130.2, 70)]), oy=.62, light=(1.6, .6), shadow=.35)
    moon_ground(iso, seed=9)
    lander(iso, 0, 0)
    astronaut(iso, 4.2, 3.2)
    iso.draw()
    if t > 122.2:
        r = random.Random(int(t * 15))
        x, y = iso.P(1.5, 1.5, 5.2)
        cr.set_line_width(5)
        for k in range(4):
            cr.set_source_rgba(1, 1, 1, .8); cr.move_to(x, y)
            for s_ in range(1, 5): cr.line_to(x + r.uniform(-30, 30) + s_ * 20, y - s_ * 30)
            cr.stroke()
    if t > 124.5:
        p = ease(prog(t, 124.5, 130.0)); sx, sy = 300, 360
        R = 10 + 120 * p
        g = cairo.RadialGradient(sx, sy, 0, sx, sy, R * 4); g.add_color_stop_rgba(0, 1, 1, 1, 1); g.add_color_stop_rgba(.2, .7, .9, 1, .8); g.add_color_stop_rgba(1, .5, .7, 1, 0)
        cr.set_source(g); cr.arc(sx, sy, R * 4, 0, 7); cr.fill()
        cr.set_line_width(4); cr.set_source_rgba(.8, .95, 1, .7)
        cr.move_to(sx - R * 6, sy); cr.line_to(sx + R * 6, sy); cr.move_to(sx, sy - R * 3); cr.line_to(sx, sy + R * 3); cr.stroke()
    post(cr, t)

SCENES = [(0, 7.32, s1), (7.32, 21.74, s2), (21.74, 36.74, s3), (36.74, 50.36, s4), (50.36, 63.26, s5), (63.26, 73.85, s6),
          (73.85, 90.68, s7), (90.68, 102.71, s8), (102.71, 112.69, s9), (112.69, 117.86, s10), (117.86, 121.24, s11), (121.24, 140, s12)]
END_OUT = 124.6     # seconds of output video
CTA_O = 125.3       # original-timeline second when the CTA appears

def overlays(cr, t):
    G, R_, Y = C['green'], C['red'], C['yellow']
    counter(cr, t, 2.4, 7.32, '384,400 KM', 'FROM HOME')
    pill(cr, t, wt('atmosphere'), 14.39, 'NO ATMOSPHERE', W / 2, 330, R_)
    title(cr, t, wt('shelter'), 21.74, 'SHELTER', y=330)
    if 24.0 <= t < 31.96:
        if t < 28.34: counter(cr, t, 24.0, 28.34, '120 °C', 'IN THE SUN')
        else: counter(cr, t, 28.34, 31.96, '−150 °C', 'IN THE SHADOWS')
    title(cr, t, wt('lava'), 36.74, 'LAVA TUBES', y=330)
    pill(cr, t, wt('half'), 46.39, 'ROCK: ~45% OXYGEN', W / 2, 330, Y)
    title(cr, t, wt('reactor'), 50.36, 'OXYGEN REACTOR', y=330)
    pill(cr, t, wt('craters'), 57.78, 'PERMANENT SHADOW', W / 2, 330, Y)
    title(cr, t, wt('ice', 58), 63.26, 'ICE MINE', y=330)
    title(cr, t, wt('greenhouse', 64), 73.85, 'GREENHOUSE', y=330)
    pill(cr, t, wt('glass'), 81.81, 'SHARP AS GLASS', W / 2, 330, R_)
    pill(cr, t, wt('scratches'), 84.62, 'SCRATCHED VISOR', W / 2, 330, R_)
    counter(cr, t, wt('two', 92), 97.3, '14 DAYS', 'OF DARKNESS')
    title(cr, t, wt('batteries', 97), 102.71, 'BATTERIES', y=330)
    pill(cr, t, wt('transmitting'), 112.69, 'TRANSMITTING...', W / 2, 330, G)
    for a, lbl in (('Oxygen', 'OXYGEN REACTOR'), ('Ice', 'ICE MINE'), ('Greenhouse', 'GREENHOUSE'), ('Batteries', 'BATTERIES'), ('Radio', 'RADIO')):
        t0 = wt(a, 112); nx = {'Oxygen': wt('Ice', 113), 'Ice': wt('Greenhouse', 114), 'Greenhouse': wt('Batteries', 115), 'Batteries': wt('Radio', 116), 'Radio': 117.86}[a]
        pill(cr, t, t0, nx, lbl, W / 2, 330, G)
    title(cr, t, 117.9, 121.24, 'CONGRATULATIONS!', y=360, size=120, sub='You survived on the Moon')
    if t >= CTA_O:
        title(cr, t, CTA_O, 999, 'COMMENT', y=560, size=110, tilt=0, col=C['white'])
        title(cr, max(t, CTA_O + .25), CTA_O + .25, 999, '"MOON"', y=720, size=150, tilt=-.07)
        if t > CTA_O + .6:
            text_center(cr, "if you'd survive", W / 2, 880, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - CTA_O - .6) / .3))
    if t < 126.6: caption(cr, t, WORDS)

def render(t_out, surf):
    t = t_out * SPEED
    cr = ctx_for(surf)
    EARTH[0] = False
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    if EARTH[0]: earth_in_sky(cr, 880, 250, 95)
    overlays(cr, t)
