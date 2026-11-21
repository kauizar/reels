import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5'); sys.path.append('/home/claude/vid6'); sys.path.append('/home/claude/vid12')
import cairo
from engine import *
from real import *
from scenes6 import capsule
from scenes12 import astro

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 94.746
END = DUR + 1.5

def iss(cr, x, y, s, t):
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.rotate(math.sin(t * .2) * .05)
    rrect(cr, -260, -8, 520, 16, 6); fill(cr, hexc('#B9BEC6'))
    for sx in (-1, 1):
        for k in range(2):
            px = sx * (150 + k * 80)
            for sy in (-1, 1):
                cr.rectangle(px - 30, sy * 20 if sy > 0 else -20 - 150, 60, 150); fill(cr, hexc('#2D4A86'))
                for j in range(5):
                    cr.rectangle(px - 30, (sy * 20 if sy > 0 else -170) + j * 30, 60, 2); fill(cr, hexc('#6E8FD0'))
    rrect(cr, -90, -40, 180, 80, 30); fill(cr, hexc('#E8ECF2'))
    rrect(cr, -30, -70, 60, 140, 26); fill(cr, hexc('#D2D8E0'))
    circle(cr, 40, 0, 14, hexc('#3B82D6'))
    cr.restore()

def module_bg(cr, t, tilt=0.0):
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(tilt); cr.translate(-W / 2, -H / 2)
    cr.rectangle(-400, -400, W + 800, H + 800); fill(cr, hexc('#C9CED6'))
    for k in range(-4, 14):
        y = k * 180
        cr.rectangle(-400, y, W + 800, 14); fill(cr, hexc('#A9B0BA'))
        for j in range(-2, 8):
            rrect(cr, j * 220 + 40, y + 40, 140, 90, 10); fill(cr, [hexc('#E8ECF2'), hexc('#F2D49A'), hexc('#B8D4F0')][(j + k) % 3])
    circle(cr, W / 2, 380, 150, hexc('#0B1030')); cr.set_line_width(20); cr.set_source_rgb(*hexc('#8D96A3')); cr.arc(W / 2, 380, 150, 0, 7); cr.stroke()
    draw_globe(cr, W / 2 + 60, 470, 120, lon0=t * 10, tilt=.3)
    cr.restore()

def ear_spiral(cr, x, y, R, t, a=1.0):
    cr.set_line_width(R * .18); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_source_rgba(*C['pink'], a)
    cr.move_to(x, y)
    for k in range(80):
        th = k * .2; r = R * k / 80
        cr.line_to(x + math.cos(th + t * 4) * r, y + math.sin(th + t * 4) * r)
    cr.stroke()

def puffy_char(cr, cx, by, s, puff, t):
    """front_char with bigger head, thinner legs"""
    cr.save()
    # legs thin: draw char with horizontal squash on lower part via two clips
    cr.rectangle(0, by - s * .31, W, s); cr.clip()
    cr.translate(cx, 0); cr.scale(1 - .45 * puff, 1); cr.translate(-cx, 0)
    front_char(cr, cx, by, s, expr='sad', t=t)
    cr.restore()
    cr.save(); cr.rectangle(0, 0, W, by - s * .31); cr.clip()
    hy = by - s * .82
    cr.translate(cx, hy); cr.scale(1 + .35 * puff, 1 + .3 * puff); cr.translate(-cx, -hy)
    front_char(cr, cx, by, s, expr='sad', t=t)
    cr.restore()
    if puff > .3:
        u = s / 10
        for ex in (-1.3, 1.3):
            cr.save(); cr.translate(cx + ex * u * (1 + .35 * puff), by - 7.3 * u); cr.scale(1, .6); circle(cr, 0, 0, .55 * u, C['pink'], .6 * puff); cr.restore()

def spine(cr, x, y, n, gap, s=1.0):
    for k in range(n):
        yy = y - k * (40 * s + gap)
        rrect(cr, x - 50 * s, yy - 40 * s, 100 * s, 40 * s, 12 * s); fill(cr, hexc('#F2EEE4'))
        rrect(cr, x - 20 * s, yy - 40 * s - gap, 40 * s, gap, 6); fill(cr, hexc('#F2A0B0'), .9)

def bone(cr, x, y, s, holes):
    cr.save(); cr.translate(x, y); cr.rotate(-.5); cr.scale(s, s)
    rrect(cr, -160, -32, 320, 64, 30); fill(cr, hexc('#F2EEE4'))
    for sx in (-1, 1):
        circle(cr, sx * 170, -30, 42, hexc('#F2EEE4')); circle(cr, sx * 170, 30, 42, hexc('#F2EEE4'))
    r = random.Random(3)
    for k in range(int(40 * holes)):
        circle(cr, r.uniform(-180, 180), r.uniform(-40, 40), r.uniform(5, 13), hexc('#C9BCA8'))
    cr.restore()

def eye(cr, x, y, R, flat, t):
    cut = x - R * (1 - .22 * flat)
    cr.save(); cr.rectangle(cut - 6, 0, W, H); cr.clip()
    circle(cr, x, y, R + 10, C['dark']); circle(cr, x, y, R, C['white'])
    for k in range(6):
        a = k * .5 + 2.2
        cr.set_source_rgba(*C['red'], .35); cr.set_line_width(5)
        cr.move_to(x + math.cos(a) * R * .95, y + math.sin(a) * R * .95); cr.line_to(x + math.cos(a + .2) * R * .55, y + math.sin(a + .2) * R * .5); cr.stroke()
    circle(cr, x + R * .72, y, R * .32, hexc('#3B82D6')); circle(cr, x + R * .78, y, R * .15, C['dark']); circle(cr, x + R * .7, y - R * .1, R * .05, C['white'])
    cr.restore()
    if flat > 0:
        cr.set_source_rgb(*C['dark']); cr.set_line_width(12); cr.move_to(cut, y - R * .8); cr.line_to(cut, y + R * .8); cr.stroke()
        cr.set_source_rgba(*C['red'], .9); cr.set_line_width(14); cr.move_to(cut + 14, y - R * .55); cr.line_to(cut + 14, y + R * .55); cr.stroke()
        for k in range(4):
            ph = (t * .8 + k / 4) % 1
            cr.set_line_width(8); cr.set_source_rgba(.5, .8, 1, 1 - ph)
            xx = x - R - 180 + ph * 140
            cr.move_to(xx, y - 60 + k * 40); cr.line_to(xx + 50, y - 60 + k * 40); cr.stroke()

# ---------------- scenes ----------------
def s1(cr, t):
    space(cr, t)
    R = keys(t, [(0, 820), (7.1, 900)])
    draw_globe(cr, W / 2, 1500 + R * .6, R, lon0=60 + t * 4, tilt=-.15, sun=(-.5, -.6, .6))
    iss(cr, keys(t, [(0, -200), (7.1, W / 2 + 120)]), 760, 1.2, t)
    if t > 4.0:
        x = keys(t, [(4.0, W / 2 - 300), (7.1, W / 2)])
        astro(cr, x, 1150 + math.sin(t * 1.5) * 30, 220, rot=t * .5)
    post(cr, t)

def s2(cr, t):
    tilt = math.sin(t * 1.2) * .25 + (t - 7.1) * .2
    module_bg(cr, t, tilt)
    spin = (t - 7.1) * 1.4
    astro(cr, W / 2, 1150, 340, rot=spin)
    if t > 8.4:
        a = prog(t, 8.4, 8.8)
        cr.save(); cr.translate(W / 2 + math.cos(spin) * 0, 1150 - 120); cr.set_source_rgba(.4, .85, .3, .55 * a); cr.restore()
        for k in range(3):
            ph = (t * .7 + k / 3) % 1
            text_center(cr, '~', W / 2 + 200 + k * 30, 900 - ph * 200, 90, hexc('#6BD15A'), stroke=C['dark'], sw=8, alpha=a * (1 - ph))
    if t > 9.5:
        a = prog(t, 9.5, 10.0)
        circle(cr, 200, 650, 140, C['white'], .92 * a)
        ear_spiral(cr, 200, 650, 100 * a, t)
        if t > 13.3: text_center(cr, '?', 340, 520, 120, C['yellow'], stroke=C['dark'], sw=10, scale=back(prog(t, 13.3, 13.6)))
    if t > 14.5:
        a = prog(t, 14.5, 14.9); fl = math.sin(t * 3)
        for k, (lbl, yy) in enumerate((('CIMA', 1600), ('BAIXO', 1760))):
            text_center(cr, lbl if fl > 0 else ('BAIXO' if k == 0 else 'CIMA'), W / 2, yy, 70, C['white'], stroke=C['dark'], sw=10, alpha=a)
    post(cr, t)

def s3(cr, t):
    module_bg(cr, t, .05 * math.sin(t))
    puff = ease(prog(t, 18.6, 20.0))
    y = 1700 + math.sin(t * 1.2) * 20
    puffy_char(cr, W / 2, y, 640, puff, t)
    if 20.8 < t < 24.6:
        a = prog(t, 20.8, 21.2)
        for k in range(14):
            ph = (t * .8 + k / 14) % 1
            x = W / 2 + (k % 2 * 2 - 1) * 70; yy = y - 60 - ph * 520
            circle(cr, x, yy, 14, C['red'], a * (1 - ph * .5))
        cr.set_source_rgba(*C['red'], a); cr.set_line_width(14); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for sx in (-1, 1):
            cr.move_to(W / 2 + sx * 300, 1500); cr.line_to(W / 2 + sx * 300, 1150); cr.stroke()
            cr.move_to(W / 2 + sx * 300 - 30, 1190); cr.line_to(W / 2 + sx * 300, 1150); cr.line_to(W / 2 + sx * 300 + 30, 1190); cr.stroke()
    if t > 26.4:
        a = prog(t, 26.4, 26.8)
        circle(cr, 170, 700, 110, hexc('#F4F1E8'), a)
        for k, (dx, dy, rr) in enumerate(((-30, -20, 20), (30, 30, 14), (10, -50, 10))): circle(cr, 170 + dx, 700 + dy, rr, hexc('#D8D2C4'), a)
    post(cr, t)

def s4(cr, t):
    if t < 36.9:
        sky(cr, hexc('#1E2A4A'), hexc('#2E3E66'))
        gap = 6 + 22 * ease(prog(t, 31.0, 33.5))
        spine(cr, W / 2, 1550, 14, gap, 1.1)
        if t > 34.6:
            a = prog(t, 34.6, 35.0)
            top = 1550 - 14 * (44 + gap) + 40
            cr.set_source_rgba(*C['yellow'], a); cr.set_line_width(10)
            cr.move_to(W / 2 + 160, 1550 - 14 * 50 + 40); cr.line_to(W / 2 + 160, top); cr.stroke()
            text_center(cr, '+5 cm', W / 2 + 290, (top + 1550 - 14 * 50) / 2, 70, C['yellow'], stroke=C['dark'], sw=10, alpha=a)
        post(cr, t); return
    sky(cr, hexc('#DCE6F2'), hexc('#B9C8DC'))
    cr.rectangle(0, 1650, W, 270); fill(cr, hexc('#8A6B4E'))
    tall = ease(prog(t, 40.6, 41.6))
    front_char(cr, W / 2 - 220, 1700, 600, expr='smile', t=t, jacket=hexc('#3B82D6'))
    front_char(cr, W / 2 + 220, 1700, 600 * (1 + .09 * tall), expr='happy', arm='up' if tall > .5 else 'down', t=t, jacket=C['jacket'])
    if tall > 0:
        cr.set_source_rgba(*C['yellow'], tall); cr.set_line_width(8); cr.set_dash([16, 12])
        cr.move_to(W / 2 - 420, 1100); cr.line_to(W / 2 + 420, 1100); cr.stroke(); cr.set_dash([])
        text_center(cr, 'NA TERRA', W / 2 - 220, 960, 46, C['dark'], alpha=tall); text_center(cr, 'NO ESPAÇO', W / 2 + 220, 920, 46, C['dark'], alpha=tall)
    post(cr, t)

def s5(cr, t):
    sky(cr, hexc('#2A1A2A'), hexc('#4A2A3A'))
    if t < 49.2:
        holes = ease(prog(t, 45.2, 48.8))
        bone(cr, W / 2, 900, 2.0 * back(prog(t, 43.4, 43.9)), holes)
        rrect(cr, 140, 1660, 800, 60, 30); fill(cr, (0, 0, 0), .5)
        rrect(cr, 150, 1670, 780 * (1 - .12 * holes), 40, 20); fill(cr, C['red'] if holes > .5 else hexc('#F2EEE4'))
        post(cr, t); return
    if t < 53.4:
        shrink = ease(prog(t, 50.0, 52.5))
        front_char(cr, W / 2, 1700, 640, expr='sad', arm='up', t=t)
        for sx in (-1, 1):
            cr.save(); cr.translate(W / 2 + sx * 230, 1050); cr.scale(1.3 - .6 * shrink, 1.3 - .6 * shrink)
            circle(cr, 0, 0, 80, C['skin']); circle(cr, -20, -20, 30, shade(C['skin'], 1.1)); cr.restore()
        post(cr, t); return
    # treadmill
    cr.rectangle(0, 0, W, H); fill(cr, hexc('#C9CED6'))
    rrect(cr, 140, 1350, 800, 80, 30); fill(cr, C['dark'])
    for k in range(10):
        x = 160 + ((k * 80 - t * 400) % 760)
        cr.rectangle(x, 1360, 30, 60); fill(cr, hexc('#4A5260'))
    astro(cr, W / 2, 1150 + abs(math.sin(t * 8)) * -30, 320, rot=math.sin(t * 8) * .08)
    cr.set_source_rgba(.2, .2, .2, .9); cr.set_line_width(8)
    for sx in (-1, 1): cr.move_to(W / 2 + sx * 120, 1050); cr.line_to(W / 2 + sx * 300, 1360); cr.stroke()
    post(cr, t)

def s6(cr, t):
    sky(cr, hexc('#0E1A2E'), hexc('#1E3050'))
    flat = ease(prog(t, 62.4, 64.4))
    eye(cr, W / 2 + 60, 900, 330 * back(prog(t, 58.3, 58.8)), flat, t)
    if t > 65.0:
        a = prog(t, 65.0, 65.6)
        cr.save(); cr.rectangle(0, 1500, W, 300); cr.clip()
        for k in range(6):
            text_center(cr, 'E  F  P', W / 2 + math.sin(k) * 6 * a, 1640, 110, C['white'], alpha=.25)
        cr.restore()
        text_center(cr, 'E  F  P', W / 2, 1640, 110, C['white'], alpha=1 - .7 * a)
    post(cr, t)

def s7(cr, t):
    space(cr, t)
    draw_globe(cr, W / 2, 1300, 300, lon0=t * 8, tilt=.3)
    sh = 1 - .0
    cr.set_line_width(10); cr.set_source_rgba(.4, .7, 1, .6)
    for k in range(3):
        cr.save(); cr.translate(W / 2, 1300); cr.scale(1 + k * .25, .8 + k * .2); cr.arc(0, 0, 380, 0, 7); cr.restore(); cr.stroke()
    ix, iy = W / 2 + 330, 760
    iss(cr, ix, iy, .45, t)
    r = random.Random(5)
    for k in range(30):
        ph = (t * .6 + k / 30) % 1
        y0 = r.uniform(-200, 900)
        x = -100 + ph * (W + 200); y = y0 + ph * 200
        hit = abs(x - ix) < 160 and abs(y - iy) < 120
        circle(cr, x, y, 8, hexc('#FFD23F') if not hit else C['red'], .9)
        cr.set_source_rgba(1, .9, .3, .4); cr.set_line_width(4); cr.move_to(x, y); cr.line_to(x - 60, y - 12); cr.stroke()
    if t > 73.0:
        a = (.5 + .5 * math.sin(t * 10)) * prog(t, 73.0, 73.4)
        circle(cr, ix, iy, 200, C['red'], .25 * a)
    post(cr, t)

def s8(cr, t):
    if t < 78.2:
        sky(cr, hexc('#7FC6F0'), hexc('#D8F0FA'))
        y = keys(t, [(76.7, 200), (78.2, 1000)])
        cr.set_source_rgba(*C['white'], 1); cr.move_to(W / 2 - 250, y - 380); cr.curve_to(W / 2 - 200, y - 600, W / 2 + 200, y - 600, W / 2 + 250, y - 380); cr.close_path(); cr.fill()
        for k in range(5):
            cr.move_to(W / 2 - 250 + k * 125, y - 380); cr.line_to(W / 2, y - 60); cr.set_source_rgba(.3, .3, .3, .8); cr.set_line_width(3); cr.stroke()
        capsule(cr, W / 2, y, 1.2, heat=0.0)
        cr.rectangle(0, 1500, W, 420); fill(cr, hexc('#D9C89A'))
        post(cr, t); return
    sky(cr, hexc('#DCE6F2'), hexc('#B9C8DC'))
    cr.rectangle(0, 1650, W, 270); fill(cr, hexc('#8A6B4E'))
    wob = math.sin(t * 5) * .12
    cr.save(); cr.translate(W / 2, 1700); cr.rotate(wob); cr.translate(-W / 2, -1700)
    front_char(cr, W / 2, 1700, 640, expr='sad', arm='flash' if t > 81.5 else 'down', t=t)
    cr.restore()
    if t > 81.5:
        a = prog(t, 81.5, 81.9)
        rrect(cr, W / 2 + 230, 1060 + 60 * a, 180, 120, 20); fill(cr, C['dark'], a)
        text_center(cr, '100 KG?', W / 2 + 320, 980, 60, C['red'], stroke=C['dark'], sw=8, alpha=a)
    if t > 84.8:
        a = prog(t, 84.8, 85.2)
        for k in range(6):
            x = 170 + k * 150
            rrect(cr, x - 60, 560, 120, 130, 16); fill(cr, C['white'], a)
            text_center(cr, f'MÊS {k + 1}', x, 625, 34, C['dark'], alpha=a * prog(t, 85.0 + k * .15, 85.3 + k * .15))
    post(cr, t)

def s9(cr, t):
    space(cr, t)
    draw_globe(cr, W / 2, 1050, keys(t, [(87.5, 300), (92.7, 420)]), lon0=t * 10, tilt=.3)
    astro(cr, W / 2 + 300, 600, 200, rot=t * .4)
    post(cr, t)

SCENES = [(0, 7.1, s1), (7.1, 17.6, s2), (17.6, 29.3, s3), (29.3, 43.3, s4), (43.3, 58.3, s5), (58.3, 68.2, s6),
          (68.2, 76.7, s7), (76.7, 87.5, s8), (87.5, 92.7, s9), (92.7, 999, s9)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    counter(cr, t, 2.8, 7.0, '365 DIAS', 'FLUTUANDO')
    title(cr, t, 8.4, 9.5, 'ENJOO', y=330, col=hexc('#6BD15A'))
    pill(cr, t, 9.6, 14.4, 'OUVIDO INTERNO CONFUSO', W / 2, 330, Y)
    title(cr, t, 19.0, 20.6, 'ROSTO INCHADO', y=330)
    pill(cr, t, 20.8, 24.5, 'O SANGUE SOBE', W / 2, 330, R_)
    title(cr, t, 26.4, 29.2, 'CARA DE LUA CHEIA', y=330, size=100)
    title(cr, t, 29.9, 31.0, 'VOCÊ CRESCE', y=330, col=G)
    counter(cr, t, 35.0, 36.9, '+5 CM', 'MAIS ALTO')
    pill(cr, t, 37.8, 43.2, 'MAIS ALTO QUE O GÊMEO', W / 2, 330, Y)
    counter(cr, t, 47.0, 49.2, '-1%', 'DE OSSO POR MÊS')
    title(cr, t, 49.4, 53.3, 'MÚSCULOS ENCOLHEM', y=330, size=100, col=R_)
    counter(cr, t, 55.9, 58.2, '2 HORAS', 'DE EXERCÍCIO POR DIA')
    pill(cr, t, 58.4, 62.3, 'OS OLHOS MUDAM', W / 2, 330, C['water'])
    pill(cr, t, 62.4, 68.1, 'O FUNDO DO OLHO DEFORMA', W / 2, 330, R_)
    title(cr, t, 68.7, 71.5, 'RADIAÇÃO', y=330, col=Y)
    pill(cr, t, 73.0, 76.6, 'MUITO MAIS QUE NA TERRA', W / 2, 330, R_)
    title(cr, t, 77.3, 78.2, 'A VOLTA', y=330)
    pill(cr, t, 78.3, 84.7, 'FICAR EM PÉ É DIFÍCIL', W / 2, 330, R_)
    counter(cr, t, 85.0, 87.4, 'MESES', 'DE RECUPERAÇÃO')
    title(cr, t, 88.6, 92.6, 'MUDA SEU CORPO', y=330, col=G)
    if t >= 92.7:
        title(cr, t, 92.7, 999, 'VOCÊ TOPARIA?', y=420, size=120, tilt=-.05)
        if t > 94.0: title(cr, t, 94.0, 999, 'COMENTA', y=580, size=110, tilt=0, col=C['white'])
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
