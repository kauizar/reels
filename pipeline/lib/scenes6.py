import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
import scenes as v1
from scenes import confetti, PROD
sys.path.append('/home/claude/vid3'); sys.path.append('/home/claude/vid4')
import scenes3 as v3
from scenes3 import arrow, snow_ground, SNOW
import scenes5 as v5
from scenes5 import fireball, flash, smoke_puffs

WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes6.json')))
def merge(first, last, disp, after=0.0):
    i = next(k for k, w in enumerate(WORDS) if w['t0'] >= after and w['w'].strip('.,') == first)
    j = next(k for k in range(i + (1 if first == last else 0), len(WORDS)) if WORDS[k]['w'].strip('.,') == last)
    WORDS[i] = dict(WORDS[i], w=disp, key=True, t1=WORDS[j]['t1']); del WORDS[i + 1:j + 1]
merge('doze', 'quilômetros', '12 km'); merge('vinte', 'anos', '20 anos'); merge('treze', 'mil', '13 mil km')
merge('cem', 'graus', '100 °C'); merge('cinco', 'graus', '5.000 °C'); merge('trinta', 'hora', '30 mil km/h')
merge('quarenta', 'minutos', '40 minutos')

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

LAYERS = [(1.0, hexc('#6B5A4A')), (.985, hexc('#C2502A')), (.55, hexc('#F08A2A')), (.19, hexc('#FFE9A8'))]

# ---------- drawing helpers ----------
def cut_earth(cr, cx, cy, R, t, spin=0.0, tunnel_ang=None, tunnel_glow=0.0, poles=False):
    g = cairo.RadialGradient(cx, cy, R * .95, cx, cy, R * 1.12); g.add_color_stop_rgba(0, .4, .65, 1, .5); g.add_color_stop_rgba(1, .4, .65, 1, 0)
    cr.set_source(g); cr.arc(cx, cy, R * 1.12, 0, 7); cr.fill()
    # surface ring with spin marks
    circle(cr, cx, cy, R, hexc('#3E8E5A'))
    cr.set_line_width(R * .02)
    for k in range(24):
        a = spin + k * math.pi / 12
        cr.set_source_rgb(*(hexc('#2E78B8') if k % 3 else hexc('#5DBB55'))); cr.arc(cx, cy, R * .99, a, a + .18); cr.stroke()
    circle(cr, cx, cy, R * .975, hexc('#6B5A4A'))
    g = cairo.RadialGradient(cx, cy, R * .55, cx, cy, R * .96); g.add_color_stop_rgb(0, *hexc('#F07A2A')); g.add_color_stop_rgb(1, *hexc('#A8361E'))
    cr.set_source(g); cr.arc(cx, cy, R * .955, 0, 7); cr.fill()
    # mantle convection
    cr.set_line_width(R * .03)
    for k in range(10):
        a = t * .15 * (1 if k % 2 else -1) + k * .63
        cr.set_source_rgba(1, .75, .35, .18); cr.arc(cx, cy, R * (.62 + .03 * (k % 5) * 2.5), a, a + .9); cr.stroke()
    g = cairo.RadialGradient(cx, cy, R * .19, cx, cy, R * .55); g.add_color_stop_rgb(0, *hexc('#FFD27A')); g.add_color_stop_rgb(1, *hexc('#F59A2E'))
    cr.set_source(g); cr.arc(cx, cy, R * .55, 0, 7); cr.fill()
    g = cairo.RadialGradient(cx - R * .05, cy - R * .05, 0, cx, cy, R * .2); g.add_color_stop_rgb(0, 1, 1, .95); g.add_color_stop_rgb(1, *hexc('#FFE08A'))
    cr.set_source(g); cr.arc(cx, cy, R * .2, 0, 7); cr.fill()
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, R * .45); g.add_color_stop_rgba(0, 1, .95, .7, .5); g.add_color_stop_rgba(1, 1, .9, .6, 0)
    cr.set_source(g); cr.arc(cx, cy, R * .45, 0, 7); cr.fill()
    if tunnel_ang is not None:
        dx, dy = math.sin(tunnel_ang), -math.cos(tunnel_ang)
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_line_width(R * .05); cr.set_source_rgb(*hexc('#14161C'))
        cr.move_to(cx - dx * R, cy - dy * R); cr.line_to(cx + dx * R, cy + dy * R); cr.stroke()
        cr.set_line_width(R * .012); cr.set_source_rgba(.75, .85, 1, .5 + .4 * tunnel_glow)
        for s in (-1, 1):
            ox, oy = -dy * R * .028 * s, dx * R * .028 * s
            cr.move_to(cx - dx * R + ox, cy - dy * R + oy); cr.line_to(cx + dx * R + ox, cy + dy * R + oy); cr.stroke()
    if poles:
        text_center(cr, 'N', cx, cy - R - 60, 64, C['white'], stroke=C['dark'], sw=8)
        text_center(cr, 'S', cx, cy + R + 60, 64, C['white'], stroke=C['dark'], sw=8)

def capsule(cr, x, y, s, heat=0.0, ang=0.0, face='O'):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    if heat > 0:
        g = cairo.RadialGradient(0, 0, 40, 0, 0, 220); g.add_color_stop_rgba(0, 1, .6, .2, .7 * heat); g.add_color_stop_rgba(1, 1, .4, .1, 0)
        cr.set_source(g); cr.arc(0, 0, 220, 0, 7); cr.fill()
    g = cairo.LinearGradient(-70, 0, 70, 0)
    g.add_color_stop_rgb(0, *hexc('#4A525C')); g.add_color_stop_rgb(.35, *hexc('#D8DEE6')); g.add_color_stop_rgb(.6, *hexc('#9AA3AE')); g.add_color_stop_rgb(1, *hexc('#3A4048'))
    rrect(cr, -70, -130, 140, 260, 70); cr.set_source(g); cr.fill()
    if heat > 0:
        g = cairo.LinearGradient(0, -130, 0, 130); g.add_color_stop_rgba(0, 1, .5, .1, .0); g.add_color_stop_rgba(1, 1, .45, .1, .55 * heat)
        rrect(cr, -70, -130, 140, 260, 70); cr.set_source(g); cr.fill()
    circle(cr, 0, -40, 44, hexc('#2A3F5A'))
    circle(cr, 0, -40, 34, C['skin']); rrect(cr, -36, -82, 72, 26, 10); fill(cr, C['hair'])
    circle(cr, -12, -44, 5, C['dark']); circle(cr, 12, -44, 5, C['dark'])
    if face == 'O': circle(cr, 0, -26, 6, C['dark'])
    else: cr.set_line_width(4); cr.set_source_rgb(*C['dark']); cr.arc(0, -32, 10, .3, math.pi - .3); cr.stroke()
    g = cairo.LinearGradient(-40, -80, 30, 0); g.add_color_stop_rgba(0, 1, 1, 1, .45); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(g); cr.arc(0, -40, 44, 0, 7); cr.fill()
    for yy in (40, 80): cr.rectangle(-70, yy, 140, 6); fill(cr, hexc('#3A4048'))
    cr.restore()

def speed_lines(cr, t, x, y, n=30, length=300, a=.5, up=True, spread=200, seed=2):
    r = random.Random(seed); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(n):
        ph = (t * 3 + k / n) % 1
        lx = x + r.uniform(-spread, spread); ly = y - 600 + ph * 1200 if not up else y + 600 - ph * 1200
        L = r.uniform(.5, 1) * length
        cr.set_line_width(r.uniform(2, 5)); cr.set_source_rgba(1, 1, 1, a * r.uniform(.4, 1))
        cr.move_to(lx, ly); cr.line_to(lx, ly + (L if up else -L)); cr.stroke()

def drill(cr, x, y, s, t, spin=True):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    g = cairo.LinearGradient(-160, 0, 160, 0); g.add_color_stop_rgb(0, *hexc('#8A6A1E')); g.add_color_stop_rgb(.4, *hexc('#F2C13D')); g.add_color_stop_rgb(1, *hexc('#7A5A14'))
    rrect(cr, -160, -420, 320, 360, 30); cr.set_source(g); cr.fill()
    for k in range(4): cr.rectangle(-160, -380 + k * 80, 320, 14); fill(cr, hexc('#3A3020'))
    rrect(cr, -60, -380, 120, 70, 14); fill(cr, hexc('#2A3F5A'))
    g = cairo.LinearGradient(-150, 0, 150, 0); g.add_color_stop_rgb(0, *hexc('#4A525C')); g.add_color_stop_rgb(.5, *hexc('#C8D0DA')); g.add_color_stop_rgb(1, *hexc('#3A4048'))
    cr.move_to(-150, -60); cr.line_to(150, -60); cr.line_to(0, 200); cr.close_path(); cr.set_source(g); cr.fill()
    ph = (t * 4) % 1 if spin else 0
    cr.set_line_width(10); cr.set_source_rgb(*hexc('#2A2F38'))
    for k in range(6):
        yy = -40 + ((k + ph) / 6) * 220; w = 150 * (1 - (yy + 60) / 260)
        cr.move_to(-w, yy); cr.line_to(w, yy + 30); cr.stroke()
    cr.restore()

def can_crush(cr, t, p):
    cx, cy = W / 2, 1050; h = 420 * (1 - .6 * p); w = 240 * (1 + .12 * p)
    g = cairo.LinearGradient(cx - w / 2, 0, cx + w / 2, 0); g.add_color_stop_rgb(0, *hexc('#8A1E1E')); g.add_color_stop_rgb(.35, *hexc('#F24A3A')); g.add_color_stop_rgb(.6, *hexc('#C42E24')); g.add_color_stop_rgb(1, *hexc('#5A1010'))
    cr.move_to(cx - w / 2, cy + 210)
    n = 10
    for k in range(n + 1):
        yy = cy + 210 - h * k / n; dx = (18 * p) * (1 if k % 2 else -1)
        cr.line_to(cx - w / 2 + dx, yy)
    for k in range(n, -1, -1):
        yy = cy + 210 - h * k / n; dx = (18 * p) * (1 if k % 2 else -1)
        cr.line_to(cx + w / 2 - dx, yy)
    cr.close_path(); cr.set_source(g); cr.fill()
    cr.save(); cr.translate(cx, cy + 210 - h); cr.scale(1, .22); circle(cr, 0, 0, w / 2, hexc('#D9DEE6')); cr.restore()
    for k in range(4):
        a = k * math.pi / 2
        x0, y0 = cx + math.cos(a) * 520, cy + math.sin(a) * 520
        arrow(cr, x0, y0, cx + math.cos(a) * (300 + 60 * (1 - p)), cy + math.sin(a) * (300 + 60 * (1 - p)), C['red'], w=22, a=.9)

def descent_bg(cr, depth):
    """vertical slice of Earth layers around a depth in km (0..6371)"""
    sc = .9  # px per km
    def col_at(d):
        if d < 35: return hexc('#6B5A4A')
        if d < 2900: return mix(hexc('#B8401E'), hexc('#F07A2A'), (d - 35) / 2865)
        if d < 5150: return mix(hexc('#F59A2E'), hexc('#FFD27A'), (d - 2900) / 2250)
        return mix(hexc('#FFE08A'), hexc('#FFFDF0'), min(1, (d - 5150) / 1220))
    for y in range(0, H, 16):
        d = depth + (y - H / 2) / sc
        if d < 0: c = hexc('#8FB7E2')
        else: c = col_at(d)
        cr.rectangle(0, y, W, 17); fill(cr, c)

def oscillate(cr, t, t0, period=4.2):
    space(cr, t)
    cx, cy, R = W / 2, 1060, 440
    cut_earth(cr, cx, cy, R, t, tunnel_ang=0, poles=True)
    ph = (t - t0) / period * 2 * math.pi
    y = cy - math.cos(ph) * R * .94
    capsule(cr, cx, y, .32, heat=max(0, 1 - abs(y - cy) / (R * .5)) * .8, face='O')

# ======================= SCENES =======================
def s1(cr, t):
    sky_r(cr, hexc('#5E9FE0'), hexc('#A8CCF0'), hexc('#E2EEF8'))
    dive = ease(prog(t, 4.7, 5.74))
    iso = IsoR(cr, 1, 1, .4 - dive * 2, 95 + dive * 500, oy=.55, light=(1.4, .5), shadow=.28)
    iso.ground(hexc('#6FB45A'))
    r = random.Random(3)
    for k in range(10):
        x, y = r.uniform(-6, 8), r.uniform(-6, 8)
        if abs(x - 1) < 3 and abs(y - 1) < 3: continue
        v1.tree(iso, x, y, 1.0)
    def hole(i):
        pts = [i.P(-.5, -.5, 0), i.P(2.5, -.5, 0), i.P(2.5, 2.5, 0), i.P(-.5, 2.5, 0)]
        i.cr.move_to(*pts[0]); [i.cr.line_to(*p) for p in pts[1:]]; i.cr.close_path(); fill(i.cr, hexc('#0A0A0E'))
        a, b = i.P(-.5, -.5, 0), i.P(2.5, -.5, 0); c2, d2 = i.P(2.5, -.5, -1.2), i.P(-.5, -.5, -1.2)
        i.cr.move_to(*a); i.cr.line_to(*b); i.cr.line_to(*c2); i.cr.line_to(*d2); i.cr.close_path(); fill(i.cr, hexc('#3A2E24'))
        a, b = i.P(-.5, -.5, 0), i.P(-.5, 2.5, 0); c2, d2 = i.P(-.5, 2.5, -1.2), i.P(-.5, -.5, -1.2)
        i.cr.move_to(*a); i.cr.line_to(*b); i.cr.line_to(*c2); i.cr.line_to(*d2); i.cr.close_path(); fill(i.cr, hexc('#4A3A2E'))
    iso.custom(-50, hole)
    jump = prog(t, 4.62, 5.4)
    pz = 1.2 * math.sin(jump * math.pi) - (3 * jump * jump if jump > .5 else 0)
    if t < 5.6: person(iso, 3.2 - jump * 2.2, 1.0 - jump * .2, z=pz, arms_up=1 if jump > 0 else 0, jacket=C['orange'])
    iso.draw()
    if dive > 0: cr.set_source_rgba(0, 0, 0, dive); cr.paint()
    post(cr, t)

def s2(cr, t):
    if t < 18.4:
        space(cr, t)
        z = ease(prog(t, 10.0, 15.0))
        R = 470 * (1 + 30 * (1 - z)) if t > 7.9 else 470
        cy = 1040 + (R - 470) if t > 7.9 else 1040
        cut_earth(cr, W / 2, cy, R, t)
        if t > 7.9:
            top = cy - R
            L = max(2, R * 12 / 6371)
            cr.set_line_width(max(4, R * .004)); cr.set_source_rgb(*C['yellow']); cr.move_to(W / 2, top); cr.line_to(W / 2, top + L); cr.stroke()
            if z < .3:
                cr.save(); cr.translate(W / 2, top); s = 1.0
                cr.set_line_width(8); cr.set_source_rgb(*hexc('#C9CED6'))
                cr.move_to(-60, 0); cr.line_to(0, -260); cr.line_to(60, 0); cr.move_to(-40, -80); cr.line_to(40, -80); cr.move_to(-25, -160); cr.line_to(25, -160); cr.stroke(); cr.restore()
        if t > 15.5:
            a = prog(t, 15.5, 16.0)
            cr.set_line_width(8); cr.set_source_rgba(1, 1, 1, a); cr.set_dash([18, 12])
            cr.move_to(W / 2 - 470, 1040); cr.line_to(W / 2 + 470, 1040); cr.stroke(); cr.set_dash([])
        post(cr, t, grain=.06); return
    space(cr, t)
    cut_earth(cr, W / 2, 1300, 470, t)
    shake = math.sin(t * 50) * 6
    drill(cr, W / 2 + shake, 760 + 60 * ease(prog(t, 18.4, 21.0)), 1.0, t)
    r = random.Random(int(t * 20))
    for k in range(30):
        an = r.uniform(-2.8, -.3); d = r.uniform(20, 260)
        circle(cr, W / 2 + math.cos(an) * d, 840 + 60 * ease(prog(t, 18.4, 21.0)) + math.sin(an) * d * .5, r.uniform(3, 8), (1, r.uniform(.6, .9), .3), .9)
    post(cr, t, grain=.06)

def s3(cr, t):
    if t < 37.8:
        depth = keys(t, [(23.9, 0), (27.6, 60), (31.3, 1800), (34.9, 6000), (37.8, 6371)])
        descent_bg(cr, depth)
        for s in (-1, 1):
            g = cairo.LinearGradient(W / 2 + s * 140, 0, W / 2 + s * 220, 0); g.add_color_stop_rgba(0, 0, 0, 0, .55); g.add_color_stop_rgba(1, 0, 0, 0, 0)
            cr.set_source(g); cr.rectangle(W / 2 + s * 140 - (80 if s < 0 else 0), 0, 80, H); cr.fill()
        cr.rectangle(W / 2 - 140, 0, 280, H); fill(cr, (0.05, .05, .07), .55)
        speed_lines(cr, t, W / 2, 960, n=24, length=260, a=.35, up=True, spread=110)
        capsule(cr, W / 2, 960 + math.sin(t * 6) * 6, .9, heat=clamp(depth / 5000))
        post(cr, t); return
    space(cr, t)
    capsule(cr, W / 2, 1000, 1.8, heat=.9 + .1 * math.sin(t * 8))
    post(cr, t)

def s4(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2A2F38')); g.add_color_stop_rgb(1, *hexc('#0E1014')); cr.set_source(g); cr.paint()
    if t < 47.5:
        can_crush(cr, t, ease(prog(t, 43.2, 46.5)))
    else:
        capsule(cr, W / 2, 1000, 1.5, heat=.6)
        for k in range(8):
            a = k * math.pi / 4; pulse = 30 * math.sin(t * 6)
            arrow(cr, W / 2 + math.cos(a) * (560 + pulse), 1000 + math.sin(a) * (560 + pulse), W / 2 + math.cos(a) * 330, 1000 + math.sin(a) * 330, C['red'], w=18, a=.85)
    post(cr, t)

def s5(cr, t):
    space(cr, t)
    cx, cy, R = W / 2, 960, 470
    cut_earth(cr, cx, cy, R, t, tunnel_ang=0, tunnel_glow=prog(t, 59.0, 61.5))
    fall = prog(t, 52.5, 58.4)
    y = cy - R * .94 + R * .9 * (fall ** 2 if t < 56.6 else (fall ** 2) * (1 - .3 * prog(t, 56.6, 58.4)))
    capsule(cr, cx, y, .3, heat=0)
    if 56.6 < t < 58.8:
        speed_lines(cr, t, cx, y - 60, n=26, length=120, a=.6, up=False, spread=24, seed=4)
    if t > 58.8:
        a = prog(t, 58.8, 59.2)
        for s in (-1, 1):
            arrow(cr, cx + s * 30, cy - R - 20, cx + s * 160, cy - R - 160, hexc('#7FD3FF'), w=12, a=a)
        cr.set_source_rgba(.6, .8, 1, .25 * (1 - prog(t, 59.0, 61.5))); cr.rectangle(cx - 12, cy - R, 24, 2 * R); cr.fill()
    post(cr, t, grain=.06)

def s6(cr, t):
    space(cr, t)
    cx, cy, R = W / 2, 960, 470
    aligned = ease(prog(t, 70.3, 71.5))
    spin = (t - 62.76) * .5 * (1 - aligned)
    ang = (math.pi / 3 + spin) * (1 - aligned)
    cut_earth(cr, cx, cy, R, t, spin=spin, tunnel_ang=ang, poles=aligned > .5)
    if t < 70.3:
        p = prog(t, 65.6, 69.0)
        dx, dy = math.sin(ang), -math.cos(ang)
        sx, sy = cx - dx * R * .94, cy - dy * R * .94
        x = sx + (cx - sx) * p * .6 + 40 * p; y = sy + (cy - sy) * p * .6
        capsule(cr, x, y, .3, ang=ang * .5)
        if t > 68.6:
            r = random.Random(int(t * 25))
            for k in range(16): circle(cr, x + 30 + r.uniform(-20, 40), y + r.uniform(-40, 40), r.uniform(3, 7), (1, .85, .4), .9)
    else:
        capsule(cr, cx, cy - R * .94, .3)
        cr.set_line_width(6); cr.set_dash([16, 12]); cr.set_source_rgba(1, 1, 1, .7 * aligned)
        cr.move_to(cx, cy - R - 120); cr.line_to(cx, cy + R + 120); cr.stroke(); cr.set_dash([])
    post(cr, t, grain=.06)

def s7(cr, t):
    if 80.3 <= t < 82.47:
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#3A4250')); g.add_color_stop_rgb(1, *hexc('#1A1E26')); cr.set_source(g); cr.paint()
        circle(cr, W / 2, 900, 600, hexc('#2A303A'))
        bob = math.sin(t * 2.5) * 40
        front_char(cr, W / 2, 1500 + bob, 1000, 'happy', arm='up', t=t * .3, jacket=C['orange'])
        for k, (ox, oy, c) in enumerate(((-300, 700, C['red']), (320, 820, C['yellow']), (-260, 1180, C['green']))):
            cr.save(); cr.translate(W / 2 + ox + math.sin(t + k) * 20, oy + math.cos(t * 1.3 + k) * 30); cr.rotate(t * .8 + k)
            rrect(cr, -40, -40, 80, 80, 14); fill(cr, c); cr.restore()
        post(cr, t); return
    if t >= 88.77:
        space(cr, t)
        cut_earth(cr, W / 2, 1200, 380, t, tunnel_ang=0, poles=True)
        capsule(cr, W / 2, 1200 + 380 * .94, .25)
        p = prog(t, 88.8, 94.4)
        x = 140 + p * 160
        cr.save(); cr.translate(x, 640); cr.set_source_rgb(*C['white'])
        cr.move_to(-80, 0); cr.line_to(80, 0); cr.line_to(100, -10); cr.line_to(80, 12); cr.line_to(-80, 12); cr.close_path(); cr.fill()
        cr.move_to(-10, 4); cr.line_to(-40, 60); cr.line_to(0, 60); cr.line_to(30, 4); cr.close_path(); cr.fill()
        cr.move_to(-70, 0); cr.line_to(-90, -40); cr.line_to(-60, -40); cr.line_to(-45, 0); cr.close_path(); cr.fill(); cr.restore()
        post(cr, t, grain=.06); return
    space(cr, t)
    cx, cy, R = W / 2, 960, 470
    cut_earth(cr, cx, cy, R, t, tunnel_ang=0, poles=True)
    p = prog(t, 74.66, 88.3)
    y = cy - math.cos(p * math.pi) * R * .94
    v = abs(math.sin(p * math.pi))
    if v > .2: speed_lines(cr, t, cx, y, n=16, length=120 * v, a=.5 * v, up=True, spread=14, seed=7)
    capsule(cr, cx, y, .3, heat=v * .8)
    post(cr, t, grain=.06)

def s8(cr, t):
    cuts = [(wt('Máquina', 94), 'm'), (wt('Cápsula', 95), 'c'), (wt('Vácuo', 96), 'v'), (wt('Polo', 98), 'p')]
    cur = cuts[0][1]
    for t0, k in cuts:
        if t >= t0 - .05: cur = k
    space(cr, t)
    if cur == 'm': drill(cr, W / 2, 1100, 1.4, t)
    elif cur == 'c': capsule(cr, W / 2, 1000, 1.8, heat=.8)
    elif cur == 'v':
        cut_earth(cr, W / 2, 1100, 420, t, tunnel_ang=0, tunnel_glow=1)
        for s in (-1, 1): arrow(cr, W / 2 + s * 30, 660, W / 2 + s * 170, 520, hexc('#7FD3FF'), w=14)
    else:
        draw_globe(cr, W / 2, 1000, 420, lon0=200, tilt=.1, sun=(-.6, -.3, .7), clouds=.6)
        cr.set_line_width(10); cr.set_dash([20, 14]); cr.set_source_rgb(*C['yellow']); cr.move_to(W / 2, 480); cr.line_to(W / 2, 1520); cr.stroke(); cr.set_dash([])
    post(cr, t, grain=.06)

def pole_exit(cr, t, state):
    sky_r(cr, hexc('#9DB8D3'), hexc('#CFDDEA'), hexc('#F1F5F9'), sun=(820, 360, 40, (1, .9, .7)))
    iso = IsoR(cr, 1, 1, .6, 110, oy=.55, light=(1.2, .5), shadow=.2)
    snow_ground(iso)
    def hole(i):
        pts = [i.P(-.5, -.5, 0), i.P(1.5, -.5, 0), i.P(1.5, 1.5, 0), i.P(-.5, 1.5, 0)]
        i.cr.move_to(*pts[0]); [i.cr.line_to(*p) for p in pts[1:]]; i.cr.close_path(); fill(i.cr, hexc('#0A0A0E'))
    iso.custom(-50, hole)
    if state == 'party':
        person(iso, 2.2, 1.2, z=abs(math.sin(t * 7)) * .5, arms_up=1, jacket=C['orange'])
    elif state == 'hold':
        person(iso, 1.0, 1.6, z=-.9, arms_up=1, jacket=C['orange'])
    elif state == 'fall':
        f = prog(t, 104.4, 105.6)
        if f < 1: person(iso, .5, .5, z=-.9 - 6 * f * f, arms_up=1, jacket=C['orange'])
    iso.draw(); post(cr, t)

def s9(cr, t): pole_exit(cr, t, 'party'); confetti(cr, t, 99.42)

def s10(cr, t):
    if t < 104.4: pole_exit(cr, t, 'hold'); return
    if t < 106.0: pole_exit(cr, t, 'fall'); return
    oscillate(cr, t, 106.0); post(cr, t, grain=.06)

SCENES = [(0, 5.74, s1), (5.74, 23.89, s2), (23.89, 41.37, s3), (41.37, 51.85, s4), (51.85, 62.76, s5), (62.76, 73.51, s6),
          (73.51, 94.47, s7), (94.47, 99.42, s8), (99.42, 101.95, s9), (101.95, 121.5, s10)]
END = 121.5

def overlays(cr, t):
    G, R_, Y = C['green'], C['red'], C['yellow']
    pill(cr, t, wt('Rússia'), 15.5, 'POÇO DE KOLA, RÚSSIA', W / 2, 330, Y)
    if 9.7 <= t < 15.5: counter(cr, t, 9.7, 15.5, '12 KM', 'PROFUNDIDADE MÁXIMA', y=520)
    if 15.5 <= t < 18.4: counter(cr, t, 15.5, 18.4, '12.742 KM', 'DIÂMETRO DA TERRA', y=330)
    title(cr, t, wt('máquina'), 22.16, 'MÁQUINA', y=330)
    pill(cr, t, wt('fingir'), 23.89, 'VAMOS FINGIR QUE EXISTE', W / 2, 330, Y)
    if 24.0 <= t < 37.8:
        d = keys(t, [(23.9, 0), (27.6, 60), (31.3, 1800), (34.9, 6000), (37.8, 6371)])
        temp = 15 + d * 3 if d < 30 else min(5200, 100 + (d - 30) * .8)
        counter(cr, t, 24.0, 37.8, f"{int(temp):,} °C".replace(',', '.'), f"{int(d):,} KM DE PROFUNDIDADE".replace(',', '.'))
    pill(cr, t, wt('manto'), 31.7, 'MANTO', W / 2, 520, C['orange'])
    pill(cr, t, wt('núcleo'), 37.8, 'NÚCLEO', W / 2, 520, Y)
    title(cr, t, wt('cápsula'), 41.37, 'CÁPSULA TÉRMICA', y=330)
    pill(cr, t, wt('milhões'), 51.85, 'MILHÕES DE VEZES MAIS PRESSÃO', W / 2, 330, R_)
    pill(cr, t, wt('freia'), 58.78, 'RESISTÊNCIA DO AR', W / 2, 330, R_)
    title(cr, t, wt('vácuo'), 62.76, 'VÁCUO', y=330)
    pill(cr, t, wt('bate'), 70.3, 'BATE NA PAREDE', W / 2, 330, R_)
    title(cr, t, wt('polo', 70), 73.51, 'POLO A POLO', y=330)
    if 74.66 <= t < 88.77:
        p = prog(t, 74.66, 88.3); v = int(28400 * abs(math.sin(p * math.pi)))
        counter(cr, t, 74.66, 88.77, f"{v:,} KM/H".replace(',', '.'), 'VELOCIDADE')
    pill(cr, t, wt('nada'), 82.47, 'GRAVIDADE ZERO', W / 2, 330, G)
    counter(cr, t, 88.77, 94.47, '~40 MIN', 'DE VIAGEM', y=330)
    for a, lbl in (('Máquina', 'MÁQUINA IMPOSSÍVEL'), ('Cápsula', 'CÁPSULA TÉRMICA'), ('Vácuo', 'VÁCUO'), ('Polo', 'POLO A POLO')):
        t0 = wt(a, 94); nx = {'Máquina': wt('Cápsula', 95), 'Cápsula': wt('Vácuo', 96), 'Vácuo': wt('Polo', 98), 'Polo': 99.42}[a]
        pill(cr, t, t0, nx, lbl, W / 2, 330, G)
    title(cr, t, 99.45, 101.95, 'PARABÉNS!', y=360, size=150, sub='Você atravessou a Terra')
    if t >= 109.3:
        title(cr, t, 109.3, 999, 'COMENTE', y=210, size=110, tilt=0, col=C['white'])
        title(cr, max(t, 109.55), 109.55, 999, '"TÚNEL"', y=370, size=150, tilt=-.07)
        if t > 109.9:
            text_center(cr, 'se você pularia', W / 2, 1640, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - 109.9) / .3))
    if t < 109.3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    overlays(cr, t)
