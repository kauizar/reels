import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5'); sys.path.append('/home/claude/vid8')
import cairo
from engine import *
from real import *
from scenes import stars, heart
import scenes8 as v8
from scenes8 import moon_disk

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 98.038
END = DUR + 1.5

def night_land(cr, t, moon_a, dark=0.0, S=48):
    top = mix(hexc('#14204A'), hexc('#020308'), dark); bot = mix(hexc('#2E3E78'), hexc('#05070E'), dark)
    sky(cr, top, bot); stars(cr, a=.5 + .5 * dark)
    if moon_a > 0:
        g = cairo.RadialGradient(780, 380, 60, 780, 380, 420); g.add_color_stop_rgba(0, .9, .9, 1, .35 * moon_a); g.add_color_stop_rgba(1, .9, .9, 1, 0)
        cr.set_source(g); cr.paint()
        moon_disk(cr, 780, 380, 120, rot=.3)
        if moon_a < 1: circle(cr, 780, 380, 130, top, 1 - moon_a)
    iso = IsoR(cr, 3, 3, 0, S, oy=.72, light=(1.4, .5), shadow=.3)
    iso.quad(-5, -5, 16, 16, C['grass'])
    iso.box(-5, -5, -1.2, 16, 16, 1.2, hexc('#6E4A2E'), key=-50, top=C['grass'])
    for k in range(10): tree(iso, -4 + k * 1.4, -3 + (k % 3), s=1.2)
    house(iso, 4, 2, 3, 3, 2.2, lit=True)
    iso.draw(night=.65 + .3 * dark)
    return iso

def owl(cr, x, y, s, t, lost=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1, 1.25); circle(cr, 0, 0, 60, hexc('#8A6A4A')); cr.restore()
    for sx in (-1, 1):
        circle(cr, sx * 24, -20, 22, C['white']); circle(cr, sx * 24 + math.sin(t * 3 + sx) * 8 * lost, -20, 10, C['dark'])
    cr.move_to(-8, 0); cr.line_to(0, 14); cr.line_to(8, 0); cr.close_path(); fill(cr, C['orange'])
    cr.restore()

def tide_diagram(cr, t, moon_gone):
    space(cr, t)
    ex, ey = W / 2, 960
    # sun on left
    g = cairo.RadialGradient(-80, ey, 20, -80, ey, 360); g.add_color_stop_rgba(0, 1, .95, .7, 1); g.add_color_stop_rgba(.3, 1, .85, .4, .6); g.add_color_stop_rgba(1, 1, .7, .3, 0)
    cr.set_source(g); cr.arc(-80, ey, 360, 0, 7); cr.fill()
    mx = W - 150; my = ey - 40
    bulge_lunar = 1 - moon_gone
    stretch_x = 1 + .22 * bulge_lunar + .07  # sun adds a bit
    # water envelope: elongated toward moon (horizontal axis) - solar part toward sun (same axis here)
    cr.save(); cr.translate(ex, ey); cr.scale(stretch_x, 1 - .06 * bulge_lunar - .02)
    circle(cr, 0, 0, 300, hexc('#3B8FE0'), .55); cr.restore()
    draw_globe(cr, ex, ey, 270, lon0=t * 12, tilt=.3, clouds=.6)
    if moon_gone < 1:
        moon_disk(cr, mx, my, 70 * (1 - moon_gone) + .01)
        cr.set_source_rgba(1, 1, 1, .5 * (1 - moon_gone)); cr.set_line_width(6); cr.set_dash([14, 10])
        cr.move_to(ex + 320, ey); cr.line_to(mx - 80, my); cr.stroke(); cr.set_dash([])
    # tide bars
    lv = .3 + .7 * (1 - moon_gone)
    for k, (lbl, v, col) in enumerate((('COM LUA', 1.0, hexc('#3B8FE0')), ('SEM LUA', lv if moon_gone > 0 else 1.0, hexc('#7FD3FF')))):
        x = W / 2 - 200 + k * 400
        rrect(cr, x - 70, 1350, 140, 320, 20); fill(cr, (1, 1, 1), .15)
        h = 300 * (v if k == 1 else 1.0)
        rrect(cr, x - 60, 1660 - h, 120, h, 16); fill(cr, col, .9 if k == 0 or moon_gone > 0 else .3)
        text_center(cr, lbl, x, 1720, 40, C['white'], stroke=C['dark'], sw=6, alpha=1 if (k == 0 or moon_gone > 0) else .3)

def coral_scene(cr, t, chaos):
    sky(cr, hexc('#0E6FA8'), hexc('#04304A'))
    for k in range(9):
        x = 60 + k * 120; h = 220 + (k % 3) * 90
        col = [C['pink'], C['orange'], hexc('#B37CFF')][k % 3]
        cr.set_source_rgb(*col); cr.set_line_width(28); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for b in range(3):
            cr.move_to(x, 1920); cr.curve_to(x + (b - 1) * 30, 1920 - h * .5, x + (b - 1) * 70, 1920 - h * .8, x + (b - 1) * 60, 1920 - h); cr.stroke()
    r = random.Random(4)
    for k in range(120):
        if chaos > .5 and r.random() < .6: continue
        x0 = r.uniform(40, W - 40)
        if chaos < .5:
            ph = ((t * .25) + k / 120) % 1
        else:
            ph = (t * r.uniform(.05, .6) + r.random()) % 1
        y = 1650 - ph * 1300
        circle(cr, x0 + math.sin(t + k) * 20, y, 8, hexc('#FFE7F0'), .85 * (1 - ph))
    # moon clock
    cx, cy = W / 2, 520
    if chaos < 1:
        moon_disk(cr, cx, cy, 90 * (1 - chaos) + .01)
    else:
        circle(cr, cx, cy, 90, hexc('#0E5A8A')); text_center(cr, '?', cx, cy, 120, C['white'])

def tilted_earth(cr, t, ang, R=360, cx=W / 2, cy=980, moon=True, extra=None):
    space(cr, t)
    cr.save(); cr.translate(cx, cy); cr.rotate(ang); cr.translate(-cx, -cy)
    draw_globe(cr, cx, cy, R, lon0=t * 20, tilt=0.0, clouds=.7)
    cr.set_source_rgba(1, 1, 1, .85); cr.set_line_width(8)
    cr.move_to(cx, cy - R - 140); cr.line_to(cx, cy + R + 140); cr.stroke()
    if extra: extra(cr, cx, cy, R)
    cr.restore()
    if moon:
        a = t * .8
        mx, my = cx + math.cos(a) * (R + 300), cy + math.sin(a) * (R + 300) * .3
        moon_disk(cr, mx, my, 55)

def s1(cr, t):
    gone = prog(t, 2.8, 4.2)
    night_land(cr, t, 1 - gone)
    front_char(cr, 260, 1750, 420, expr='shock' if t > 3.5 else 'smile', t=t)
    post(cr, t)

def s2(cr, t):
    dark = ease(prog(t, 6.8, 10.5))
    S = keys(t, [(4.9, 48), (13.8, 42)])
    iso = night_land(cr, t, 0, dark=dark, S=S)
    if t > 13.8:
        r = random.Random(3)
        for k in range(4):
            x, y = 180 + k * 240, 1250 + (k % 2) * 140
            owl(cr, x, y, 1.0 * back(prog(t, 13.8 + k * .15, 14.2 + k * .15)), t, lost=prog(t, 17.0, 17.6))
            if t > 17.3: text_center(cr, '?', x + 60, y - 120, 80, C['yellow'], stroke=C['dark'], sw=8, scale=back(prog(t, 17.3 + k * .1, 17.6 + k * .1)))
    post(cr, t, vignette=.6 + .3 * dark)

def s3(cr, t):
    tide_diagram(cr, t, ease(prog(t, 26.3, 28.5)))
    post(cr, t)

def s4(cr, t):
    coral_scene(cr, t, ease(prog(t, 40.2, 41.4)))
    post(cr, t)

def s5(cr, t):
    tilted_earth(cr, t, .41 + .02 * math.sin(t))
    if t > 52.0:
        a = prog(t, 52.0, 52.5)
        cr.set_source_rgba(*C['yellow'], a); cr.set_line_width(10)
        cr.arc(W / 2, 980, 520, -math.pi / 2, -math.pi / 2 + .41); cr.stroke()
        text_center(cr, '23,5°', W / 2 + 160, 420, 70, C['yellow'], stroke=C['dark'], sw=8, alpha=a)
    if t > 57.0:
        for k, s_ in enumerate(['❄', '✿', '☀', '🍂']):
            pass
    post(cr, t)

def s6(cr, t):
    if t < 65.0:
        wob = .41 + .5 * math.sin((t - 58.8) * 1.6) * ease(prog(t, 59.3, 62.0))
        tilted_earth(cr, t, wob, moon=t < 59.3)
        post(cr, t); return
    if t < 70.3:
        space(cr, t)
        ang = .44 + .6 * math.sin((t - 65) * 1.3)
        cx, cy, R = W / 2, 980, 320
        cr.save(); cr.translate(cx, cy); cr.rotate(ang); cr.translate(-cx, -cy)
        draw_globe(cr, cx, cy, R, lon0=t * 20, tilt=0.0, clouds=0, tint=(1.45, .75, .5), atmo=.3)
        cr.set_source_rgba(1, 1, 1, .85); cr.set_line_width(8); cr.move_to(cx, cy - R - 140); cr.line_to(cx, cy + R + 140); cr.stroke()
        cr.restore()
        text_center(cr, 'MARTE', W / 2, 1460, 70, hexc('#FF9A6A'), stroke=C['dark'], sw=8)
        post(cr, t); return
    def climate(cr_, cx, cy, R):
        p = ease(prog(t, 72.4, 75.8))
        cr_.save(); cr_.arc(cx, cy, R, 0, 7); cr_.clip()
        for sy in (-1, 1):
            g = cairo.RadialGradient(cx, cy + sy * R, 0, cx, cy + sy * R, R * .7)
            g.add_color_stop_rgba(0, 1, .4, .1, .7 * p); g.add_color_stop_rgba(1, 1, .4, .1, 0); cr_.set_source(g); cr_.paint()
        cr_.rectangle(cx - R, cy - R * .22, 2 * R, R * .44); cr_.set_source_rgba(.92, .97, 1, .75 * prog(t, 74.7, 76.0)); cr_.fill()
        cr_.restore()
    ang = .41 + .9 * math.sin((t - 70.3) * .8)
    tilted_earth(cr, t, ang, moon=False, extra=climate)
    if t > 76.3:
        a = prog(t, 76.3, 76.8)
        for k in range(30):
            r = random.Random(k); x, y = r.uniform(0, W), (r.uniform(0, H) + t * 120) % H
            text_center(cr, '*', x, y, 50, C['white'], alpha=.6 * a)
    post(cr, t)

def s7(cr, t):
    space(cr, t)
    brake = 1 - prog(t, 83.4, 84.6)
    spin = t * 25 if brake > .5 else t * 25
    draw_globe(cr, W / 2, 900, 340, lon0=spin, tilt=.3)
    if brake > 0:
        moon_disk(cr, W / 2 + 470, 900, 70 * brake + .01)
        cr.set_source_rgba(1, .5, .3, .6 * brake); cr.set_line_width(10)
        for k in range(3):
            cr.arc_negative(W / 2, 900, 380 + k * 22, -.3, -1.2); cr.stroke()
    # day-length clock
    cx, cy = W / 2, 1560
    rrect(cr, cx - 280, cy - 90, 560, 180, 40); fill(cr, (0, 0, 0), .6)
    hrs = 24.0 if t < 80.5 else (24.0 + min(.002, (t - 80.5) * .0005) if brake > .5 else 24.0)
    txt = '24h 00min' + (' ⬆' if 80.5 < t < 83.4 else '')
    text_center(cr, '1 DIA = 24h', cx, cy, 80, C['white'] if brake > .5 else C['yellow'])
    if 80.5 < t < 83.4:
        text_center(cr, '+2 ms por século', cx, cy + 140, 50, C['white'], stroke=C['dark'], sw=8, alpha=prog(t, 80.6, 81.0))
    if t > 85.6:
        text_center(cr, 'FICA ASSIM', cx, cy + 140, 60, C['yellow'], stroke=C['dark'], sw=8, scale=back(prog(t, 85.6, 86.0)))
    post(cr, t)

def s8(cr, t):
    iso = night_land(cr, t, ease(prog(t, 88.3, 89.3)))
    front_char(cr, 260, 1750, 420, expr='happy', t=t)
    if t > 91.2:
        heart(cr, 780, 620 - 15 * math.sin(t * 3), 2.2 * back(prog(t, 91.2, 91.6)))
    post(cr, t)

def s9(cr, t):
    space(cr, t)
    g = cairo.RadialGradient(W / 2, 1150, 100, W / 2, 1150, 600); g.add_color_stop_rgba(0, .9, .9, 1, .3); g.add_color_stop_rgba(1, .9, .9, 1, 0); cr.set_source(g); cr.paint()
    moon_disk(cr, W / 2, 1150, 300 * back(prog(t, 95.6, 96.0)), rot=t * .05)
    post(cr, t)

SCENES = [(0, 4.9, s1), (4.9, 19.1, s2), (19.1, 32.9, s3), (32.9, 44.8, s4), (44.8, 58.8, s5), (58.8, 79.2, s6),
          (79.2, 88.3, s7), (88.3, 95.6, s8), (95.6, 999, s9)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    title(cr, t, 3.4, 4.9, 'A LUA SUMIU', y=330)
    title(cr, t, 7.5, 9.6, 'ESCURIDÃO', y=330, col=hexc('#9AA8D8'))
    pill(cr, t, 14.0, 19.0, 'ANIMAIS PERDIDOS', W / 2, 330, Y)
    title(cr, t, 21.2, 26.2, 'MARÉS', y=330, col=hexc('#7FD3FF'))
    counter(cr, t, 30.5, 32.8, '1/3', 'DA FORÇA DAS MARÉS')
    pill(cr, t, 37.0, 40.2, 'CORAIS SEGUEM A LUA', W / 2, 330, C['pink'])
    title(cr, t, 40.2, 44.7, 'RELÓGIO QUEBRADO', y=330, col=R_)
    title(cr, t, 49.4, 52.0, 'ESTABILIZADOR', y=330, col=G)
    pill(cr, t, 52.2, 58.7, 'INCLINAÇÃO = ESTAÇÕES', W / 2, 330, Y)
    title(cr, t, 61.6, 65.0, 'A TERRA BALANÇA', y=330, col=R_)
    pill(cr, t, 65.1, 70.2, 'MARTE JÁ PASSOU POR ISSO', W / 2, 330, hexc('#FF7A4A'))
    pill(cr, t, 72.6, 75.2, 'POLOS QUENTES', W / 2, 330, R_)
    pill(cr, t, 75.3, 77.5, 'TRÓPICOS CONGELADOS', W / 2, 330, hexc('#7FD3FF'))
    title(cr, t, 77.5, 79.1, 'ERAS GLACIAIS', y=330, col=hexc('#BFE6FA'))
    title(cr, t, 80.4, 83.3, 'A LUA FREIA A TERRA', y=330, size=96)
    title(cr, t, 90.2, 95.5, 'NOSSA LUA ❤'.replace(' ❤', ''), y=330, col=hexc('#E8E4FF'))
    if t >= 95.6:
        title(cr, t, 95.6, 999, 'VOCÊ SENTIRIA', y=380, size=110, tilt=0, col=C['white'])
        title(cr, max(t, 95.9), 95.9, 999, 'FALTA DELA?', y=540, size=120, tilt=-.06)
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
