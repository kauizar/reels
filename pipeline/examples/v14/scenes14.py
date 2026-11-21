import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
from scenes import clouds

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 47.726
END = DUR + 1.4

def dragonfly(cr, x, y, s, t, a=1.0, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    f = math.sin(t * 35) * .25
    for sx in (-1, 1):
        for k, (ox, L) in enumerate(((-6, 120), (14, 110))):
            cr.save(); cr.translate(ox, 0); cr.rotate(sx * (1.4 + f + k * .15) - math.pi / 2)
            cr.save(); cr.scale(1, .22); circle(cr, L / 2, 0, L / 2, (.8, .92, 1), .45 * a); cr.restore()
            cr.set_source_rgba(.4, .6, .8, .5 * a); cr.set_line_width(1.5); cr.move_to(0, 0); cr.line_to(L, 0); cr.stroke()
            cr.restore()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*hexc('#1E6E8A'), a); cr.set_line_width(14); cr.move_to(0, 0); cr.line_to(-150, 0); cr.stroke()
    for k in range(7):
        circle(cr, -30 - k * 18, 0, 6, hexc('#2FA0C0'), a)
    cr.save(); cr.scale(1.3, 1); circle(cr, 10, 0, 16, hexc('#1E6E8A'), a); cr.restore()
    circle(cr, 36, -10, 12, hexc('#3CC46A'), a); circle(cr, 36, 10, 12, hexc('#3CC46A'), a)
    cr.restore()

def flames(cr, x, y, s, t, a=1.0, seed=0):
    r = random.Random(seed)
    for layer, col in ((1.0, hexc('#E8473C')), (.7, hexc('#F59A3B')), (.42, hexc('#FFD23F'))):
        cr.move_to(x - 60 * s * layer, y)
        n = 5
        for k in range(n + 1):
            px = x - 60 * s * layer + k * 120 * s * layer / n
            h = (110 + 60 * math.sin(t * 9 + k * 1.7 + seed)) * s * layer * (1.3 if k in (2, 3) else .8)
            cr.line_to(px - 10 * s, y - h * .5); cr.line_to(px, y - h)
        cr.line_to(x + 60 * s * layer, y); cr.close_path(); fill(cr, col, a)

def molecule(cr, x, y, s, col, a=1.0, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    circle(cr, -14 * s, 0, 18 * s, col, a); circle(cr, 14 * s, 0, 18 * s, shade(col, .9), a)
    circle(cr, -18 * s, -6 * s, 5 * s, (1, 1, 1), .5 * a)
    cr.restore()

def bolt(cr, x, y, h, a):
    pts = [(x, y), (x - 40, y + h * .35), (x + 20, y + h * .38), (x - 30, y + h * .7), (x + 30, y + h * .72), (x - 10, y + h)]
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for w, col in ((30, (1, 1, .7)), (12, (1, 1, 1))):
        cr.set_source_rgba(*col, a); cr.set_line_width(w); cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        cr.stroke()

def eagle(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    f = math.sin(t * 4) * .2
    col = hexc('#5A3A22')
    for sx in (-1, 1):
        cr.save(); cr.scale(sx, 1); cr.rotate(f)
        cr.move_to(20, -10); cr.curve_to(120, -80, 220, -60, 300, -30); cr.line_to(260, -10); cr.line_to(280, 10); cr.line_to(230, 15); cr.curve_to(150, 20, 60, 20, 20, 15); cr.close_path(); fill(cr, col, a)
        cr.restore()
    cr.save(); cr.scale(1, 1.6); circle(cr, 0, 0, 34, col, a); cr.restore()
    circle(cr, 0, -60, 26, C['white'], a); cr.move_to(10, -55); cr.line_to(34, -45); cr.line_to(10, -42); cr.close_path(); fill(cr, C['yellow'], a)
    cr.move_to(-20, 50); cr.line_to(0, 90); cr.line_to(20, 50); cr.close_path(); fill(cr, col, a)
    cr.restore()

def s1(cr, t):
    sky(cr, hexc('#CFEAFB'), hexc('#F2FAFF'))
    dbl = ease(prog(t, 4.9, 5.8))
    r = random.Random(3)
    n_o = int(12 + 12 * dbl)
    for k in range(40):
        is_o = k < n_o
        x = (r.uniform(0, W) + math.sin(t * .9 + k) * 60) % W; y = (r.uniform(300, 1600) + math.cos(t * .7 + k * 2) * 60)
        molecule(cr, x, y, 1.6, hexc('#3B82D6') if is_o else hexc('#B4BAC4'), .9, t + k)
    pct = 21 + 21 * dbl
    cx, cy, R = W / 2, 1650, 120
    circle(cr, cx, cy, R + 16, C['dark']); circle(cr, cx, cy, R, hexc('#E2E6EC'))
    cr.move_to(cx, cy); cr.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * pct / 100); cr.close_path(); fill(cr, hexc('#3B82D6'))
    post(cr, t)

def s2(cr, t):
    if t < 9.4:
        sky(cr, hexc('#BFE6FA'), hexc('#EAF6FC'))
        front_char(cr, W / 2, 1700, 620, expr='happy', arm='up', t=t)
        for k in range(8):
            ph = (t * .6 + k / 8) % 1
            molecule(cr, W / 2 + math.sin(k * 2) * 250 * (1 - ph), 760 + 400 * (1 - ph), 1.4, hexc('#3B82D6'), 1 - ph * .5, t)
        post(cr, t); return
    sky(cr, hexc('#2A0E08'), hexc('#5A1E0E'))
    flames(cr, W / 2, 1300, 4.0 * back(prog(t, 9.4, 9.9)), t)
    post(cr, t)

def forest(cr, t, burn_t):
    sky(cr, mix(hexc('#8FCFE8'), hexc('#3A1A10'), prog(t, burn_t, burn_t + 3)), mix(hexc('#DDF2E8'), hexc('#8A3A1A'), prog(t, burn_t, burn_t + 3)))
    iso = IsoR(cr, 3, 3, 0, keys(t, [(10.5, 60), (21, 45)]), oy=.58, light=(1.4, .5), shadow=.35)
    iso.ground(mix(C['grass'], hexc('#3A2A1E'), prog(t, burn_t + 1, burn_t + 5)))
    r = random.Random(7)
    trees = [(r.uniform(-6, 12), r.uniform(-6, 12)) for _ in range(36)]
    for x, y in trees: tree(iso, x, y, s=r.uniform(.9, 1.4))
    iso.draw()
    for k, (x, y) in enumerate(trees):
        d = math.hypot(x - 3, y - 3)
        start = burn_t + d * .35
        if t > start:
            px, py = iso.P(x + .5, y + .5, 0)
            flames(cr, px, py, .9 + 1.0 * prog(t, start, start + 1), t, .95, seed=k)
    return iso

def s3(cr, t):
    if t < 14.6:
        forest(cr, t, 12.2)
        if t > 11.4:
            x, y = W / 2, 1000
            flames(cr, x, y, 1.2 * back(prog(t, 11.4, 11.8)), t)
        post(cr, t); return
    if t < 17.0:
        sky(cr, hexc('#4E7A5A'), hexc('#2A4A32'))
        for k in range(6):
            x = 150 + k * 160
            cr.set_source_rgb(*C['leaf2']); cr.set_line_width(20); cr.move_to(x, 1500); cr.curve_to(x - 40, 1200, x + 40, 1000, x, 800); cr.stroke()
            cr.save(); cr.translate(x, 800); cr.scale(.5, 1); circle(cr, 0, 0, 90, C['leaf']); cr.restore()
            circle(cr, x + 30, 900 + (t * 200 + k * 50) % 400, 12, C['water'], .8)
            if t > 15.8:
                flames(cr, x, 1100, 1.2 * prog(t, 15.8 + k * .1, 16.3 + k * .1), t, seed=k)
        post(cr, t); return
    forest(cr, t, 17.5)
    if 17.0 < t < 17.9:
        a = 1 - prog(t, 17.5, 17.9)
        cr.set_source_rgba(1, 1, 1, .5 * a); cr.paint()
        bolt(cr, W / 2, 0, 1000, a)
    post(cr, t)

def s4(cr, t):
    sky(cr, hexc('#8FBF6A'), hexc('#D8E8B0'))
    r = random.Random(2)
    for k in range(8):
        x = 60 + k * 140; h = r.uniform(700, 1100)
        cr.set_source_rgb(*hexc('#5A4A2A')); cr.rectangle(x - 18, 1700 - h, 36, h); cr.fill()
        for j in range(5):
            cr.save(); cr.translate(x, 1700 - h + j * 30); cr.rotate((j - 2) * .5); cr.scale(1, .25); circle(cr, 0, 0, 140, hexc('#3E7A3A'), .9); cr.restore()
    cr.rectangle(0, 1700, W, 220); fill(cr, hexc('#4A6A2A'))
    s = 1.0 + 1.6 * ease(prog(t, 27.1, 29.9))
    x = W / 2 + math.sin(t * .8) * 120; y = 800 + math.sin(t * 1.3) * 60
    dragonfly(cr, x, y, s, t, ang=math.sin(t) * .1)
    if t > 29.6:
        a = prog(t, 29.6, 30.0)
        cr.set_source_rgba(*C['yellow'], a); cr.set_line_width(10)
        cr.move_to(x - 150 * s, y + 140 * s * .6); cr.line_to(x + 50 * s, y + 140 * s * .6); cr.stroke()
        text_center(cr, '70 cm', x - 50 * s, y + 140 * s * .6 + 60, 70, C['yellow'], stroke=C['dark'], sw=10, alpha=a)
    front_char(cr, 150, 1720, 260, expr='shock', t=t)
    post(cr, t)

def s5(cr, t):
    sky(cr, hexc('#0E2238'), hexc('#1E3A58'))
    grow = 1 + .35 * ease(prog(t, 35.2, 37.5))
    cx, cy = W / 2, 950
    cr.save(); cr.translate(cx, cy); cr.scale(grow, grow)
    cr.save(); cr.scale(1.9, 1); circle(cr, 0, 0, 200, hexc('#2FA0C0'), .35); cr.restore()
    cr.set_line_width(5); cr.set_source_rgba(.9, .95, 1, .8)
    for k in range(10):
        x0 = -340 + k * 75; sy = -1 if k % 2 else 1
        cr.move_to(x0, sy * 200); cr.curve_to(x0, sy * 120, x0 + 30, sy * 60, x0 + 20, 0); cr.stroke()
        for b in range(2):
            cr.move_to(x0 + 20, 0); cr.line_to(x0 + 50 + b * 10, sy * (40 + b * 30)); cr.stroke()
    r = random.Random(1)
    for k in range(24):
        ph = (t * .5 + k / 24) % 1; x0 = -340 + (k % 10) * 75; sy = -1 if (k % 10) % 2 else 1
        circle(cr, x0 + 20 * ph, sy * 200 * (1 - ph), 8, hexc('#7FD3FF'), 1 - ph * .3)
    cr.restore()
    post(cr, t)

def s6(cr, t):
    sky(cr, hexc('#1A1028'), hexc('#3A1E3A'))
    molecule(cr, 200, 900, 3 * back(prog(t, 38.8, 39.2)), hexc('#3B82D6'))
    text_center(cr, '+', 200, 760, 100, C['white'], alpha=prog(t, 38.8, 39.2))
    if t > 40.3: text_center(cr, '=', 380, 900, 120, C['white'], scale=back(prog(t, 40.3, 40.6)))
    if t > 41.1: flames(cr, 600, 1000, 1.5 * back(prog(t, 41.1, 41.5)), t)
    if t > 42.0:
        text_center(cr, '+', 770, 900, 100, C['white'])
        dragonfly(cr, 950, 900, .9 * back(prog(t, 42.0, 42.4)), t)
    post(cr, t)

def s7(cr, t):
    sky(cr, hexc('#7FC6F0'), hexc('#D8F0FA'))
    clouds(cr, t, 3)
    s = back(prog(t, 43.8, 44.3))
    eagle(cr, W / 2 - 230, 1050, 1.0 * s, t)
    dragonfly(cr, W / 2 + 330, 1050, 1.9 * back(prog(t, 44.7, 45.2)), t)
    if t > 45.4: text_center(cr, 'VS', W / 2 + 40, 1050, 110, C['white'], stroke=C['dark'], sw=12, scale=back(prog(t, 45.4, 45.7)))
    post(cr, t)

SCENES = [(0, 5.9, s1), (5.9, 10.5, s2), (10.5, 21.0, s3), (21.0, 31.2, s4), (31.2, 37.9, s5), (37.9, 43.8, s6), (43.8, 999, s7)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    counter(cr, t, 1.9, 4.9, '21%', 'DE OXIGÊNIO NO AR')
    counter(cr, t, 4.9, 5.9, '42%?', 'E SE DOBRASSE')
    pill(cr, t, 6.2, 8.4, 'RESPIRAR MAIS FÁCIL', W / 2, 330, C['water'])
    title(cr, t, 9.4, 10.5, 'FOGO', y=330, col=hexc('#FF7A3A'))
    pill(cr, t, 12.0, 14.5, 'TUDO QUEIMA MAIS FÁCIL', W / 2, 330, R_)
    pill(cr, t, 14.6, 17.0, 'ATÉ PLANTAS ÚMIDAS', W / 2, 330, C['water'])
    title(cr, t, 18.6, 21.0, 'INCÊNDIO GIGANTE', y=330, col=R_)
    counter(cr, t, 22.6, 27.0, '300 MILHÕES', 'DE ANOS ATRÁS')
    title(cr, t, 27.6, 29.6, 'LIBÉLULAS GIGANTES', y=330, size=100)
    pill(cr, t, 33.0, 37.8, 'RESPIRAM POR TUBOS', W / 2, 330, Y)
    title(cr, t, 38.6, 43.7, 'MAIS O2 = MAIS FOGO + INSETOS GIGANTES', y=300, size=60, tilt=-.03)
    if t >= 44.0:
        title(cr, t, 44.0, 999, 'VOCÊ AGUENTARIA?', y=420, size=115, tilt=-.05)
        if t > 46.9: title(cr, t, 46.9, 999, 'COMENTA', y=580, size=110, tilt=0, col=C['white'])
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
