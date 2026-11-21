import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
from scenes import heart, stars

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 112.43
END = DUR + 1.6

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

NIGHT_TOP, NIGHT_BOT = hexc('#0B1030'), hexc('#1E2A5A')
WOOD, WOOD2 = hexc('#B07A4A'), hexc('#8A5A35')
SHEET, PILLOW, BLANK = hexc('#F4F1EA'), hexc('#FFFFFF'), hexc('#3D6FD1')
FLOOR = hexc('#C9A27A')
WALL = hexc('#5B6B9A')
PINK, PINK2 = hexc('#F2A0B0'), hexc('#D97A90')

# ---------------- reusable bits ----------------
def bedroom(iso, t, lamp=1.0, wall=None, sleeper=None, stand=None):
    """sleeper: dict(z) person lying; stand: dict(x,y,expr) standing person"""
    wall = wall or WALL
    iso.ground(FLOOR)
    iso.box(-4, -4.4, 0, 12, .4, 4.2, wall, key=-20)
    iso.box(-4.4, -4, 0, .4, 12, 4.2, shade(wall, .85), key=-20,
            deco=lambda i, *b: (i.frect(b, 'y', .38, .35, .62, .75, hexc('#0E1638')),
                                i.frect(b, 'y', .40, .37, .60, .73, hexc('#1C2A66'))))
    # rug
    iso.quad(-1.5, 1.5, 4, 3, hexc('#E0645A'), z=.01)
    # bed
    iso.box(-3.6, -3.6, 0, 3.0, 4.6, .9, WOOD)
    iso.box(-3.6, -3.9, 0, 3.0, .3, 2.0, WOOD2)
    iso.box(-3.5, -3.5, .9, 2.8, 4.4, .35, SHEET)
    iso.box(-3.3, -3.4, 1.25, 2.4, 1.0, .35, PILLOW)
    if sleeper is not None:
        z = 1.25 + sleeper.get('z', 0)
        iso.box(-2.55, -3.15, z + .15, .8, .75, .6, C['skin'], key=-1.2, top=C['hair'],
                deco=lambda i, *b: (i.frect(b, 'x', .0, .7, 1.0, 1.0, C['hair'], edge=0), i.frect(b, 'x', .25, .35, .4, .42, C['dark'], edge=0), i.frect(b, 'x', .6, .35, .75, .42, C['dark'], edge=0)))
    iso.box(-3.5, -2.1 + (0 if sleeper else 1.8), 1.25, 2.8, 2.8 - (0 if sleeper else 1.6), .4 if sleeper else .15, BLANK, key=-.9)
    # nightstand + clock + lamp
    iso.box(-3.6, 1.3, 0, 1.0, 1.0, 1.1, WOOD2)
    iso.box(-3.4, 1.5, 1.1, .5, .3, .35, hexc('#22262E'),
            deco=lambda i, *b: i.frect(b, 'x', .1, .2, .9, .8, hexc('#FF4040'), glow=True))
    iso.box(-3.4, 2.0, 1.1, .3, .3, .6, hexc('#DDDDDD'))
    iso.box(-3.55, 1.85, 1.7, .6, .6, .45, hexc('#FFE7A8') if lamp > .5 else hexc('#9A927A'))
    if stand:
        person(iso, stand['x'], stand['y'], crouch=stand.get('crouch', 0), arms_up=stand.get('arms', 0), jacket=hexc('#3D6FD1'), s=1.3)

def lamp_glow(cr, iso, a):
    x, y = iso.P(-3.25, 2.15, 1.9)
    g = cairo.RadialGradient(x, y, 10, x, y, 650)
    g.add_color_stop_rgba(0, 1, .85, .5, .55 * a); g.add_color_stop_rgba(1, 1, .8, .4, 0)
    cr.set_source(g); cr.paint()

def zzz(cr, x, y, t, a=1.0):
    for k in range(3):
        ph = (t * .5 + k / 3) % 1
        text_center(cr, 'Z', x + ph * 90 + math.sin(ph * 6) * 15, y - ph * 220, 50 + ph * 60, C['white'], stroke=C['dark'], sw=8, alpha=a * (1 - ph) * min(1, ph * 5))

def night_bg(cr, t):
    sky(cr, NIGHT_TOP, NIGHT_BOT); stars(cr, a=.8)

def eyelids(cr, cx, by, s, close):
    """draw eyelids over a front_char face (close 0..1)"""
    if close <= 0: return
    u = s / 10.0; ey = by - 8.0 * u
    for ex in (-.85, .85):
        x = cx + ex * u
        cr.save(); cr.rectangle(x - .55 * u, ey - .55 * u, 1.1 * u, 1.1 * u * close); cr.clip()
        circle(cr, x, ey, .5 * u, shade(C['skin'], .92)); cr.restore()
        cr.set_source_rgb(*shade(C['skin'], .45)); cr.set_line_width(.14 * u)
        yy = ey - .5 * u + 1.0 * u * close
        cr.move_to(x - .45 * u, yy); cr.line_to(x + .45 * u, yy); cr.stroke()

def bags(cr, cx, by, s, a):
    u = s / 10.0; ey = by - 8.0 * u
    for ex in (-.85, .85):
        cr.save(); cr.translate(cx + ex * u, ey + .55 * u); cr.scale(1, .45)
        circle(cr, 0, 0, .45 * u, hexc('#7A5A8A'), .55 * a); cr.restore()

def clock_face(cr, x, y, R, hours, glow=0.0):
    circle(cr, x + 10, y + 14, R, (0, 0, 0), .3)
    circle(cr, x, y, R, C['dark']); circle(cr, x, y, R * .9, C['white'])
    for k in range(12):
        a = k / 12 * 2 * math.pi
        cr.set_source_rgb(*C['dark']); cr.set_line_width(10 if k % 3 == 0 else 5)
        cr.move_to(x + math.sin(a) * R * .72, y - math.cos(a) * R * .72); cr.line_to(x + math.sin(a) * R * .82, y - math.cos(a) * R * .82); cr.stroke()
    ah = hours / 12 * 2 * math.pi; am = hours * 2 * math.pi
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(22); cr.move_to(x, y); cr.line_to(x + math.sin(ah) * R * .45, y - math.cos(ah) * R * .45); cr.stroke()
    cr.set_source_rgb(*C['red']); cr.set_line_width(12); cr.move_to(x, y); cr.line_to(x + math.sin(am) * R * .7, y - math.cos(am) * R * .7); cr.stroke()
    circle(cr, x, y, 20, C['dark'])

def road_scene(cr, t, t0, weave=0.0, night=0.0, cam_speed=6.0):
    """car driving along x with optional weaving"""
    if night > 0: sky(cr, mix(C['sky'], NIGHT_TOP, night), mix(C['sky2'], NIGHT_BOT, night))
    else: sky(cr)
    cx = (t - t0) * cam_speed
    iso = IsoR(cr, cx + 1, 1, 0, 70, oy=.58, light=(1.4, .5), shadow=.35)
    iso.ground(mix(C['grass'], hexc('#1E3A28'), night))
    iso.quad(cx - 30, -1.5, 60, 4, C['road'], z=.01)
    for k in range(int(cx) - 16, int(cx) + 18, 3):
        iso.quad(k, .4, 1.4, .2, C['line'], z=.02)
    r = random.Random(3)
    for k in range(int(cx / 4) - 6, int(cx / 4) + 8):
        rr = random.Random(k)
        tree(iso, k * 4 + rr.uniform(0, 2), -4 - rr.uniform(0, 3), s=rr.uniform(.8, 1.3))
        if rr.random() < .6: tree(iso, k * 4 + rr.uniform(0, 2), 4.5 + rr.uniform(0, 3), s=rr.uniform(.8, 1.2))
    wy = math.sin((t - t0) * 2.2) * 1.3 * weave + math.sin((t - t0) * 5.1) * .3 * weave
    car(iso, cx + 1, .9 + wy, C['red'], along='x')
    iso.draw(night=night * .8)
    if night > .3:
        x, y = iso.P(cx + 3.4, 1.4 + wy, .5)
        cr.move_to(x, y); cr.line_to(x + 600, y + 260); cr.line_to(x + 700, y + 80); cr.close_path()
        g = cairo.LinearGradient(x, y, x + 650, y + 170); g.add_color_stop_rgba(0, 1, .95, .7, .45); g.add_color_stop_rgba(1, 1, .95, .7, 0)
        cr.set_source(g); cr.fill()
    return iso

def brain(cr, x, y, R, grey=0.0, glow=0.0):
    col = mix(PINK, hexc('#9A8E92'), grey); col2 = mix(PINK2, hexc('#776B70'), grey)
    if glow:
        g = cairo.RadialGradient(x, y, R * .5, x, y, R * 1.6); g.add_color_stop_rgba(0, .5, .8, 1, .45 * glow); g.add_color_stop_rgba(1, .5, .8, 1, 0)
        cr.set_source(g); cr.paint()
    cr.save(); cr.translate(x, y); cr.scale(1, .78)
    circle(cr, 10, 18, R, (0, 0, 0), .25)
    circle(cr, 0, 0, R, col)
    cr.set_source_rgb(*col2); cr.set_line_width(R * .06); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    r = random.Random(7)
    for k in range(16):
        a = r.uniform(0, 6.28); d = r.uniform(.15, .75) * R
        px, py = math.cos(a) * d, math.sin(a) * d
        cr.move_to(px, py)
        cr.curve_to(px + r.uniform(-.3, .3) * R, py + r.uniform(-.3, .3) * R, px + r.uniform(-.3, .3) * R, py + r.uniform(-.3, .3) * R, px + r.uniform(-.25, .25) * R, py + r.uniform(-.25, .25) * R)
        cr.stroke()
    cr.move_to(0, -R * .95); cr.curve_to(-R * .1, -R * .3, R * .1, R * .3, 0, R * .95); cr.set_line_width(R * .05); cr.stroke()
    cr.restore()

def debris(cr, x, y, R, t, amount, seed=2):
    r = random.Random(seed)
    for k in range(70):
        a = r.uniform(0, 6.28); d = r.uniform(.1, .85) * R
        if r.random() > amount: continue
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * .75
        s = r.uniform(8, 22)
        circle(cr, px, py, s, hexc('#4E4A42'), .85); circle(cr, px - s * .3, py - s * .3, s * .35, hexc('#7A746A'), .8)

def rat(cr, x, y, s, t, alive=1.0):
    col = mix(hexc('#E8E4DE'), hexc('#B8B2AA'), 1 - alive)
    bob = math.sin(t * 10) * 4 * alive
    cr.save(); cr.translate(x, y + bob); cr.scale(s, s)
    cr.set_source_rgb(*hexc('#F2A0B0')); cr.set_line_width(6); cr.move_to(-60, 10)
    cr.curve_to(-120, 0, -130, -40, -170 + math.sin(t * 6) * 10 * alive, -30); cr.stroke()
    cr.save(); cr.scale(1.4, 1); circle(cr, 0, 0, 50, col); cr.restore()
    circle(cr, 62, -10, 32, col)
    circle(cr, 50, -42, 16, hexc('#F2A0B0')); circle(cr, 50, -42, 10, hexc('#E07A90'))
    circle(cr, 94, -6, 7, hexc('#E07A90'))
    if alive > .5: circle(cr, 72, -18, 6, C['dark'])
    else:
        cr.set_source_rgb(*C['dark']); cr.set_line_width(4)
        cr.move_to(66, -24); cr.line_to(78, -12); cr.move_to(78, -24); cr.line_to(66, -12); cr.stroke()
    cr.restore()

def cage(cr, x, y, w, h):
    rrect(cr, x - w / 2, y + h / 2 - 30, w, 40, 10); fill(cr, hexc('#5E6670'))
    cr.set_source_rgba(.85, .88, .92, .9); cr.set_line_width(6)
    for k in range(13):
        xx = x - w / 2 + 20 + k * (w - 40) / 12
        cr.move_to(xx, y - h / 2 + 30); cr.line_to(xx, y + h / 2 - 30); cr.stroke()
    rrect(cr, x - w / 2, y - h / 2, w, 40, 14); fill(cr, hexc('#8D96A3'))

def dna(cr, x, y, h, t, a=1.0, red=0.0):
    n = 26
    pts = []
    for k in range(n):
        yy = y - h / 2 + k * h / (n - 1); ph = k * .5 + t * 2.4
        x1 = x + math.sin(ph) * 150; x2 = x - math.sin(ph) * 150
        z = math.cos(ph)
        pts.append((yy, x1, x2, z))
        cr.set_source_rgba(*mix(hexc('#FFFFFF'), C['red'], red if k in (11, 12, 13) else 0), .6 * a); cr.set_line_width(10)
        cr.move_to(x1, yy); cr.line_to(x2, yy); cr.stroke()
    for side in (1, 2):
        for yy, x1, x2, z in pts:
            px = x1 if side == 1 else x2; zz = z if side == 1 else -z
            col = hexc('#4FB3FF') if side == 1 else hexc('#B37CFF')
            circle(cr, px, yy, 20 + 6 * zz, shade(col, .8 + .25 * zz), a)

def shield(cr, x, y, R, crack=0.0, a=1.0):
    cr.save(); cr.translate(x, y)
    cr.move_to(0, -R); cr.curve_to(R * .7, -R * .8, R * .9, -R * .7, R * .9, -R * .55)
    cr.curve_to(R * .9, R * .2, R * .4, R * .7, 0, R); cr.curve_to(-R * .4, R * .7, -R * .9, R * .2, -R * .9, -R * .55)
    cr.curve_to(-R * .9, -R * .7, -R * .7, -R * .8, 0, -R); cr.close_path()
    cr.set_source_rgba(*mix(hexc('#3CC46A'), hexc('#777777'), crack), a); cr.fill_preserve()
    cr.set_source_rgba(1, 1, 1, .8 * a); cr.set_line_width(14); cr.stroke()
    if crack > 0:
        cr.set_source_rgba(*C['dark'], a); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        r = random.Random(3)
        for k in range(int(1 + crack * 5)):
            px, py = r.uniform(-.2, .2) * R, -R * .8
            cr.move_to(px, py)
            for s in range(5):
                px += r.uniform(-.25, .25) * R; py += R * .32 * crack
                cr.line_to(px, py)
            cr.stroke()
    cr.restore()

def ecg(cr, t, y, col, amp=1.0, bpm=1.2, irregular=0.0):
    cr.set_source_rgba(*col, .9); cr.set_line_width(9); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for i in range(0, W + 1, 6):
        ph = (i / 360 - t * bpm) % 1
        v = 0
        if .45 < ph < .5: v = -(ph - .45) * 20 * 160
        elif .5 <= ph < .55: v = (-1 + (ph - .5) * 40) * 160
        elif .55 <= ph < .6: v = (1 - (ph - .55) * 20) * 60
        v *= amp * (1 + irregular * math.sin(i * .05 + t * 7))
        if i == 0: cr.move_to(i, y + v)
        else: cr.line_to(i, y + v)
    cr.stroke()

def calendar(cr, x, y, s, day, flip):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rrect(cr, -190, -230, 380, 460, 30); fill(cr, (0, 0, 0), .3)
    rrect(cr, -200, -240, 400, 460, 30); fill(cr, C['white'])
    rrect(cr, -200, -240, 400, 120, 30); fill(cr, C['red'])
    cr.rectangle(-200, -160, 400, 40); fill(cr, C['red'])
    text_center(cr, 'DIA', 0, -185, 64, C['white'])
    text_center(cr, str(day), 0, 60, 230, C['dark'])
    if flip > 0:
        cr.save(); cr.translate(0, -120); cr.scale(1, max(.02, 1 - flip))
        rrect(cr, -200, 0, 400, 340, 30); fill(cr, shade(C['white'], .9 - .3 * flip))
        cr.restore()
    for xx in (-110, 110): rrect(cr, xx - 14, -270, 28, 70, 14); fill(cr, C['dark'])
    cr.restore()

def sepia(cr, a):
    cr.save(); cr.set_operator(cairo.OPERATOR_SOFT_LIGHT); cr.set_source_rgba(.75, .55, .3, a); cr.paint(); cr.restore()
    cr.set_source_rgba(.4, .3, .15, .18 * a); cr.paint()

def office_bg(cr, t, tint=None):
    sky(cr, hexc('#DCE6F2'), hexc('#B9C8DC'))
    for k in range(5):
        x = 80 + k * 230
        rrect(cr, x, 260, 160, 420, 12); fill(cr, hexc('#A9BAD2'))
        for j in range(6):
            rrect(cr, x + 20, 290 + j * 62, 120, 36, 6); fill(cr, hexc('#E8EEF7') if (k + j + int(t)) % 4 else hexc('#FFE7A8'))
    cr.rectangle(0, 1180, W, 740); fill(cr, hexc('#8A6B4E'))
    rrect(cr, 120, 1080, 840, 110, 18); fill(cr, hexc('#6E5038'))

# ---------------- scenes ----------------
T_DORM = wt('dormir'); T_OITO = wt('oito'); T_OLHA = wt('olha')
def s1(cr, t):
    night_bg(cr, t)
    S = keys(t, [(0, 105), (T_DORM + .3, 120), (8.2, 135)])
    iso = IsoR(cr, -1.6, -.8, 1, S, oy=.6, light=(1.3, .7), shadow=.35)
    up = t >= T_DORM + .2
    if not up:
        bedroom(iso, t, sleeper={'z': 0})
    else:
        p = eout(prog(t, T_DORM + .2, T_DORM + .7))
        bedroom(iso, t, stand={'x': .2 + 1.2 * p, 'y': 2.2, 'arms': 1 if t > T_OITO else 0})
    iso.draw(night=.55)
    lamp_glow(cr, iso, 1)
    if not up:
        x, y = iso.P(-2.2, -2.8, 2.4); zzz(cr, x, y, t)
    else:
        if T_OITO <= t < T_OLHA:
            for k in range(8):
                a = k / 8 * 6.28 + t; x, y = iso.P(-.6, .9, 2.2)
                circle(cr, x + math.cos(a) * 170, y - 80 + math.sin(a) * 60, 10, C['yellow'], .8)
    if t >= T_OLHA:
        d = prog(t, T_OLHA, 8.2)
        cr.set_source_rgba(0, 0, 0, .5 * d); cr.paint()
    post(cr, t)

T_EST = wt('estudos'); T_REF = wt('reflexos')
def s2(cr, t):
    if t < T_EST:
        # day/night cycling with spinning clock
        hrs = 24 * ease(prog(t, 8.3, T_EST - .2))
        day = .5 + .5 * math.cos(hrs / 24 * 2 * math.pi + math.pi)
        sky(cr, mix(NIGHT_TOP, C['sky'], day), mix(NIGHT_BOT, C['sky2'], day))
        sa = hrs / 24 * 2 * math.pi
        sx, sy = W / 2 + math.sin(sa + math.pi) * 520, 1250 + math.cos(sa + math.pi) * 620
        circle(cr, sx, sy, 80, C['sun'])
        mx, my = W / 2 - math.sin(sa + math.pi) * 520, 1250 - math.cos(sa + math.pi) * 620
        circle(cr, mx, my, 60, hexc('#F4F1E8')); circle(cr, mx + 22, my - 12, 52, mix(NIGHT_TOP, C['sky'], day))
        cr.rectangle(0, 1250, W, 670); fill(cr, mix(hexc('#1E3A28'), C['grass'], day))
        clock_face(cr, W / 2, 860, 300 * back(prog(t, 8.2, 8.6)), hrs)
        tired = prog(t, 14, T_EST)
        front_char(cr, W / 2 + 300, 1850, 360, expr='sad' if tired > .5 else 'smile', t=t)
        eyelids(cr, W / 2 + 300, 1850, 360, .25 + .35 * tired)
        post(cr, t); return
    weave = ease(prog(t, T_REF - .5, T_REF + .8))
    road_scene(cr, t, T_EST, weave=weave)
    if t > T_REF:
        # wobble/double-vision
        a = .25 * prog(t, T_REF, T_REF + .5)
        cr.save(); cr.translate(14 * math.sin(t * 3), 0); cr.set_source_rgba(1, .2, .2, a * .4); cr.paint(); cr.restore()
    post(cr, t)

T_MS = wt('microssonos'); T_DIRIG = wt('dirigindo'); T_PERIGO = wt('perigo')
def blink_black(t, base):
    """microsleep blackout amount"""
    for s in (base, base + 1.9, base + 3.3, base + 4.2):
        if s <= t < s + .45: return min(1, (t - s) / .08, (s + .45 - t) / .1)
    return 0

def s3(cr, t):
    if t < T_DIRIG - .3:
        office_bg(cr, t)
        sway = math.sin(t * 1.3) * .05
        cr.save(); cr.translate(W / 2, 1650); cr.rotate(sway); cr.translate(-W / 2, -1650)
        front_char(cr, W / 2, 1650, 560, expr='sad', t=t)
        nod = 0.0
        for s in (wt('desliga'), wt('desliga') + 1.4, T_MS, T_MS + 1.6, T_MS + 3.0):
            if s <= t < s + .7: nod = max(nod, math.sin((t - s) / .7 * math.pi))
        eyelids(cr, W / 2, 1650, 560, .45 + .55 * nod); bags(cr, W / 2, 1650, 560, 1)
        cr.restore()
        if t > T_MS:
            b = blink_black(t, T_MS + .3)
            cr.set_source_rgba(0, 0, 0, .95 * b); cr.paint()
            if b > .5: text_center(cr, 'OFF', W / 2, 960, 140, hexc('#444444'))
        post(cr, t); return
    road_scene(cr, t, T_DIRIG - .3, weave=.6, night=.85)
    b = blink_black(t, T_PERIGO - .2) if t > T_PERIGO - .3 else 0
    cr.set_source_rgba(0, 0, 0, .97 * b); cr.paint()
    if t > T_PERIGO:
        a = .35 * (.5 + .5 * math.sin(t * 14)) * prog(t, T_PERIGO, T_PERIGO + .3)
        cr.set_source_rgba(1, 0, 0, a); cr.paint()
    post(cr, t)

T_IRR = wt('irritado'); T_ALU = wt('alucinações')
def s4(cr, t):
    if t < T_ALU - .2:
        office_bg(cr, t)
        sh = math.sin(t * 40) * 6 * prog(t, T_IRR, T_IRR + .3)
        front_char(cr, W / 2 + sh, 1650, 560, expr='disgust', t=t)
        bags(cr, W / 2 + sh, 1650, 560, 1)
        if t > T_IRR:
            u = 56; x, y = W / 2 + 140, 1650 - 10.2 * u
            cr.set_source_rgb(*C['red']); cr.set_line_width(12); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            for a in (0, 1.57, 3.14, 4.71):
                cr.move_to(x + math.cos(a + .78) * 18, y + math.sin(a + .78) * 18); cr.line_to(x + math.cos(a + .78) * 48, y + math.sin(a + .78) * 48); cr.stroke()
        if t > wt('esquece'):
            r = random.Random(4)
            for k, ch in enumerate('A?B?C?'):
                ph = (t * .4 + k / 6) % 1
                text_center(cr, ch, W / 2 + r.uniform(-380, 380), 900 - ph * 500, 90, C['white'], stroke=C['dark'], sw=10, alpha=(1 - ph))
        post(cr, t); return
    # hallucinations: dark room with drifting shadow figures and eyes
    sky(cr, hexc('#07070C'), hexc('#14121E'))
    wob = prog(t, T_ALU, T_ALU + 1)
    cr.save()
    for k in range(5):
        x = (k * 260 + t * (40 + k * 12)) % (W + 400) - 200
        y = 1100 + math.sin(t * .8 + k) * 40
        a = .5 + .3 * math.sin(t * 2 + k)
        cr.save(); cr.translate(x, y); cr.scale(1 + .08 * math.sin(t * 3 + k), 1)
        circle(cr, 0, -330, 80, (0, 0, 0), a)
        rrect(cr, -110, -260, 220, 520, 90); fill(cr, (0, 0, 0), a)
        if k % 2 == 0:
            circle(cr, -28, -335, 10, hexc('#FF3B3B'), a); circle(cr, 28, -335, 10, hexc('#FF3B3B'), a)
        cr.restore()
    cr.restore()
    # chromatic wobble
    for k, col in enumerate(((1, .2, .3), (.2, .6, 1))):
        cr.save(); cr.translate(math.sin(t * 5 + k * 2) * 18 * wob, 0)
        cr.set_source_rgba(*col, .06 * wob); cr.paint(); cr.restore()
    # sound waves (voices)
    if t > wt('vozes') - .2:
        a = prog(t, wt('vozes') - .2, wt('vozes') + .2)
        cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for side in (-1, 1):
            for k in range(3):
                ph = (t * 1.4 + k / 3) % 1
                cr.set_source_rgba(1, 1, 1, a * (1 - ph) * .7)
                cr.arc(W / 2 + side * 120, 900, 60 + ph * 260, (-.6 if side > 0 else math.pi - .6), (.6 if side > 0 else math.pi + .6)); cr.stroke()
    post(cr, t, vignette=.75)

T_FAX = wt('faxina'); T_SEM = wt('Sem', 58)
def s5(cr, t):
    sky(cr, hexc('#101A33'), hexc('#1D2E55'))
    R = 330 * back(prog(t, 52.2, 52.7)) * (1 + .03 * math.sin(t * 2))
    x, y = W / 2, 900
    grey = .6 * prog(t, T_SEM, T_SEM + 3)
    brain(cr, x, y, R, grey=grey, glow=(1 - grey) * prog(t, T_FAX - .3, T_FAX + .3))
    # debris amount: starts some, cleaned during faxina, grows after "sem sono"
    amt = keys(t, [(52.2, .35), (T_FAX, .35), (T_SEM - .5, .02), (T_SEM, .02), (62.9, 1.0)])
    debris(cr, x, y, R, t, amt)
    if T_FAX - .3 < t < T_SEM:
        r = random.Random(11)
        for k in range(12):
            ph = (t * .5 + k / 12) % 1; a = r.uniform(0, 6.28) + t * .8
            d = R * (.2 + .7 * ph)
            circle(cr, x + math.cos(a) * d, y + math.sin(a) * d * .75, 16, hexc('#7FD3FF'), .9 * (1 - ph))
        # broom sweep
        bx = x + math.sin(t * 3) * R * .7
        cr.save(); cr.translate(bx, y + R * .5); cr.rotate(math.sin(t * 3) * .4)
        rrect(cr, -8, -260, 16, 260, 8); fill(cr, WOOD)
        cr.move_to(-60, 0); cr.line_to(60, 0); cr.line_to(40, 70); cr.line_to(-40, 70); cr.close_path(); fill(cr, C['yellow'])
        cr.restore()
    post(cr, t)

T_1964 = wt('1964'); T_11 = wt('11', 63); T_FINAL = wt('11', 63) + 5.5
def s6(cr, t):
    sky(cr, hexc('#E9DCC2'), hexc('#CDB48C'))
    cr.rectangle(0, 1300, W, 620); fill(cr, hexc('#8A6B4E'))
    day = 1 + int(min(10, max(0, (t - T_11 + .3) / ((T_FINAL - T_11) / 10)))) if t > T_11 - .3 else 1
    seg = (T_FINAL - T_11) / 10
    flip = ((t - T_11 + .3) % seg) / seg if T_11 - .3 < t < T_FINAL else 0
    cs = back(prog(t, T_1964, T_1964 + .4))
    calendar(cr, W / 2 + 300, 640, .9 * cs, day, ease(flip))
    tired = prog(t, T_11, T_FINAL + 4)
    sway = math.sin(t * 1.7) * .08 * tired
    cr.save(); cr.translate(W / 2 - 200, 1700); cr.rotate(sway); cr.translate(-(W / 2 - 200), -1700)
    front_char(cr, W / 2 - 200, 1700, 600, expr='sad' if tired > .3 else 'O', t=t, jacket=hexc('#6E8B5A'))
    eyelids(cr, W / 2 - 200, 1700, 600, .2 + .6 * tired); bags(cr, W / 2 - 200, 1700, 600, tired)
    cr.restore()
    if t > wt('paranoia') - .2:
        a = prog(t, wt('paranoia') - .2, wt('paranoia') + .2)
        for k in range(3):
            ex, ey = 180 + k * 360, 250 + (k % 2) * 90
            cr.save(); cr.translate(ex, ey); cr.scale(1, .55); circle(cr, 0, 0, 60, C['white'], a); cr.restore()
            circle(cr, ex + math.sin(t * 2 + k) * 20, ey, 22, C['dark'], a)
    sepia(cr, .85)
    # film scratches
    r = random.Random(int(t * 12))
    for k in range(3):
        x = r.uniform(0, W); cr.rectangle(x, 0, 2, H); fill(cr, (1, 1, 1), .25)
    post(cr, t, vignette=.7, grain=.16)

T_RAT = wt('ratos'); T_HUM = wt('humanos'); T_FAT = wt('fatal')
def s7(cr, t):
    if t < T_HUM - .2:
        sky(cr, hexc('#2C3A48'), hexc('#1C2630'))
        cr.rectangle(0, 1250, W, 670); fill(cr, hexc('#3E4C58'))
        g = cairo.RadialGradient(W / 2, 600, 50, W / 2, 600, 900); g.add_color_stop_rgba(0, 1, 1, .95, .35); g.add_color_stop_rgba(1, 1, 1, .95, 0); cr.set_source(g); cr.paint()
        cage(cr, W / 2, 1030, 760 * back(prog(t, 77.3, 77.7)), 520)
        alive = 1 - prog(t, wt('morreram') - .2, wt('morreram') + .6)
        rx = W / 2 + (math.sin(t * 2) * 140 if alive > .5 else 0)
        rat(cr, rx, 1150 if alive > .5 else 1185, 1.8, t, alive)
        # wheel
        cr.set_source_rgba(.4, .45, .5, .9); cr.set_line_width(10); cr.arc(W / 2 + 300, 1080, 130, 0, 7); cr.stroke()
        for k in range(8):
            a = k / 8 * 6.28 + t * 3 * alive
            cr.move_to(W / 2 + 300, 1080); cr.line_to(W / 2 + 300 + math.cos(a) * 130, 1080 + math.sin(a) * 130); cr.stroke()
        if t > T_RAT + .5 and alive > .3:
            for k in range(3):
                ph = (t * .7 + k / 3) % 1
                text_center(cr, '!', rx + 120 + ph * 40, 1000 - ph * 160, 90, C['red'], stroke=C['dark'], sw=8, alpha=1 - ph)
        post(cr, t); return
    sky(cr, hexc('#0D0A1C'), hexc('#1E1440'))
    red = prog(t, T_FAT - .3, T_FAT + .3)
    g = cairo.RadialGradient(W / 2, 950, 50, W / 2, 950, 900); g.add_color_stop_rgba(0, .9, .1, .2, .45 * red); g.add_color_stop_rgba(1, .9, .1, .2, 0); cr.set_source(g); cr.paint()
    dna(cr, W / 2, 950, 1100 * eout(prog(t, T_HUM - .2, T_HUM + .5)), t, red=red)
    post(cr, t)

T_IMU = wt('imunológico'); T_COR = wt('coração'); T_CORPO = wt('corpo', 95)
def s8(cr, t):
    sky(cr, hexc('#140C14'), hexc('#2A1020'))
    if t < T_COR - .1:
        crack = prog(t, T_IMU + .3, T_COR - .2)
        shake = math.sin(t * 50) * 10 * crack
        shield(cr, W / 2 + shake, 900, 340 * back(prog(t, 92.0, 92.5)), crack=crack)
        r = random.Random(5)
        for k in range(14):
            ph = (t * .6 + k / 14) % 1; a = r.uniform(0, 6.28)
            d = 700 - ph * 380
            x, y = W / 2 + math.cos(a) * d, 900 + math.sin(a) * d
            circle(cr, x, y, 26, hexc('#8FD14F'), .9)
            for s in range(6):
                b = s / 6 * 6.28; circle(cr, x + math.cos(b) * 32, y + math.sin(b) * 32, 7, hexc('#6FB13F'), .9)
        post(cr, t); return
    irr = prog(t, T_COR, T_COR + 2)
    beat = (t * (1.3 + 1.2 * irr)) % 1
    pulse = 1 + .18 * math.exp(-beat * 9) + .1 * irr * math.sin(t * 23)
    heart(cr, W / 2, 900, 8.5 * pulse * back(prog(t, T_COR - .1, T_COR + .3)))
    ecg(cr, t, 1300, C['green'] if irr < .5 else C['red'], amp=1, bpm=1.2 + irr, irregular=irr * .6)
    if t > T_CORPO:
        a = prog(t, T_CORPO, T_CORPO + .4) * (.5 + .5 * math.sin(t * 10))
        cr.set_source_rgba(1, 0, 0, .25 * a); cr.paint()
    post(cr, t)

T_ENT = wt('Então'); T_VIVO = wt('vivo')
def s9(cr, t):
    dawn = prog(t, T_VIVO - .8, T_VIVO + 1.2)
    sky(cr, mix(NIGHT_TOP, hexc('#F7B267'), dawn), mix(NIGHT_BOT, hexc('#FDE3B0'), dawn))
    if dawn < .9: stars(cr, a=.8 * (1 - dawn))
    S = keys(t, [(T_ENT - .5, 110), (108.4, 85)])
    iso = IsoR(cr, -1.6, -1.2, 1, S, oy=.6, light=(1.3, .7), shadow=.35)
    bedroom(iso, t, sleeper={'z': 0}, wall=mix(WALL, hexc('#E7B98A'), dawn))
    iso.draw(night=.5 * (1 - dawn))
    lamp_glow(cr, iso, .6 * (1 - dawn) + .2)
    x, y = iso.P(-2.2, -2.8, 2.4); zzz(cr, x, y, t, 1 - dawn)
    if dawn > 0:
        g = cairo.RadialGradient(0, 600, 50, 0, 600, 1500); g.add_color_stop_rgba(0, 1, .85, .5, .5 * dawn); g.add_color_stop_rgba(1, 1, .8, .4, 0)
        cr.set_source(g); cr.paint()
        hx, hy = iso.P(-2.2, -2.6, 3.0)
        heart(cr, hx + 40, hy - 120 - 20 * math.sin(t * 3), 2.2 * back(prog(t, T_VIVO, T_VIVO + .4)))
    post(cr, t, warm=.15 * dawn)

T_CTA = wt('Comenta', 110)
def s10(cr, t):
    night_bg(cr, t)
    clock_face(cr, W / 2, 1000, 280 * back(prog(t, 108.4, 108.8)), (t - 108.4) * 3)
    for k in range(10):
        ph = (t * .3 + k / 10) % 1; a = k / 10 * 6.28
        circle(cr, W / 2 + math.cos(a) * (360 + ph * 200), 1000 + math.sin(a) * (360 + ph * 200), 10, C['yellow'], 1 - ph)
    post(cr, t)

SCENES = [(0, 8.2, s1), (8.2, 22.74, s2), (22.74, 39.1, s3), (39.1, 52.2, s4), (52.2, 63.1, s5), (63.1, 77.4, s6),
          (77.4, 92.2, s7), (92.2, 100.85, s8), (100.85, 108.4, s9), (108.4, 999, s10)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    counter(cr, t, T_OITO, 8.1, '+8 HORAS', 'POR DIA')
    counter(cr, t, wt('24'), T_EST - .2, '24 HORAS', 'ACORDADO')
    pill(cr, t, T_REF, 22.6, 'REFLEXOS DE BÊBADO', W / 2, 330, R_)
    title(cr, t, wt('segundo'), wt('desliga'), 'DIA 2', y=330)
    title(cr, t, T_MS, T_MS + 3.2, 'MICROSSONOS', y=330)
    pill(cr, t, T_PERIGO, 39.0, 'PERIGO AO VOLANTE', W / 2, 330, R_)
    title(cr, t, wt('terceiro'), T_IRR + .3, 'DIA 3', y=330)
    title(cr, t, T_ALU, wt('Sabe') - .3, 'ALUCINAÇÕES', y=330, col=hexc('#FF5A5A'))
    title(cr, t, T_FAX, T_SEM, 'FAXINA CEREBRAL', y=300, col=hexc('#7FD3FF'))
    pill(cr, t, T_SEM, 62.9, 'O LIXO SE ACUMULA', W / 2, 330, R_)
    title(cr, t, T_1964, T_11, '1964', y=300, col=hexc('#FFF2CC'))
    counter(cr, t, T_11, 77.2, '11 DIAS', 'SEM DORMIR (RECORDE)')
    counter(cr, t, wt('duas', 78), T_HUM - .3, '2 A 3 SEMANAS', 'RATOS SEM SONO')
    pill(cr, t, wt('doença'), T_FAT, 'DOENÇA GENÉTICA RARA', W / 2, 330, Y)
    title(cr, t, T_FAT, 92.9, 'SEMPRE FATAL', y=330, col=R_)
    pill(cr, t, T_IMU, T_COR - .1, 'IMUNIDADE DESABA', W / 2, 330, R_)
    pill(cr, t, T_COR, 100.6, 'CORAÇÃO SOFRE', W / 2, 330, R_)
    counter(cr, t, wt('oito', 100), T_VIVO, '8 HORAS', 'DE SONO')
    title(cr, t, T_VIVO, 108.4, 'TE MANTÊM VIVO', y=330, col=G)
    if t >= T_CTA - .1:
        title(cr, t, T_CTA - .1, 999, 'COMENTA', y=420, size=120, tilt=0, col=C['white'])
        title(cr, max(t, T_CTA + .2), T_CTA + .2, 999, 'QUANTO TEMPO?', y=580, size=120, tilt=-.06)
        if t > T_CTA + .6:
            text_center(cr, 'você já ficou sem dormir', W / 2, 720, 60, C['white'], stroke=C['dark'], sw=10, scale=back((t - T_CTA - .6) / .3))
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
