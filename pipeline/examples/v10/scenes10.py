import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5'); sys.path.append('/home/claude/vid6')
import cairo
from engine import *
from real import *
from scenes import stars, clouds
from scenes6 import cut_earth

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 53.551
END = DUR + 1.4

def float_z(t):
    """height of floating objects (iso units) in the 5-second street scene"""
    if t < 16.6: return 0.0
    if t < 42.1: return 2.6 * ease(prog(t, 16.6, 22.0)) + .2 * math.sin(t * 1.7)
    return max(0.0, (2.6 + .2 * math.sin(42.1 * 1.7)) * (1 - prog(t, 42.1, 43.9) ** 2))

def street(cr, t, S=75, cx=2, cy=2, shake=0.0, timer=None):
    sky(cr); clouds(cr, t, 4)
    z = float_z(t)
    iso = IsoR(cr, cx + math.sin(t * 60) * .05 * shake, cy, .5 + z * .08, S, oy=.6, light=(1.3, .55), shadow=.35)
    iso.ground(C['grass'])
    iso.quad(-20, 3.5, 50, 3, C['road'], z=.01)
    for k in range(-20, 30, 3): iso.quad(k, 4.85, 1.4, .2, C['line'], z=.02)
    iso.quad(-20, 2.2, 50, 1.3, C['walk'], z=.02)
    building(iso, -4, -3, 3, 3, 4, C['wall'], lit=None)
    house(iso, 1, -2.5, 3, 3, 2.2)
    building(iso, 6, -3, 3, 3, 6, hexc('#D9C6A5'))
    tree(iso, 4.6, 1.4); tree(iso, -1.6, 1.4, s=1.2)
    r = random.Random(4)
    # floating things: cars, people, water drops, balls
    car(iso, 1.0 + .2 * z, 3.8, C['red'], along='x') if z <= 0 else None
    if z > 0:
        iso.box(1.0, 3.8, z * .8, 2.4, 1.2, .9, C['red'], key=6.4)
        iso.box(1.4, 3.9, z * .8 + .9, 1.4, 1.0, .6, C['glass'], key=6.41)
        iso.box(5.5, 4.3, z * .6, 2.4, 1.2, .9, hexc('#3B82D6'), key=10.4)
    else:
        car(iso, 5.5, 4.3, hexc('#3B82D6'), along='x')
    for k, (px, py) in enumerate(((-.5, 2.6), (2.4, 2.5), (3.8, 2.7), (-2.3, 2.8))):
        zz = z * (1 + .25 * k) + (.08 * math.sin(t * 3 + k) if z > 0 else 0)
        person(iso, px, py, z=zz, arms_up=1 if z > .3 else 0, phase=None if z > 0 else t * 6 + k, jacket=[C['jacket'], hexc('#3B82D6'), C['green'], C['orange']][k])
    iso.draw()
    if z > .3:
        for k in range(9):
            x, y = iso.P(-1 + k * .8, 3 + (k % 3) * .3, 1.2 + z + math.sin(t * 2 + k) * .3)
            circle(cr, x, y, 16 + (k % 3) * 6, C['water'], .85); circle(cr, x - 5, y - 6, 5, C['white'], .8)
    if timer is not None:
        clock_ring(cr, W - 170, 520, 110, timer)
    post(cr, t)
    return iso

def clock_ring(cr, x, y, R, frac):
    circle(cr, x + 6, y + 8, R, (0, 0, 0), .3); circle(cr, x, y, R, C['dark'])
    cr.set_line_width(R * .22); cr.set_source_rgb(*C['yellow'])
    cr.arc(x, y, R * .78, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (1 - frac)); cr.stroke()
    n = max(1, math.ceil(5 * (1 - frac)))
    text_center(cr, f'{n}s', x, y, R * .9, C['white'])

def globe_shot(cr, t, R, cy=960, arrow=0.0, flip=0.0):
    space(cr, t)
    cr.save(); cr.translate(W / 2, cy); cr.rotate(flip * math.pi); cr.translate(-W / 2, -cy)
    draw_globe(cr, W / 2, cy, R, lon0=(t * 25) % 360, tilt=.35, sun=(-.6, -.35, .72))
    cr.restore()
    if arrow > 0:
        cr.set_line_width(26); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_source_rgba(*C['yellow'], arrow)
        cr.save(); cr.translate(W / 2, cy); cr.scale(1, .32)
        a0 = 1.9 - 1.6 * arrow; cr.arc_negative(0, 0, R * 1.08, 2.0, a0); cr.stroke(); cr.restore()
        ex, ey = W / 2 + math.cos(a0) * R * 1.08, cy + math.sin(a0) * R * 1.08 * .32
        cr.move_to(ex - 10, ey - 40); cr.line_to(ex + 60, ey + 5); cr.line_to(ex - 10, ey + 45); cr.close_path(); fill(cr, C['yellow'], arrow)

def tangent_shot(cr, t):
    """side view: planet curve, person keeps straight line"""
    sky(cr, hexc('#5EB6F2'), hexc('#CDEBFF'))
    R = 3200; cx, cy = W / 2, 1500 + R
    rot = (t - 9.9) * .05
    circle(cr, cx, cy, R, C['grass']); circle(cr, cx, cy, R - 120, hexc('#8C6A45'))
    # houses on curve
    for k in range(-8, 9):
        a = -math.pi / 2 + k * .045 - rot
        hx, hy = cx + math.cos(a) * R, cy + math.sin(a) * R
        cr.save(); cr.translate(hx, hy); cr.rotate(a + math.pi / 2)
        rrect(cr, -50, -110, 100, 110, 6); fill(cr, C['wall'] if k % 2 else hexc('#D9C6A5'))
        cr.move_to(-62, -108); cr.line_to(0, -170); cr.line_to(62, -108); cr.close_path(); fill(cr, C['roof'])
        cr.restore()
    # person moving straight along tangent; ground curves away
    p = prog(t, 11.0, 16.9)
    gap = 260 * ease(p)
    px, py = W / 2, 1500 - 40 - gap
    cr.set_line_width(8); cr.set_dash([22, 18]); cr.set_source_rgba(1, 1, 1, .8 * prog(t, 11.5, 12))
    cr.move_to(0, py - 30); cr.line_to(W, py - 30); cr.stroke(); cr.set_dash([])
    # little character
    cr.save(); cr.translate(px, py)
    front_char(cr, 0, 0, 220, expr='shock' if p > .3 else 'O', arm='up' if p > .3 else 'down', t=t)
    cr.restore()
    if p > .1:
        cr.set_line_width(6); cr.set_source_rgba(1, 1, 1, .7)
        for k in range(4):
            yy = py + 20 + k * 30
            cr.move_to(px - 30, yy + gap * .3); cr.line_to(px + 30, yy + gap * .3); cr.stroke()
    post(cr, t)

def spring(cr, x, y, h, coils=8, w=70, c=None):
    c = c or C['yellow']
    cr.set_line_width(14); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_source_rgb(*c)
    cr.move_to(x, y)
    for k in range(coils * 2 + 1):
        cr.line_to(x + (w if k % 2 else -w), y - h * k / (coils * 2))
    cr.line_to(x, y - h); cr.stroke()

def core_shot(cr, t):
    space(cr, t)
    relax = ease(prog(t, 34.2, 38.5))
    R = 430 * back(prog(t, 27.2, 27.7)) * (1 + .06 * relax + .02 * math.sin(t * 9) * relax)
    shake = math.sin(t * 45) * 8 * relax
    # compress arrows
    if t < 34.2:
        for k in range(8):
            a = k / 8 * 6.28; d = R * 1.35 - 30 * math.sin(t * 4)
            x, y = W / 2 + math.cos(a) * d, 960 + math.sin(a) * d
            cr.save(); cr.translate(x, y); cr.rotate(a + math.pi)
            cr.move_to(0, -26); cr.line_to(60, 0); cr.line_to(0, 26); cr.close_path(); fill(cr, C['red'], .9 * prog(t, 31.0, 31.6))
            cr.restore()
    cut_earth(cr, W / 2 + shake, 960, R, t, spin=t * .2)
    if t > 37.4:
        hh = 120 + 220 * ease(prog(t, 37.6, 38.6)) + 30 * math.sin(t * 12)
        spring(cr, W / 2, 960 + 60, hh)
    if relax > 0:
        r = random.Random(2)
        cr.set_source_rgba(1, 1, 1, .8 * relax); cr.set_line_width(6)
        for k in range(10):
            a = r.uniform(0, 6.28); d = R * r.uniform(.6, .95)
            x, y = W / 2 + math.cos(a) * d, 960 + math.sin(a) * d
            cr.move_to(x, y); cr.line_to(x + r.uniform(-50, 50), y + r.uniform(-50, 50)); cr.stroke()
    post(cr, t)

# ---------------- scenes ----------------
def s1(cr, t):
    R = keys(t, [(0, 260), (3.9, 380)])
    globe_shot(cr, t, R)
    if t > 2.6:
        a = prog(t, 2.6, 2.9); clock_ring(cr, W / 2, 1740, 120 * back(prog(t, 2.6, 3.0)), 0)
    post(cr, t)

def s2(cr, t):
    if t < 9.9:
        globe_shot(cr, t, keys(t, [(3.9, 380), (9.9, 430)]), arrow=ease(prog(t, 5.6, 7.0)))
        post(cr, t); return
    tangent_shot(cr, t)

def s3(cr, t):
    S = keys(t, [(17.0, 60), (21.5, 85), (23.9, 70), (27.1, 62)])
    frac = prog(t, 17.5, 42.1)
    street(cr, t, S=S, timer=frac)
    if 21.4 < t < 23.9:
        # glass with water bubbles close-up inset
        a = prog(t, 21.4, 21.8) * (1 - prog(t, 23.6, 23.9))
        x, y = 280, 620
        rrect(cr, x - 160, y - 200, 320, 400, 40); fill(cr, C['white'], .92 * a)
        cr.set_source_rgba(*C['dark'], a); cr.set_line_width(8)
        cr.move_to(x - 70, y - 120); cr.line_to(x - 55, y + 150); cr.line_to(x + 55, y + 150); cr.line_to(x + 70, y - 120); cr.stroke()
        for k in range(6):
            bx = x + math.sin(t * 2 + k * 1.3) * 60; by = y + 60 - ((t - 21.4) * 80 + k * 50) % 300
            circle(cr, bx, by, 18 + (k % 3) * 8, C['water'], .9 * a); circle(cr, bx - 6, by - 7, 5, C['white'], a)

def s4(cr, t):
    if t < 30.4:
        # look down at the feet/ground then dive inside
        S = keys(t, [(27.1, 62), (30.4, 160)])
        street(cr, t, S=S, timer=prog(t, 17.5, 42.1))
        cr.set_source_rgba(0, 0, 0, prog(t, 29.6, 30.4)); cr.paint(); return
    core_shot(cr, t)

def s5(cr, t):
    shake = prog(t, 43.7, 44.0) * (1 - prog(t, 44.6, 45.3))
    street(cr, t, S=keys(t, [(39.2, 75), (42.0, 85), (44.0, 70)]), shake=shake, timer=prog(t, 17.5, 42.1) if t < 42.1 else None)
    if t > 43.8:
        a = prog(t, 43.8, 44.0) * (1 - prog(t, 44.3, 45.2))
        cr.set_source_rgba(1, 1, 1, .3 * a); cr.paint()
        r = random.Random(3)
        for k in range(30):
            ph = prog(t, 43.8, 45.2)
            x = r.uniform(0, W); y = 1250 + r.uniform(-200, 200) - ph * 200
            circle(cr, x, y, 40 + ph * 60, hexc('#E8DCC8'), .6 * (1 - ph))
    if 41.4 < t < 42.6:
        a = (.5 + .5 * math.sin(t * 25)) * .5
        text_center(cr, '0s', W - 170, 520, 100, C['red'], stroke=C['dark'], sw=10, alpha=a)

def s6(cr, t):
    flip = ease(prog(t, 48.5, 49.9))
    globe_shot(cr, t, keys(t, [(45.2, 300), (50.3, 420)]), flip=flip)
    if t > 45.4:
        clock_ring(cr, W / 2, 1740, 120 * back(prog(t, 45.4, 45.8)), prog(t, 45.4, 49.9))
    post(cr, t)

def s7(cr, t):
    globe_shot(cr, t, 330, cy=1100)
    post(cr, t)

SCENES = [(0, 3.9, s1), (3.9, 17.2, s2), (17.2, 27.1, s3), (27.1, 39.2, s4), (39.2, 45.2, s5), (45.2, 50.3, s6), (50.3, 999, s7)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    title(cr, t, .6, 2.6, 'SEM GRAVIDADE', y=330)
    counter(cr, t, 6.9, 9.9, '1.700 KM/H', 'NA LINHA DO EQUADOR')
    pill(cr, t, 12.0, 14.6, 'O CHÃO FAZ A CURVA', W / 2, 330, Y)
    title(cr, t, 16.4, 17.2, 'FLUTUANDO!', y=330, col=hexc('#7FD3FF'))
    counter(cr, t, 20.2, 21.4, '~50 CM', 'EM 5 SEGUNDOS')
    pill(cr, t, 21.5, 23.8, 'ÁGUA EM BOLHAS', W / 2, 330, C['water'])
    title(cr, t, 23.8, 27.0, 'TUDO DESCOLA', y=330)
    title(cr, t, 31.6, 34.1, 'ESPREMIDO', y=330, col=R_)
    pill(cr, t, 36.8, 39.1, 'ROCHAS RELAXAM', W / 2, 330, Y)
    title(cr, t, 41.4, 43.8, 'GRAVIDADE VOLTA', y=330, col=G)
    title(cr, t, 43.8, 45.2, 'TUDO CAI!', y=330, col=R_)
    title(cr, t, 48.6, 50.3, 'DE CABEÇA PRA BAIXO', y=300)
    if t >= 50.4:
        title(cr, t, 50.4, 999, 'COMENTA', y=420, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 50.7), 50.7, 999, 'ONDE VOCÊ ESTARIA?', y=580, size=110, tilt=-.06)
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
