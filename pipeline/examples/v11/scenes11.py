import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5'); sys.path.append('/home/claude/vid3')
import cairo
from engine import *
from real import *
from scenes import stars, clouds, heart
from scenes3 import thermo

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 107.729
END = DUR + 1.5
SAND, SAND2 = hexc('#E8CF9A'), hexc('#CDAE74')
SEA, SEA2 = hexc('#2E86C8'), hexc('#1B5E96')
SEABED, SEABED2 = hexc('#8A6E52'), hexc('#6E553E')
SALT = hexc('#F4F2EC')

def beach(cr, t, level):
    sky(cr)
    clouds(cr, t, 4)
    S = keys(t, [(0, 70), (5.9, 95)])
    iso = IsoR(cr, 3, 2, 0, S, oy=.55, light=(1.3, .55), shadow=.35)
    iso.ground(SAND)
    shore = 2 + 12 * (1 - level)
    iso.quad(shore, -30, 60, 60, SEABED, z=.005)
    if level > 0:
        iso.quad(shore, -30, 60, 60, SEA, z=.02 + .6 * level, a=.9)
    r = random.Random(3)
    for k in range(10):
        x, y = r.uniform(4, 16), r.uniform(-6, 8)
        if x > shore: iso.box(x, y, 0, .6, .6, .4, SEABED2)
    # stranded boat
    bz = .6 * level
    iso.box(6, 1, bz, 2.6, 1.0, .6, C['white'], key=8)
    iso.box(6.8, 1.2, bz + .6, .9, .6, .6, C['red'], key=8.1)
    iso.box(-1, -3, 0, .2, .2, 2.4, C['trunk']); iso.box(-1.8, -3.8, 2.3, 1.8, 1.8, .2, C['leaf'])
    person(iso, 0, 1.5, arms_up=1 if level < .6 else 0)
    iso.draw(); post(cr, t)

def depth_profile(cr, t):
    sky(cr, hexc('#A8D8F0'), hexc('#E2F2FA'))
    base = 700
    drain = prog(t, 18.0, 18.3)
    cr.move_to(0, base)
    pts = [(0, base), (200, base + 200), (380, base + 220), (470, base + 1050), (560, base + 260), (W, base + 180)]
    for p in pts: cr.line_to(*p)
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path()
    g = cairo.LinearGradient(0, base, 0, H); g.add_color_stop_rgb(0, *SEABED); g.add_color_stop_rgb(1, *hexc('#3A2C20')); cr.set_source(g); cr.fill()
    # Everest drop into trench
    ev = ease(prog(t, 24.5, 25.4))
    ey = keys(t, [(24.5, 380), (25.4, base + 1050)])
    if t > 24.4:
        cr.move_to(470 - 230, ey); cr.line_to(470, ey - 520); cr.line_to(470 + 230, ey); cr.close_path(); fill(cr, hexc('#9AA3AD'))
        cr.move_to(470 - 90, ey - 330); cr.line_to(470, ey - 520); cr.line_to(470 + 90, ey - 330); cr.close_path(); fill(cr, C['white'])
        if t > 25.4: text_center(cr, 'EVEREST', 470, ey - 560, 56, C['white'], stroke=C['dark'], sw=8)
    # depth arrow
    if t > 20.7:
        a = prog(t, 20.7, 21.1)
        cr.set_source_rgba(*C['yellow'], a); cr.set_line_width(10)
        cr.move_to(700, base + 220); cr.line_to(700, base + 220 + 830 * ease(prog(t, 20.7, 22.0))); cr.stroke()
        text_center(cr, '11 km', 850, base + 640, 80, C['yellow'], stroke=C['dark'], sw=10, alpha=a)
    post(cr, t)

def salt_plain(cr, t):
    sky(cr, hexc('#2F7FC6'), hexc('#8EC3EA'))
    S = keys(t, [(26.4, 60), (32.0, 90), (38.9, 70)])
    iso = IsoR(cr, 2 + (t - 26.4) * .3, 2, 0, S, oy=.55, light=(1.5, .55), shadow=.3)
    iso.ground(mix(SEABED, hexc('#E4DED2'), ease(prog(t, 26.5, 29.0))))
    r = random.Random(5)
    for k in range(40):
        x, y = r.uniform(-12, 18), r.uniform(-12, 14); s = r.uniform(.3, 1.0)
        g = ease(prog(t, 26.6 + k * .05, 27.4 + k * .05))
        iso.box(x, y, 0, s, s, s * .9 * g + .01, SALT)
    iso.box(3, 3, 0, 4, 1.4, 1.0, hexc('#6E6A62'), key=6)
    iso.box(4, 3.3, 1.0, 1.4, .9, .8, hexc('#B9B3A8'), key=6.1)
    iso.draw()
    if t > 33.8:
        a = prog(t, 33.8, 34.2)
        rrect(cr, 120, 1580, 840, 230, 30); fill(cr, (0, 0, 0), .35 * a)
        h = 150 * ease(prog(t, 34.0, 35.5))
        cr.rectangle(160, 1760 - h, 760, h); fill(cr, SALT, a)
        cr.rectangle(160, 1760, 760, 30); fill(cr, SEABED, a)
        text_center(cr, 'SAL', W / 2, 1760 - h / 2, 60, C['dark'], alpha=a * prog(t, 34.5, 35))
    post(cr, t)

def plankton(cr, t):
    fade = prog(t, 48.6, 50.4)
    sky(cr, mix(hexc('#0E5C7A'), hexc('#3A3A38'), fade), mix(hexc('#06304A'), hexc('#22201E'), fade))
    r = random.Random(8)
    for k in range(26):
        x = (r.uniform(0, W) + math.sin(t * .5 + k) * 40) % W; y = (r.uniform(0, H) - t * 20 * r.uniform(.5, 1.5)) % H
        rr = r.uniform(30, 75) * (1 - fade * .3)
        col = mix(hexc('#5BD16A'), hexc('#6A6660'), fade)
        circle(cr, x, y, rr, col, .9 * (1 - fade * .6))
        circle(cr, x, y, rr * .55, shade(col, 1.2), .8 * (1 - fade * .6))
        cr.set_source_rgba(1, 1, 1, .3 * (1 - fade)); cr.set_line_width(4); cr.arc(x, y, rr, 3.6, 5.4); cr.stroke()
        if fade < .9 and k % 2 == 0:
            ph = (t * .7 + k / 26) % 1
            text_center(cr, 'O2', x + 30, y - rr - ph * 200, 36, C['white'], alpha=(1 - ph) * (1 - fade))
    # oxygen gauge
    lv = 1 - .5 * fade
    rrect(cr, 140, 1660, 800, 70, 35); fill(cr, (0, 0, 0), .5)
    rrect(cr, 150, 1670, 780 * lv, 50, 25); fill(cr, C['green'] if lv > .6 else C['red'])
    text_center(cr, f'OXIGÊNIO {int(lv * 100)}%', W / 2, 1610, 56, C['white'], stroke=C['dark'], sw=8)
    post(cr, t, vignette=.6)

def rain_scene(cr, t):
    dry = prog(t, 57.3, 61.8)
    sky(cr, mix(hexc('#7A8A9A'), hexc('#F2D49A'), dry), mix(hexc('#B8C4CE'), hexc('#F7E4B8'), dry))
    iso = IsoR(cr, 3, 3, 0, 70, oy=.58, light=(1.4, .5), shadow=.35)
    iso.ground(mix(C['grass'], hexc('#C9A86A'), dry))
    rw = 2.4 * (1 - dry) + .1
    iso.quad(-20, 2, 50, rw, mix(C['water'], hexc('#9E8460'), dry), z=.02)
    for k in range(-6, 12):
        for j in (5.5, 6.5, 7.5, -1.5, -2.5):
            g = 1 - dry
            iso.box(k, j, 0, .6, .6, .3 + .7 * g, mix(C['leaf'], hexc('#B8924A'), dry))
    house(iso, 8, -6, 3, 3, 2.2)
    iso.draw()
    rain = 1 - prog(t, 56.4, 57.6)
    if rain > 0:
        r = random.Random(1)
        cr.set_source_rgba(.85, .9, 1, .7 * rain); cr.set_line_width(4)
        for k in range(140):
            x = (r.uniform(0, W) + t * 200) % W; y = (r.uniform(0, H) + t * 1600) % H
            cr.move_to(x, y); cr.line_to(x - 12, y + 50); cr.stroke()
    cl = 1 - dry
    for k in range(4):
        x = 150 + k * 260 + math.sin(t * .4 + k) * 30
        for dx, dy, rr in ((0, 0, 90), (70, -30, 80), (140, 0, 90), (70, 20, 90)):
            circle(cr, x + dx, 300 + dy, rr, mix(hexc('#6E7A88'), C['white'], dry), .95 * cl)
    if dry > .3:
        cr.save(); cr.set_operator(cairo.OPERATOR_SOFT_LIGHT); cr.set_source_rgba(1, .7, .3, .3 * dry); cr.paint(); cr.restore()
    post(cr, t)

def climate(cr, t):
    split = ease(prog(t, 72.6, 73.6))
    if split <= 0:
        sky(cr, hexc('#0E3B66'), hexc('#2E86C8'))
        # ocean as AC: waves + arrows of heat being spread
        for k in range(6):
            y = 1000 + k * 140
            cr.set_source_rgba(1, 1, 1, .25); cr.set_line_width(10)
            for x in range(0, W + 1, 20):
                yy = y + math.sin(x * .02 + t * 2 + k) * 20
                (cr.move_to if x == 0 else cr.line_to)(x, yy)
            cr.stroke()
        if t > 66.0:
            a = prog(t, 66.0, 66.5)
            cx, cy = W / 2, 620
            rrect(cr, cx - 300, cy - 120, 600, 240, 30); fill(cr, C['white'], a)
            for k in range(6): rrect(cr, cx - 260, cy - 60 + k * 26, 520, 10, 5); fill(cr, hexc('#C9D1DA'), a)
            for k in range(5):
                ph = (t * .8 + k / 5) % 1
                cr.set_source_rgba(.5, .8, 1, a * (1 - ph)); cr.set_line_width(12)
                cr.move_to(cx - 200 + k * 100, cy + 130 + ph * 200); cr.rel_line_to(0, 60); cr.stroke()
        post(cr, t); return
    xs = W * .5
    # hot half (left)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#F2A23A')); g.add_color_stop_rgb(1, *hexc('#C8501E'))
    cr.rectangle(0, 0, xs, H); cr.set_source(g); cr.fill()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#0B1030')); g.add_color_stop_rgb(1, *hexc('#2E4A80'))
    cr.rectangle(xs, 0, W - xs, H); cr.set_source(g); cr.fill()
    circle(cr, xs / 2, 520, 110, C['sun']); g = cairo.RadialGradient(xs / 2, 520, 100, xs / 2, 520, 300); g.add_color_stop_rgba(0, 1, .9, .4, .5); g.add_color_stop_rgba(1, 1, .9, .4, 0); cr.set_source(g); cr.arc(xs / 2, 520, 300, 0, 7); cr.fill()
    circle(cr, xs + (W - xs) / 2, 520, 90, hexc('#F4F1E8')); circle(cr, xs + (W - xs) / 2 + 35, 500, 80, hexc('#16204A'))
    r = random.Random(3)
    for k in range(20):
        x, y = xs + r.uniform(20, W - xs - 20), r.uniform(200, 1300)
        cr.set_source_rgba(1, 1, 1, .8); cr.set_line_width(4)
        for a in range(3):
            an = a * math.pi / 3; cr.move_to(x - math.cos(an) * 14, y - math.sin(an) * 14); cr.line_to(x + math.cos(an) * 14, y + math.sin(an) * 14); cr.stroke()
    cr.rectangle(0, 1250, xs, 670); fill(cr, hexc('#D9A55A')); cr.rectangle(xs, 1250, W - xs, 670); fill(cr, hexc('#DCE6F0'))
    hot = prog(t, 74.0, 75.5); cold = prog(t, 76.0, 77.5)
    thermo(cr, xs / 2, 1050, .45 + .5 * hot, C['red'])
    thermo(cr, xs + (W - xs) / 2, 1050, .45 - .4 * cold, hexc('#3B82D6'))
    text_center(cr, '+50°C', xs / 2, 1180, 70, C['white'], stroke=C['dark'], sw=10, alpha=hot)
    text_center(cr, '-30°C', xs + (W - xs) / 2, 1180, 70, C['white'], stroke=C['dark'], sw=10, alpha=cold)
    cr.rectangle(xs - 4, 0, 8, H); fill(cr, C['white'])
    post(cr, t)

def fish(cr, x, y, s, col, a=1.0, flip=1):
    cr.save(); cr.translate(x, y); cr.scale(s * flip, s)
    cr.move_to(-60, 0); cr.curve_to(-30, -40, 40, -40, 60, 0); cr.curve_to(40, 40, -30, 40, -60, 0); cr.close_path(); fill(cr, col, a)
    cr.move_to(-55, 0); cr.line_to(-95, -30); cr.line_to(-95, 30); cr.close_path(); fill(cr, col, a)
    circle(cr, 35, -8, 7, C['dark'], a); cr.restore()

def whale(cr, x, y, s, col, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-200, 0); cr.curve_to(-150, -110, 150, -120, 230, -10); cr.curve_to(200, 70, -100, 90, -200, 0); cr.close_path(); fill(cr, col, a)
    cr.move_to(-190, -5); cr.line_to(-300, -80); cr.line_to(-270, 0); cr.line_to(-300, 70); cr.close_path(); fill(cr, col, a)
    circle(cr, 170, -30, 9, C['dark'], a); cr.restore()

def sea_life(cr, t):
    gone = prog(t, 87.4, 89.6)
    sky(cr, mix(hexc('#0F6FA8'), hexc('#5A4E42'), gone), mix(hexc('#06304A'), hexc('#2E261E'), gone))
    for k in range(7):
        x = W / 2 + (k - 3) * 160
        h = 220 + (k % 3) * 80
        col = mix([C['pink'], C['orange'], hexc('#B37CFF')][k % 3], hexc('#DDD8CE'), gone)
        for b in range(3):
            cr.set_source_rgba(*col, 1); cr.set_line_width(26); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(x, 1900); cr.curve_to(x + (b - 1) * 40, 1900 - h * .5, x + (b - 1) * 90, 1900 - h * .8, x + (b - 1) * 70 + math.sin(t + k) * 10 * (1 - gone), 1900 - h); cr.stroke()
    a = 1 - gone
    whale(cr, (t * 60) % (W + 800) - 400, 700, 1.4, hexc('#3E5C80'), a)
    for k in range(9):
        fx = (k * 170 + t * (90 + k * 9)) % (W + 300) - 150
        fish(cr, fx, 1050 + (k % 4) * 110 + math.sin(t * 2 + k) * 20, .9, [C['yellow'], C['orange'], hexc('#7FD3FF')][k % 3], a)
    if 81.5 < t < 84.4:
        aa = prog(t, 81.5, 81.9) * (1 - prog(t, 84.0, 84.4))
        circle(cr, W / 2, 520, 200, C['white'], aa); circle(cr, W / 2, 520, 160, hexc('#E8E4DC'), aa)
        fish(cr, W / 2, 520, 1.3, C['orange'], aa)
    post(cr, t)

def globe_dry(cr, t, mars):
    space(cr, t)
    tint = (1 + .35 * mars, 1 - .25 * mars, 1 - .45 * mars)
    R = keys(t, [(90.1, 380), (97.7, 440)])
    draw_globe(cr, W / 2, 960, R, lon0=(t * 18) % 360, tilt=.35, clouds=.85 * (1 - mars), tint=tint, atmo=1 - .7 * mars)
    post(cr, t)

def calm_sea(cr, t):
    sky(cr, hexc('#FFB36B'), hexc('#FFE3B0'))
    circle(cr, W / 2, 900, 150, hexc('#FFF2C2'))
    back_ = ease(prog(t, 97.8, 100))
    cr.rectangle(0, 1000, W, 920); fill(cr, SEABED)
    lvl = 1000 + 920 * (1 - back_)
    g = cairo.LinearGradient(0, lvl, 0, H); g.add_color_stop_rgb(0, *SEA); g.add_color_stop_rgb(1, *SEA2)
    cr.rectangle(0, lvl, W, H); cr.set_source(g); cr.fill()
    cr.set_source_rgba(1, 1, 1, .4); cr.set_line_width(8)
    for k in range(5):
        y = lvl + 40 + k * 120
        for x in range(0, W + 1, 20):
            (cr.move_to if x == 0 else cr.line_to)(x, y + math.sin(x * .02 + t * 2 + k) * 14)
        cr.stroke()
    if t > 102.6:
        heart(cr, W / 2, 620 - 20 * math.sin(t * 3), 3 * back(prog(t, 102.6, 103.0)))
    post(cr, t, warm=.15)

# ---------------- scenes ----------------
def s1(cr, t): beach(cr, t, 1 - ease(prog(t, 1.6, 4.9)))
def s2(cr, t):
    if t < 13.3:
        space(cr, t)
        dry = ease(prog(t, 9.7, 12.2))
        R = keys(t, [(5.9, 300), (13.3, 460)])
        draw_globe(cr, W / 2, 960, R, lon0=(t * 18) % 360, tilt=.35, clouds=.85 * (1 - dry), tint=(1 + .15 * dry, 1 - .05 * dry, 1 - .4 * dry))
        if t < 9.0:
            x, y = W / 2, 960
            for k in range(3):
                ph = (t * .8 + k / 3) % 1
                cr.set_source_rgba(1, 1, 1, .5 * (1 - ph)); cr.set_line_width(6); cr.arc(x, y, R * (1 + ph * .4), 0, 7); cr.stroke()
        post(cr, t); return
    sky(cr, hexc('#9CCBEA'), hexc('#EAF4FA'))
    iso = IsoR(cr, (t - 13.3) * 1.2, 2, 0, 46, oy=.5, light=(1.5, .55), shadow=.4)
    iso.ground(SEABED)
    r = random.Random(2)
    for k in range(60):
        x, y = r.uniform(-14, 24), r.uniform(-14, 16); w = r.uniform(1, 3); h = r.uniform(.5, 4)
        iso.box(x, y, 0, w, w, h * ease(prog(t, 13.4 + k * .03, 14.4 + k * .03)) + .01, r.choice([SEABED2, hexc('#9E8262'), hexc('#7A5E44')]))
    iso.draw(); post(cr, t)
def s3(cr, t): depth_profile(cr, t)
def s4(cr, t): salt_plain(cr, t)
def s5(cr, t): plankton(cr, t)
def s6(cr, t): rain_scene(cr, t)
def s7(cr, t): climate(cr, t)
def s8(cr, t): sea_life(cr, t)
def s9(cr, t): globe_dry(cr, t, ease(prog(t, 92.5, 95.5)))
def s10(cr, t): calm_sea(cr, t)
def s11(cr, t):
    globe_dry(cr, t, 1.0)

SCENES = [(0, 5.9, s1), (5.9, 18.3, s2), (18.3, 26.4, s3), (26.4, 38.9, s4), (38.9, 51.1, s5), (51.1, 62.6, s6),
          (62.6, 80.4, s7), (80.4, 90.1, s8), (90.1, 97.7, s9), (97.7, 104.2, s10), (104.2, 999, s11)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    title(cr, t, 4.2, 5.9, 'NEM UMA GOTA', y=330)
    counter(cr, t, 11.6, 13.3, '70%', 'DO PLANETA')
    pill(cr, t, 18.8, 24.4, 'FOSSA DAS MARIANAS', W / 2, 330, SEA)
    title(cr, t, 24.6, 26.4, 'MAIS FUNDO QUE O EVEREST', y=330, size=90)
    title(cr, t, 28.2, 30.4, 'SAL', y=330, col=C['white'])
    pill(cr, t, 34.6, 38.8, 'DEZENAS DE METROS DE SAL', W / 2, 330, Y)
    counter(cr, t, 41.7, 47.3, 'METADE', 'DO OXIGÊNIO VEM DO MAR')
    title(cr, t, 47.3, 50.9, 'FITOPLÂNCTON', y=330, col=G)
    pill(cr, t, 52.0, 57.2, 'A CHUVA VEM DO MAR', W / 2, 330, C['water'])
    title(cr, t, 58.5, 62.5, 'TUDO SECA', y=330, col=R_)
    title(cr, t, 64.5, 66.0, 'CLIMA DESCONTROLADO', y=330, size=96, col=R_)
    pill(cr, t, 67.5, 72.5, 'AR-CONDICIONADO GIGANTE', W / 2, 330, C['water'])
    pill(cr, t, 74.2, 79.9, 'DIAS FERVENDO, NOITES CONGELANDO', W / 2, 330, R_, size=40)
    counter(cr, t, 81.6, 84.4, 'BILHÕES', 'DEPENDEM DE PEIXE')
    title(cr, t, 87.4, 90.0, 'VIDA MARINHA: FIM', y=330, col=R_)
    title(cr, t, 93.5, 97.6, 'IGUAL A MARTE', y=330, col=hexc('#FF7A4A'))
    title(cr, t, 102.6, 104.2, 'TUDO DEPENDE DELE', y=330, col=G)
    if t >= 104.3:
        title(cr, t, 104.3, 999, 'VOCÊ MORARIA', y=380, size=100, tilt=0, col=C['white'])
        title(cr, max(t, 104.6), 104.6, 999, 'NO FUNDO DO MAR?', y=530, size=110, tilt=-.06)
        if t > 107.0: title(cr, t, 107.0, 999, 'COMENTA 👇'.replace(' 👇', ''), y=1700, size=110, tilt=0, col=C['white'])
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
