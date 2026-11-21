import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
from scenes import clouds, heart

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 101.251
END = DUR + 1.6

def wings(cr, s, t, a, col=(1, 1, 1)):
    f = .6 + .4 * abs(math.sin(t * 40))
    for sx in (-1, 1):
        cr.save(); cr.translate(sx * 6 * s, -10 * s); cr.rotate(sx * .5); cr.scale(1, f)
        circle(cr, sx * 12 * s, -8 * s, 14 * s, col, .55 * a); cr.restore()

def bee(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y)
    wings(cr, s, t, a)
    cr.save(); cr.scale(1.4, 1); circle(cr, 0, 0, 16 * s, C['yellow'], a); cr.restore()
    for k in (-1, 0, 1): cr.rectangle(k * 9 * s - 3 * s, -15 * s, 6 * s, 30 * s); fill(cr, C['dark'], a)
    circle(cr, 22 * s, -2 * s, 9 * s, C['dark'], a)
    cr.restore()

def mosquito(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y); wings(cr, s, t, a)
    cr.save(); cr.scale(2.2, .6); circle(cr, 0, 0, 9 * s, hexc('#5A4A3A'), a); cr.restore()
    circle(cr, 22 * s, -3 * s, 6 * s, hexc('#3A2E24'), a)
    cr.set_source_rgba(*hexc('#3A2E24'), a); cr.set_line_width(2 * s)
    cr.move_to(26 * s, -2 * s); cr.line_to(42 * s, 6 * s); cr.stroke()
    for k in range(3):
        cr.move_to(-6 * s + k * 8 * s, 4 * s); cr.line_to(-14 * s + k * 10 * s, 22 * s); cr.stroke()
    cr.restore()

def fly(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y); wings(cr, s, t, a, (.8, .9, 1))
    circle(cr, 0, 0, 14 * s, hexc('#2E3440'), a); circle(cr, 14 * s, -4 * s, 10 * s, hexc('#2E3440'), a)
    circle(cr, 18 * s, -8 * s, 6 * s, hexc('#B33A3A'), a)
    cr.restore()

def roach(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y)
    cr.set_source_rgba(*hexc('#3A2414'), a); cr.set_line_width(3 * s)
    for k in range(3):
        for sx in (-1, 1):
            cr.move_to(-10 * s + k * 12 * s, 0); cr.line_to(-18 * s + k * 14 * s + math.sin(t * 20 + k) * 3 * s, sx * 22 * s); cr.stroke()
    cr.save(); cr.scale(1.6, 1); circle(cr, 0, 0, 14 * s, hexc('#7A4A24'), a); cr.restore()
    circle(cr, 22 * s, 0, 7 * s, hexc('#5A341A'), a)
    cr.move_to(26 * s, -3 * s); cr.line_to(48 * s, -14 * s); cr.move_to(26 * s, 3 * s); cr.line_to(48 * s, 14 * s); cr.stroke()
    cr.restore()

def fruit(cr, kind, x, y, s, a=1.0, grey=0.0):
    g = lambda c: mix(c, hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if kind == 'apple':
        circle(cr, -14, 0, 40, g(C['red']), a); circle(cr, 14, 0, 40, g(C['red']), a)
        cr.rectangle(-3, -54, 6, 20); fill(cr, g(C['trunk']), a)
        cr.save(); cr.translate(14, -46); cr.rotate(-.5); cr.scale(1, .5); circle(cr, 0, 0, 16, g(C['leaf']), a); cr.restore()
    elif kind == 'straw':
        cr.move_to(-40, -20); cr.curve_to(-40, 30, -10, 55, 0, 60); cr.curve_to(10, 55, 40, 30, 40, -20); cr.close_path(); fill(cr, g(C['red']), a)
        for k in range(6): circle(cr, -20 + (k % 3) * 20, -5 + (k // 3) * 25, 3, g(C['yellow']), a)
        cr.move_to(-35, -22); cr.line_to(0, -45); cr.line_to(35, -22); cr.close_path(); fill(cr, g(C['leaf']), a)
    elif kind == 'melon':
        cr.move_to(-60, -10); cr.arc_negative(0, -10, 60, math.pi, 0); cr.close_path()
        cr.move_to(-60, -10); cr.arc(0, -10, 60, 0, math.pi); cr.close_path(); fill(cr, g(C['green']), a)
        cr.arc(0, -10, 50, 0, math.pi); cr.close_path(); fill(cr, g(hexc('#FF5A6A')), a)
        for k in range(5): circle(cr, -30 + k * 15, 10 + (k % 2) * 12, 4, C['dark'], a)
    elif kind == 'coffee':
        rrect(cr, -40, -30, 70, 70, 14); fill(cr, g(C['white']), a)
        cr.set_line_width(8); cr.set_source_rgba(*g(C['white']), a); cr.arc(36, 4, 16, -1.5, 1.5); cr.stroke()
        cr.save(); cr.scale(1, .3); circle(cr, -5, -95, 30, g(hexc('#5A341A')), a); cr.restore()
    elif kind == 'nut':
        cr.save(); cr.scale(1, .8); circle(cr, 0, 0, 40, g(hexc('#B07A4A')), a); cr.restore()
        cr.set_source_rgba(*g(hexc('#7A4A24')), a); cr.set_line_width(4); cr.arc(0, 0, 25, 3.5, 5.9); cr.stroke()
    elif kind == 'cacao':
        cr.save(); cr.scale(.6, 1); circle(cr, 0, 0, 60, g(hexc('#C8741E')), a); cr.restore()
        cr.set_source_rgba(*g(hexc('#8A4A12')), a); cr.set_line_width(4)
        for k in (-20, 0, 20): cr.move_to(k, -55); cr.curve_to(k * 1.6, -20, k * 1.6, 20, k, 55); cr.stroke()
    elif kind in ('rice', 'wheat', 'corn'):
        col = {'rice': hexc('#F2F0E8'), 'wheat': hexc('#E8C66A'), 'corn': hexc('#F2C230')}[kind]
        rrect(cr, -45, -60, 90, 120, 18); fill(cr, hexc('#C9B48C'), a)
        text_center(cr, {'rice': 'ARROZ', 'wheat': 'TRIGO', 'corn': 'MILHO'}[kind], 0, 10, 22, C['dark'], alpha=a)
        circle(cr, 0, -30, 18, col, a)
    cr.restore()

def bird(cr, x, y, s, t, a=1.0, grey=0.0):
    col = mix(hexc('#3B82D6'), hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1.3, 1); circle(cr, 0, 0, 34, col, a); cr.restore()
    circle(cr, 36, -20, 22, col, a); circle(cr, 42, -24, 5, C['dark'], a)
    cr.move_to(56, -20); cr.line_to(76, -14); cr.line_to(56, -10); cr.close_path(); fill(cr, C['orange'], a)
    fl = math.sin(t * 12) * .6 * (1 - grey)
    cr.save(); cr.rotate(-fl); cr.move_to(-10, -10); cr.line_to(-60, -50); cr.line_to(10, -20); cr.close_path(); fill(cr, shade(col, .8), a); cr.restore()
    cr.restore()

def frog(cr, x, y, s, a=1.0, grey=0.0):
    col = mix(C['green'], hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1.4, 1); circle(cr, 0, 0, 34, col, a); cr.restore()
    for sx in (-1, 1): circle(cr, sx * 22, -30, 14, col, a); circle(cr, sx * 22, -30, 7, C['dark'], a)
    cr.restore()

def bat(cr, x, y, s, t, a=1.0, grey=0.0):
    col = mix(hexc('#5A4A6A'), hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    f = math.sin(t * 10) * .3 * (1 - grey)
    for sx in (-1, 1):
        cr.save(); cr.scale(sx, 1); cr.rotate(f)
        cr.move_to(10, 0); cr.line_to(70, -30); cr.line_to(60, 0); cr.line_to(45, -5); cr.line_to(35, 12); cr.close_path(); fill(cr, col, a); cr.restore()
    circle(cr, 0, 0, 18, col, a); circle(cr, -6, -4, 3, C['white'], a); circle(cr, 6, -4, 3, C['white'], a)
    cr.restore()

def lizard(cr, x, y, s, a=1.0, grey=0.0):
    col = mix(hexc('#7BC44A'), hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.set_source_rgba(*col, a); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(-70, 10); cr.curve_to(-30, -10, 10, 10, 50, 0); cr.stroke()
    circle(cr, 55, -2, 14, col, a); circle(cr, 60, -6, 3, C['dark'], a)
    for k in (-20, 20):
        cr.move_to(k, 0); cr.line_to(k - 10, 22); cr.move_to(k, 0); cr.line_to(k + 10, -20); cr.stroke()
    cr.restore()

def fishy(cr, x, y, s, a=1.0, grey=0.0):
    col = mix(C['orange'], hexc('#8A8680'), grey)
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-50, 0); cr.curve_to(-25, -32, 30, -32, 50, 0); cr.curve_to(30, 32, -25, 32, -50, 0); cr.close_path(); fill(cr, col, a)
    cr.move_to(-45, 0); cr.line_to(-75, -24); cr.line_to(-75, 24); cr.close_path(); fill(cr, col, a)
    circle(cr, 30, -6, 5, C['dark'], a); cr.restore()

def poof(cr, x, y, p):
    if p <= 0 or p >= 1: return
    for k in range(8):
        a = k / 8 * 6.28
        circle(cr, x + math.cos(a) * 60 * p, y + math.sin(a) * 60 * p, 18 * (1 - p), C['white'], 1 - p)

# ---------------- scenes ----------------
def s1(cr, t):
    night = prog(t, 5.8, 7.0)
    sky(cr, mix(hexc('#F5E6C8'), hexc('#3A2030'), night), mix(hexc('#E8D2A8'), hexc('#1A0E14'), night))
    cr.rectangle(0, 1300, W, 620); fill(cr, mix(hexc('#8A6B4E'), hexc('#2A1A14'), night))
    happy = 4.2 <= t < 5.8
    front_char(cr, W / 2, 1700, 600, expr='happy' if happy else ('shock' if t >= 5.8 else 'disgust'), arm='up' if happy else 'down', t=t)
    gone = t > 3.3
    bugs = [(mosquito, .7), (roach, 2.0), (fly, 3.3)]
    for k, (fn, t_show) in enumerate(bugs):
        if t < t_show - .5: continue
        a = 1 - prog(t, 3.4, 3.6)
        x = W / 2 + math.cos(t * 2.3 + k * 2) * 330; y = 800 + math.sin(t * 3.1 + k) * 220
        if a > 0: fn(cr, x, y, 2.6, t, a)
        poof(cr, x, y, prog(t, 3.4, 3.9))
    if t >= 5.8:
        cr.set_source_rgba(.6, 0, .05, .25 * night); cr.paint()
    post(cr, t)

def s2(cr, t):
    sky(cr, hexc('#9FD3F0'), hexc('#E2F2FA'))
    cr.rectangle(0, 1350, W, 570); fill(cr, C['grass'])
    n = int(1500 * ease(prog(t, 10.0, 15.0)))
    r = random.Random(6)
    for k in range(n):
        a = r.uniform(0, 6.28); d = r.uniform(0, 1) ** .5 * 420
        x = W / 2 + 150 + math.cos(a + t * .3) * d; y = 800 + math.sin(a + t * .3) * d * .8
        circle(cr, x, y, 3.2, C['dark'], .75)
    front_char(cr, 180, 1600, 300, expr='O' if t > 15 else 'smile', t=t)
    post(cr, t)

FRUITS = [('apple', 25.7), ('straw', 26.3), ('melon', 27.2), ('coffee', 28.3), ('nut', 29.0)]
def s3(cr, t):
    if t < 30.2:
        sky(cr); clouds(cr, t, 3)
        iso = IsoR(cr, 3, 3, 0, keys(t, [(18.3, 60), (25.5, 80)]), oy=.58, light=(1.4, .5), shadow=.35)
        iso.ground(C['grass'])
        r = random.Random(3)
        for k in range(26):
            x, y = r.uniform(-3, 9), r.uniform(-3, 9)
            iso.box(x, y, 0, .12, .12, .8, C['leaf2'])
            iso.box(x - .2, y - .2, .8, .5, .5, .25, r.choice([C['pink'], C['yellow'], C['white'], C['purple']]))
        tree(iso, -2, 6, s=1.4); tree(iso, 8, -2, s=1.3)
        iso.draw()
        for k in range(7):
            x = W / 2 + math.sin(t * 1.3 + k * 1.7) * 400; y = 800 + math.cos(t * 1.1 + k) * 300
            bee(cr, x, y, 2.0, t)
            # pollen trail
            for j in range(4):
                tt = t - j * .08
                circle(cr, W / 2 + math.sin(tt * 1.3 + k * 1.7) * 400 - 20, 810 + math.cos(tt * 1.1 + k) * 300, 5, C['yellow'], .6 - j * .14)
        for k, (kind, t0) in enumerate(FRUITS):
            if t > t0:
                fruit(cr, kind, 150 + k * 195, 1700, 1.3 * back(prog(t, t0, t0 + .3)))
        post(cr, t); return
    sky(cr, hexc('#2E5A2A'), hexc('#1A3A18'))
    s = back(prog(t, 30.2, 30.7))
    fruit(cr, 'cacao', W / 2, 900, 4.0 * s)
    # tiny midge zoom
    if t > 32.0:
        z = ease(prog(t, 32.0, 33.0))
        x, y = W / 2 + 230 + math.sin(t * 3) * 40, 700 + math.cos(t * 4) * 30
        circle(cr, x, y, 110 * z, C['white'], .95); cr.set_line_width(10); cr.set_source_rgba(*C['dark'], z); cr.arc(x, y, 110 * z, 0, 7); cr.stroke()
        mosquito(cr, x - 10, y, 2.4 * z, t, z)
        cr.set_line_width(12); cr.move_to(x - 78 * z, y + 78 * z); cr.line_to(x - 160 * z, y + 160 * z); cr.stroke()
    if t > 31.0:
        rrect(cr, W / 2 - 200, 1550, 400, 180, 30); fill(cr, hexc('#5A341A'), prog(t, 31, 31.4))
        for k in range(3): cr.rectangle(W / 2 - 200 + k * 133, 1550, 4, 180); fill(cr, hexc('#3A2010'), prog(t, 31, 31.4))
    post(cr, t)

def s4(cr, t):
    sky(cr, hexc('#F2F2EE'), hexc('#DADAD4'))
    for row in range(3):
        y = 560 + row * 380
        rrect(cr, 60, y + 120, W - 120, 30, 6); fill(cr, hexc('#9AA3AD'))
        for k in range(5):
            kind = ['apple', 'straw', 'melon', 'coffee', 'nut'][(k + row) % 5] if row < 2 else ['rice', 'wheat', 'corn', 'rice', 'corn'][k]
            x = 160 + k * 190
            if row < 2:
                gone = prog(t, 36.8 + k * .3 + row * .4, 37.4 + k * .3 + row * .4)
                if gone < 1: fruit(cr, kind, x, y + 50, 1.0 * (1 - gone))
                poof(cr, x, y + 50, gone)
            else:
                fruit(cr, kind, x, y + 50, 1.5 * back(prog(t, 41.2 + k * .15, 41.6 + k * .15)) if t > 41.2 else .0001)
    if t > 44.6:
        a = prog(t, 44.6, 45.0)
        cr.set_source_rgba(.5, .7, 1, .7 * a); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(5):
            x0 = ((t * 500 + k * 260) % (W + 400)) - 300; y0 = 1240 + k * 40
            cr.move_to(x0, y0); cr.curve_to(x0 + 80, y0 - 30, x0 + 160, y0 + 30, x0 + 240, y0); cr.stroke()
    post(cr, t)

ANIMALS = [('bird', 49.7), ('frog', 50.9), ('bat', 51.7), ('lizard', 53.2), ('fish', 54.2)]
def s5(cr, t):
    sky(cr, hexc('#7FC6F0'), hexc('#D8F0FA'))
    cr.rectangle(0, 1350, W, 570); fill(cr, mix(C['grass'], hexc('#B8A47A'), prog(t, 56, 60.6)))
    # food chain: insect at center feeding animals
    pos = [(250, 600), (820, 620), (230, 1050), (840, 1080), (540, 1250)]
    for k, ((kind, t0), (x, y)) in enumerate(zip(ANIMALS, pos)):
        if t < t0: continue
        s = back(prog(t, t0, t0 + .3))
        grey = prog(t, 57.4 + k * .5, 58.4 + k * .5)
        fall = ease(prog(t, 58.8 + k * .4, 60.2 + k * .4)) * 400
        yy = y + fall
        if kind == 'bird': bird(cr, x, yy, 1.4 * s, t, grey=grey)
        elif kind == 'frog': frog(cr, x, yy, 1.6 * s, grey=grey)
        elif kind == 'bat': bat(cr, x, yy, 1.4 * s, t, grey=grey)
        elif kind == 'lizard': lizard(cr, x, yy, 1.4 * s, grey=grey)
        else: fishy(cr, x, yy, 1.5 * s, grey=grey)
        cr.set_source_rgba(1, 1, 1, .5 * (1 - grey)); cr.set_line_width(5); cr.set_dash([12, 10])
        cr.move_to(W / 2, 850); cr.line_to(x, yy); cr.stroke(); cr.set_dash([])
    ins = 1 - prog(t, 56.0, 56.6)
    bee(cr, W / 2, 850, 2.8, t, ins)
    poof(cr, W / 2, 850, prog(t, 56.0, 56.6))
    post(cr, t)

def s6(cr, t):
    pile = ease(prog(t, 66.5, 75.0))
    poor = prog(t, 75.2, 79.0)
    sky(cr, mix(hexc('#8FCFE8'), hexc('#C8B48A'), poor), mix(hexc('#DDF2E8'), hexc('#E8DCC0'), poor))
    iso = IsoR(cr, 3, 3, 0, keys(t, [(61.6, 70), (79, 90)]), oy=.58, light=(1.4, .5), shadow=.35)
    iso.ground(mix(hexc('#6E4A2E'), hexc('#B8A07A'), poor))
    r = random.Random(4)
    for k in range(70):
        x, y = r.uniform(-4, 10), r.uniform(-4, 10)
        if r.random() > pile: continue
        kind = r.random()
        if kind < .5: iso.box(x, y, 0, .7, .4, .08, r.choice([C['orange'], hexc('#C8501E'), hexc('#D9A43A')]))
        elif kind < .8: iso.box(x, y, 0, 2.2, .4, .4, C['trunk'])
        else: iso.box(x, y, 0, .5, .5, .3, hexc('#5A4A3A'))
    for k in range(6):
        x, y = -2 + k * 2.2, 6 - (k % 2) * 4
        h = 1.6 * (1 - .75 * poor)
        iso.box(x, y, 0, .25, .25, h, C['leaf2'])
        iso.box(x - .4, y - .4, h, 1.0, 1.0, .6 * (1 - .5 * poor), mix(C['leaf'], hexc('#A8924A'), poor))
    iso.draw()
    if t < 66.5:
        for k in range(10):
            x = (k * 140 + t * 30) % W; y = 1200 + (k % 3) * 60
            roach(cr, x, y, 1.0, t, 1 - prog(t, 63.5, 64.5))
    post(cr, t)

def s7(cr, t):
    sky(cr, hexc('#1E2238'), hexc('#2E3458'))
    a = prog(t, 80.2, 80.7)
    rrect(cr, 100, 520, W - 200, 640, 40); fill(cr, C['white'], .95 * a)
    lines = ['Sem insetos,', 'a humanidade', 'duraria só', 'alguns meses']
    for k, ln in enumerate(lines):
        aa = prog(t, 84.6 + k * .9, 85.0 + k * .9)
        text_center(cr, ln, W / 2, 680 + k * 105, 78, C['dark'], alpha=aa * a)
    text_center(cr, 'segundo o biólogo E. O. Wilson', W / 2, 1100, 46, hexc('#6E7A88'), alpha=prog(t, 81.2, 81.7))
    if t > 89.8:
        for k in range(4):
            x = 200 + k * 230; s = back(prog(t, 89.8 + k * .1, 90.2 + k * .1))
            rrect(cr, x - 70, 1300, 140, 150, 20); fill(cr, C['red'] if k < 3 else C['white'], 1)
            text_center(cr, ['MÊS 1', 'MÊS 2', 'MÊS 3', '?'][k], x, 1375, 40 * s, C['white'] if k < 3 else C['dark'])
    post(cr, t)

def s8(cr, t):
    sky(cr, hexc('#FFE3B0'), hexc('#FFC98A'))
    cr.save(); cr.translate(W / 2, 1000); cr.scale(1, .45); circle(cr, 0, 0, 420, C['white']); circle(cr, 0, 0, 340, hexc('#F2F0EA')); cr.restore()
    for k, kind in enumerate(['apple', 'straw', 'melon', 'nut', 'straw', 'apple']):
        if t > 91.6 + k * .2:
            fruit(cr, kind, W / 2 - 250 + k * 100, 980 + (k % 2) * 40, 1.1 * back(prog(t, 91.6 + k * .2, 91.9 + k * .2)))
    bx = keys(t, [(91.2, -100), (94.4, W / 2 + 200)]); by = 650 + math.sin(t * 4) * 40
    bee(cr, bx, by, 3.0, t)
    if t > 96.0: heart(cr, bx + 80, by - 120, 2 * back(prog(t, 96.0, 96.4)))
    post(cr, t, warm=.12)

def s9(cr, t):
    sky(cr, hexc('#2A3A5A'), hexc('#4A6A8A'))
    for k, fn in enumerate([mosquito, roach, fly, bee]):
        x = 170 + k * 250; y = 1200 + math.sin(t * 2 + k) * 30
        fn(cr, x, y, 2.4 * back(prog(t, 98.0 + k * .15, 98.4 + k * .15)), t)
    post(cr, t)

SCENES = [(0, 9.9, s1), (9.9, 18.3, s2), (18.3, 35.6, s3), (35.6, 47.0, s4), (47.0, 61.6, s5), (61.6, 80.1, s6),
          (80.1, 91.2, s7), (91.2, 98.0, s8), (98.0, 999, s9)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    title(cr, t, 4.2, 5.8, 'UM SONHO?', y=330, col=G)
    title(cr, t, 7.6, 9.8, 'PESADELO', y=330, col=R_)
    counter(cr, t, 15.3, 18.2, '+1 BILHÃO', 'DE INSETOS POR PESSOA')
    title(cr, t, 19.3, 21.0, 'GOLPE 1: COMIDA', y=330)
    pill(cr, t, 23.4, 25.6, 'POLINIZAÇÃO', W / 2, 330, Y)
    pill(cr, t, 30.6, 35.5, 'ATÉ O CHOCOLATE', W / 2, 330, hexc('#8A4A12'))
    pill(cr, t, 38.6, 41.0, 'PRATELEIRAS VAZIAS', W / 2, 330, R_)
    pill(cr, t, 41.2, 46.8, 'SÓ O QUE O VENTO POLINIZA', W / 2, 330, C['water'])
    title(cr, t, 47.6, 49.6, 'GOLPE 2: FOME', y=330)
    title(cr, t, 59.6, 61.5, 'EFEITO DOMINÓ', y=330, col=R_)
    title(cr, t, 64.5, 66.4, 'GOLPE 3: LIXO', y=330)
    pill(cr, t, 72.6, 75.1, 'TUDO SE ACUMULA', W / 2, 330, Y)
    pill(cr, t, 75.3, 79.9, 'SOLO POBRE', W / 2, 330, R_)
    counter(cr, t, 89.8, 91.1, 'ALGUNS MESES', 'PRA HUMANIDADE')
    title(cr, t, 94.4, 97.9, 'É ELE QUE TE ALIMENTA', y=330, size=96, col=G)
    if t >= 98.0:
        title(cr, t, 98.0, 999, 'QUAL INSETO', y=420, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 98.3), 98.3, 999, 'VOCÊ APAGARIA?', y=580, size=115, tilt=-.06)
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
