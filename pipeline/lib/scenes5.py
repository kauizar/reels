import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5')
import cairo
from engine import *
from real import *
import scenes as v1
from scenes import city_ents, roads, draw_ents, confetti, PROD, ROAD
sys.path.append('/home/claude/vid3'); sys.path.append('/home/claude/vid4')
import scenes3 as v3
import scenes4 as v4
from scenes3 import arrow, snow_ground, thermo, SNOW, twilight_fx
from scenes4 import night_sky, field, xmark

WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes5.json')))
# first phrase was mis-split by the aligner: spread block 0 evenly over 0.15-3.9 s
b0 = [w for w in WORDS if w['block'] == 0]; tot = sum(w['syl'] for w in b0); tt = 0.15
for w in b0:
    d = 3.75 * w['syl'] / tot; w['t0'], w['t1'] = tt, tt + d; tt += d
def merge(first, last, disp, after=0.0):
    i = next(k for k, w in enumerate(WORDS) if w['t0'] >= after and w['w'].strip('.,') == first)
    j = next(k for k in range(i + (1 if first == last else 0), len(WORDS)) if WORDS[k]['w'].strip('.,') == last)
    WORDS[i] = dict(WORDS[i], w=disp, key=True, t1=WORDS[j]['t1']); del WORDS[i + 1:j + 1]
merge('dois', 'dois', '2022'); merge('setenta', 'hora', '70.000 km/h'); merge('sessenta', 'milhões', '66 milhões')

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

IMP = (12.0, 282.0)          # impact site (ocean, near a coast)
VLON = 265.0
CITY = city_ents(5, low={(0, 0), (-1, 0), (0, -1)})
JK = v3.JK
T_IMPACT = 41.26

# ---------- camera shake ----------
SHAKES = [(T_IMPACT, 26, 2.2), (15.5, 0, 0), (27.0, 10, 3.5), (36.8, 6, 4.5), (45.7, 10, 3.0), (54.9, 5, 5.0)]
def shake_xy(t):
    ax = ay = 0.0
    for t0, amp, dur in SHAKES:
        if t0 <= t < t0 + dur and amp:
            k = amp * math.exp(-(t - t0) * 2.2 / dur)
            ax += k * (math.sin(t * 61) + .5 * math.sin(t * 37)); ay += k * (math.cos(t * 53) + .5 * math.sin(t * 29))
    return ax, ay

# ---------- fx ----------
def fireball(cr, x, y, r, ang, trail, t, heat=1.0):
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    # trail
    for k, (wf, col, a) in enumerate(((2.6, (1, .45, .1), .25), (1.6, (1, .65, .25), .45), (.8, (1, .95, .8), .7))):
        tx, ty = x - dx * trail * (1 - k * .2), y - dy * trail * (1 - k * .2)
        g = cairo.LinearGradient(tx, ty, x, y); g.add_color_stop_rgba(0, *col, 0); g.add_color_stop_rgba(1, *col, a * heat)
        cr.move_to(x + px * r * wf, y + py * r * wf); cr.line_to(tx, ty); cr.line_to(x - px * r * wf, y - py * r * wf); cr.close_path()
        cr.set_source(g); cr.fill()
    g = cairo.RadialGradient(x, y, 0, x, y, r * 5); g.add_color_stop_rgba(0, 1, 1, .95, heat); g.add_color_stop_rgba(.2, 1, .8, .4, .9 * heat)
    g.add_color_stop_rgba(.5, 1, .45, .1, .35 * heat); g.add_color_stop_rgba(1, 1, .3, 0, 0)
    cr.set_source(g); cr.arc(x, y, r * 5, 0, 7); cr.fill()
    r_ = random.Random(int(t * 30))
    for k in range(26):
        d = r_.uniform(0, trail * .7); s = r_.uniform(-1, 1) * r * 2
        circle(cr, x - dx * d + px * s, y - dy * d + py * s, r_.uniform(2, 6), (1, r_.uniform(.6, .95), .4), r_.uniform(.4, 1) * heat)

def smoke_puffs(cr, cx, cy, t, n=24, spread=300, rise=500, col=(.25, .22, .2), a=.6, seed=1, size=(60, 160)):
    r = random.Random(seed)
    for k in range(n):
        ph = (t * r.uniform(.12, .25) + k / n) % 1
        x = cx + r.uniform(-spread, spread) * (.4 + ph); y = cy - ph * rise
        circle(cr, x, y, r.uniform(*size) * (.5 + ph), col, a * (1 - ph) * min(1, ph * 6))

def flash(cr, t, t0, dur=1.0, col=(1, 1, 1)):
    if t0 <= t < t0 + dur:
        cr.set_source_rgba(*col, (1 - (t - t0) / dur) ** 1.5); cr.paint()

def shock_ring(cr, cx, cy, R, lat0, lon0, d, vlon, tilt, col=(1, .9, .7), w=10, a=1.0):
    la0, lo0 = math.radians(lat0), math.radians(lon0); dd = math.radians(d)
    pts = []
    for b in range(0, 361, 4):
        br = math.radians(b)
        la2 = math.asin(math.sin(la0) * math.cos(dd) + math.cos(la0) * math.sin(dd) * math.cos(br))
        lo2 = lo0 + math.atan2(math.sin(br) * math.sin(dd) * math.cos(la0), math.cos(dd) - math.sin(la0) * math.sin(la2))
        pts.append(globe_point(cx, cy, R, math.degrees(la2), math.degrees(lo2), vlon, tilt))
    cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for p, q in zip(pts, pts[1:]):
        if p[2] > 0 and q[2] > 0:
            cr.set_source_rgba(*col, a * min(1, p[2] * 3)); cr.move_to(p[0], p[1]); cr.line_to(q[0], q[1]); cr.stroke()

def target(cr, x, y, t, a=1.0):
    for k in range(3):
        ph = (t * .8 + k / 3) % 1
        cr.set_line_width(6); cr.set_source_rgba(1, .2, .15, a * (1 - ph)); cr.arc(x, y, 20 + ph * 120, 0, 7); cr.stroke()
    circle(cr, x, y, 12, (1, .25, .2), a)

def day_sky(cr, dim=0.0):
    sky_r(cr, mix(hexc('#4F86C6'), hexc('#3A2A20'), dim), mix(hexc('#8DB7E2'), hexc('#6A4A30'), dim), mix(hexc('#D8E8F5'), hexc('#B0703A'), dim))

def bunker_cut(cr, t, party=False, dust=0.0):
    g = cairo.LinearGradient(0, 0, 0, 700); g.add_color_stop_rgb(0, *mix(hexc('#6E7F94'), hexc('#5A3A22'), dust)); g.add_color_stop_rgb(1, *mix(hexc('#C3CCD6'), hexc('#A0683A'), dust))
    cr.set_source(g); cr.rectangle(0, 0, W, 700); cr.fill()
    if dust > 0: v3.streaks(cr, t, 70, seed=3, a=.5 * dust, speed=2600, ang=.08, y0=80, y1=690)
    layers = [(700, 760, hexc('#6E8F4E')), (760, 1000, hexc('#8C6A4E')), (1000, 1500, hexc('#7E6A58')), (1500, H, hexc('#5E4D40'))]
    for y0, y1, c in layers:
        g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgb(0, *shade(c, 1.05)); g.add_color_stop_rgb(1, *shade(c, .85))
        cr.set_source(g); cr.rectangle(0, y0, W, y1 - y0); cr.fill()
    r = random.Random(7)
    for _ in range(60): circle(cr, r.uniform(0, W), r.uniform(1010, H), r.uniform(4, 16), shade(hexc('#7E6A58'), r.uniform(.7, .9)))
    g = cairo.LinearGradient(500, 0, 580, 0); g.add_color_stop_rgb(0, *hexc('#5B6573')); g.add_color_stop_rgb(.5, *hexc('#A3ADBA')); g.add_color_stop_rgb(1, *hexc('#4A5260'))
    cr.set_source(g); cr.rectangle(500, 690, 80, 420); cr.fill()
    bx, by, bw, bh = 190, 1100, 700, 330
    rrect(cr, bx - 18, by - 18, bw + 36, bh + 36, 60); fill(cr, hexc('#3C434E'))
    g = cairo.LinearGradient(0, by, 0, by + bh); g.add_color_stop_rgb(0, *hexc('#FFD9A0')); g.add_color_stop_rgb(1, *hexc('#C98A4E'))
    rrect(cr, bx, by, bw, bh, 48); cr.set_source(g); cr.fill()
    lg = cairo.RadialGradient(bx + bw / 2, by + 40, 10, bx + bw / 2, by + 40, 320); lg.add_color_stop_rgba(0, 1, .95, .75, .9); lg.add_color_stop_rgba(1, 1, .9, .6, 0)
    cr.set_source(lg); rrect(cr, bx, by, bw, bh, 48); cr.fill()
    for k in range(4): cr.rectangle(bx + 430 + k * 50, by + 70, 36, 180 - k * 20); fill(cr, (hexc('#4E7FA8'), C['red'], hexc('#2F7A4E'), C['yellow'])[k])
    cr.rectangle(bx + 60, by + bh - 90, 220, 60); fill(cr, hexc('#7A5232'))
    jz = abs(math.sin(t * 7)) * 30 if party else 0
    front_char(cr, bx + 340, by + bh - 6 - jz, 240, 'happy' if party else 'O', arm='up' if party else 'down', t=t, jacket=C['orange'])

# ======================= SCENES =======================
def s1(cr, t):
    space(cr, t, sun_at=(-80, 300, 50))
    draw_globe(cr, W * .72, 1500, 300, lon0=VLON, tilt=.3, sun=(-.8, -.6, .4))
    p = prog(t, 0, 4.45) ** 1.6
    R = 70 + 380 * p
    x, y = W * .3 + (W * .5 - W * .3) * p, 520 + (820 - 520) * p
    draw_rock(cr, x, y, R, rot=t * 14, sun=(-.8, -.6, .5))
    post(cr, t, grain=.06)

def dart(cr, t):
    space(cr, t, sun_at=(-80, 300, 50))
    cx, cy = W / 2, 900
    draw_rock(cr, cx, cy, 190, rot=t * 6, sun=(-.8, -.6, .5))
    imp = wt('bateu')
    changed = ease(prog(t, imp + .3, imp + 1.6))
    a, b = 380 - 70 * changed, 150 - 25 * changed
    cr.set_line_width(4); cr.set_dash([14, 12]); cr.set_source_rgba(1, 1, 1, .6)
    cr.save(); cr.translate(cx, cy); cr.scale(1, b / a); cr.arc(0, 0, a, 0, 7); cr.restore(); cr.stroke(); cr.set_dash([])
    if changed > 0 and changed < 1:
        cr.set_source_rgba(1, 1, 1, .25); cr.save(); cr.translate(cx, cy); cr.scale(1, 150 / 380); cr.arc(0, 0, 380, 0, 7); cr.restore(); cr.stroke()
    ang = (t - 6) * .9 + 1.2
    mx, my = cx + math.cos(ang) * a, cy + math.sin(ang) * b
    draw_rock(cr, mx, my, 48, rot=t * 20, sun=(-.8, -.6, .5))
    if t < imp:
        p = prog(t, 7.0, imp)
        sx, sy = W + 60 + (mx - W - 60) * p, 260 + (my - 260) * p
        circle(cr, sx, sy, 10, hexc('#D9DEE6'))
        cr.rectangle(sx - 40, sy - 4, 26, 8); cr.rectangle(sx + 14, sy - 4, 26, 8); fill(cr, hexc('#2D4A86'))
        cr.set_line_width(3); cr.set_source_rgba(.6, .8, 1, .5); cr.move_to(sx, sy); cr.line_to(sx + 80, sy - 50 * (1 - p)); cr.stroke()
    if imp <= t < imp + 1.0:
        e = (t - imp); g = cairo.RadialGradient(mx, my, 0, mx, my, 40 + e * 300)
        g.add_color_stop_rgba(0, 1, 1, .9, 1 - e); g.add_color_stop_rgba(1, 1, .7, .3, 0); cr.set_source(g); cr.paint()
        r_ = random.Random(3)
        for k in range(30):
            an = r_.uniform(0, 6.28); d = e * r_.uniform(80, 260)
            circle(cr, mx + math.cos(an) * d, my + math.sin(an) * d, 4, (.8, .75, .7), 1 - e)
    post(cr, t, grain=.06)

def clock(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2A1A1A')); g.add_color_stop_rgb(1, *hexc('#0E0808')); cr.set_source(g); cr.paint()
    cx, cy, R = W / 2, 900, 360
    g = cairo.RadialGradient(cx, cy, R * .8, cx, cy, R * 1.6); g.add_color_stop_rgba(0, 1, .2, .1, .35 * (.6 + .4 * math.sin(t * 8))); g.add_color_stop_rgba(1, 1, .2, .1, 0)
    cr.set_source(g); cr.paint()
    g = cairo.LinearGradient(cx - R, cy - R, cx + R, cy + R); g.add_color_stop_rgb(0, *hexc('#D9DEE6')); g.add_color_stop_rgb(1, *hexc('#6E7884'))
    cr.set_source(g); cr.arc(cx, cy, R, 0, 7); cr.fill()
    g = cairo.RadialGradient(cx - 60, cy - 80, 20, cx, cy, R); g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, *hexc('#E2E4E8')); cr.set_source(g); cr.arc(cx, cy, R * .9, 0, 7); cr.fill()
    for k in range(60):
        a = k * math.pi / 30; L = 36 if k % 5 == 0 else 14
        cr.set_line_width(7 if k % 5 == 0 else 3); cr.set_source_rgb(*C['dark'])
        cr.move_to(cx + math.cos(a) * R * .86, cy + math.sin(a) * R * .86); cr.line_to(cx + math.cos(a) * (R * .86 - L), cy + math.sin(a) * (R * .86 - L)); cr.stroke()
    sp = 1 + 6 * prog(t, 15.5, 18.2)
    for ln, w, rate, col in ((.5, 18, .5, C['dark']), (.72, 12, 6, C['dark']), (.8, 5, 40, C['red'])):
        a = (t - 13) * rate * sp - math.pi / 2
        cr.set_line_width(w); cr.set_source_rgb(*col); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(cx, cy); cr.line_to(cx + math.cos(a) * R * ln, cy + math.sin(a) * R * ln); cr.stroke()
    circle(cr, cx, cy, 20, C['dark'])
    post(cr, t)

def globe_target(cr, t, R=470, zoom=0.0, rings=True, lines=0.0):
    space(cr, t, sun_at=(-80, 300, 50))
    cx, cy = W / 2, H / 2 + 40
    Rz = R * (1 + zoom)
    tilt = .3
    draw_globe(cr, cx, cy, Rz, lon0=VLON, tilt=tilt, sun=(-.6, -.45, .7))
    x, y, z = globe_point(cx, cy, Rz, IMP[0], IMP[1], VLON, tilt)
    if lines > 0:
        r = random.Random(4)
        for k in range(7):
            sx, sy = r.uniform(0, W), r.uniform(0, 600)
            p = clamp(lines * 1.4 - k * .08)
            cr.set_line_width(3); cr.set_dash([10, 10]); cr.set_source_rgba(.6, .9, 1, .7)
            cr.move_to(sx, sy); cr.line_to(sx + (x - sx) * p, sy + (y - sy) * p); cr.stroke(); cr.set_dash([])
    if rings: target(cr, x, y, t)
    return x, y

def s2(cr, t):
    if t < 6.75:
        space(cr, t, sun_at=(-80, 300, 50))
        draw_rock(cr, W / 2, 860, 440 + (t - 4.45) * 25, rot=t * 14, sun=(-.8, -.6, .5))
        q = back((t - 5.28) / .3) if t > 5.28 else 0
        if q > 0: text_center(cr, '?', W / 2 + 300, 560, 300, C['yellow'], stroke=C['dark'], sw=18, scale=q)
        post(cr, t, grain=.06); return
    if t < 13.3: dart(cr, t); return
    if t < 18.71: clock(cr, t); return
    x, y = globe_target(cr, t, zoom=.15 * prog(t, 18.7, 21.9))
    if t > 19.6:
        for k in range(8):
            a = k * math.pi / 4 + .3; p = eout(prog(t, 19.6, 20.6))
            arrow(cr, x + math.cos(a) * 60, y + math.sin(a) * 60, x + math.cos(a) * (60 + 200 * p), y + math.sin(a) * (60 + 200 * p), C['yellow'], w=10, a=.9)
    post(cr, t, grain=.06)

def tsunami(cr, t):
    t0 = 26.0; p = prog(t, t0, 31.3)
    day_sky(cr)
    # coastal city skyline
    r = random.Random(6); base = 1250
    for k in range(18):
        bw = r.uniform(60, 120); bh = r.uniform(150, 520); bx = 520 + k * 34 + r.uniform(-10, 10)
        g = cairo.LinearGradient(bx, 0, bx + bw, 0); g.add_color_stop_rgb(0, *hexc('#9AA9BC')); g.add_color_stop_rgb(1, *hexc('#6E7E92'))
        cr.set_source(g); cr.rectangle(bx, base - bh, bw, bh); cr.fill()
        for wy in range(int(base - bh + 20), base - 20, 34):
            cr.rectangle(bx + 10, wy, bw - 20, 12); fill(cr, hexc('#C9D9EA'), .5)
    g = cairo.LinearGradient(0, base, 0, H); g.add_color_stop_rgb(0, *hexc('#C9B48E')); g.add_color_stop_rgb(1, *hexc('#8C7556')); cr.set_source(g); cr.rectangle(0, base, W, H - base); cr.fill()
    # sea + wave front moving right
    front = -200 + p * 1500
    hgt = 260 + 520 * eout(prog(t, t0, 28.5))
    g = cairo.LinearGradient(0, base - hgt, 0, H); g.add_color_stop_rgb(0, *hexc('#2E78B8')); g.add_color_stop_rgb(.5, *hexc('#164A7A')); g.add_color_stop_rgb(1, *hexc('#0A2846'))
    cr.move_to(-50, H); cr.line_to(-50, base - hgt * .35)
    cr.curve_to(front - 500, base - hgt * .5, front - 160, base - hgt * 1.1, front + 60, base - hgt)
    cr.curve_to(front + 210, base - hgt * .95, front + 190, base - hgt * .6, front + 120, base - hgt * .55)
    cr.curve_to(front + 260, base - hgt * .4, front + 300, base - 40, front + 420, base + 20)
    cr.line_to(front + 420, H); cr.close_path(); cr.set_source(g); cr.fill()
    # foam
    r = random.Random(int(t * 20))
    for k in range(60):
        u = r.uniform(0, 1)
        fx = front + 60 + 150 * u * math.cos(u * 3); fy = base - hgt + 60 * u + r.uniform(-20, 20)
        circle(cr, fx, fy, r.uniform(6, 22), (1, 1, 1), r.uniform(.5, .9))
    for k in range(40):
        circle(cr, front + r.uniform(200, 420), base - r.uniform(0, 120), r.uniform(4, 16), (1, 1, 1), .7)
    post(cr, t)

def climb(cr, t):
    day_sky(cr)
    py = keys(t, [(31.3, 10), (35.2, -2)])
    iso = IsoR(cr, 2, py + 1, keys(t, [(31.3, 1.5), (35.2, 4.5)]), 46, oy=.55, light=(1.4, .5), shadow=.28)
    iso.ground(hexc('#6FA857'))
    for k in range(12):
        h = max(0, (8 - k) * .55)
        if h > 0: iso.box(-6, k * 2 - 6, 0, 18, 2, h, hexc('#7DB463') if k % 2 else hexc('#73A95A'))
    for k in range(12):
        h = max(0, (8 - k) * .55)
        if h > 0: iso.box(1.6, k * 2 - 6, h, 3.0, 2, .02, hexc('#5E6670'))
    r = random.Random(8)
    for k in range(30):
        tx, ty = r.choice((r.uniform(-6, 1.2), r.uniform(5, 12))), r.uniform(-6, 16)
        kk = int((ty + 6) / 2); h = max(0, (8 - kk) * .55)
        iso.box(tx - .5, ty - .5, h, 1, 1, 1.2, hexc('#3E8E3A')); iso.box(tx - .1, ty - .1, h, .2, .2, .4, C['trunk'])
    for k in range(6):
        cy = py + k * 1.8; h = max(0, (8 - int((cy + 6) / 2)) * .55)
        v1.car(iso, 2 + (k % 2) * 1.3, cy, JK[k % 8], along='y') if False else iso.box(2 + (k % 2) * 1.3, cy, h + .1, 1.0, 1.8, .7, JK[k % 8])
    iso.draw(); post(cr, t)

def s3(cr, t):
    if t < 24.9:
        globe_target(cr, t, zoom=.15 + .2 * prog(t, 21.9, 24.9), lines=prog(t, 21.9, 24.0)); post(cr, t, grain=.06); return
    if t < 26.0:
        x, y = globe_target(cr, t, zoom=.35 + .4 * prog(t, 24.9, 26.0))
        post(cr, t, grain=.06); return
    if t < 31.33: tsunami(cr, t); return
    climb(cr, t)

def entry(cr, t):
    dim = 0
    day_sky(cr)
    v1.clouds(cr, t, 4, alpha=.8)
    r = random.Random(3)
    cr.move_to(0, 1500)
    for x in range(0, W + 60, 60): cr.line_to(x, 1500 - 60 * math.sin(x * .004) - r.uniform(0, 30))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); fill(cr, hexc('#3C5A3A'))
    p = prog(t, 35.2, T_IMPACT)
    x = W * .85 - p * W * .6; y = 150 + p * 1300
    r_ = 20 + 60 * p ** 2
    fireball(cr, x, y, r_, math.atan2(1300, -W * .6), 500 + 900 * p, t, heat=1)
    g = cairo.RadialGradient(x, y, 0, x, y, 900); g.add_color_stop_rgba(0, 1, .7, .3, .25 * p); g.add_color_stop_rgba(1, 1, .6, .2, 0); cr.set_source(g); cr.paint()
    post(cr, t)

def explosion(cr, t):
    e = t - T_IMPACT
    sky_r(cr, hexc('#3A2418'), hexc('#B2532A'), hexc('#F2A15A'))
    hz = 1320; cx = W * .45
    R = 120 + 900 * (1 - math.exp(-e * .9))
    g = cairo.RadialGradient(cx, hz, 0, cx, hz, R); g.add_color_stop_rgba(0, 1, 1, .85, 1); g.add_color_stop_rgba(.25, 1, .75, .3, 1)
    g.add_color_stop_rgba(.6, .9, .35, .08, .85); g.add_color_stop_rgba(1, .4, .12, .03, 0)
    cr.set_source(g); cr.arc(cx, hz, R, math.pi, 2 * math.pi); cr.fill()
    smoke_puffs(cr, cx, hz - R * .6, t, n=40, spread=R * .5, rise=R * .9, col=(.18, .12, .1), a=.75, seed=4, size=(80, 220))
    cr.set_line_width(14); cr.set_source_rgba(1, .9, .7, max(0, .8 - e * .2))
    cr.save(); cr.translate(cx, hz); cr.scale(1, .18); cr.arc(0, 0, R * 1.6, 0, 7); cr.restore(); cr.stroke()
    cr.move_to(0, hz)
    for x in range(0, W + 60, 60): cr.line_to(x, hz + 10 * math.sin(x * .01))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); fill(cr, hexc('#1E140E'))
    flash(cr, t, T_IMPACT, 1.0)
    post(cr, t)

def s4(cr, t):
    if t < T_IMPACT: entry(cr, t); return
    if t < 45.6: explosion(cr, t); return
    if t < 49.3:
        space(cr, t, sun_at=(-80, 300, 50))
        cx, cy, R = W / 2, H / 2 + 40, 520
        e = t - 45.6
        draw_globe(cr, cx, cy, R, lon0=VLON, tilt=.3, sun=(-.6, -.45, .7), hot=(IMP[0], IMP[1], 8 + e * 3, 1.0), haze=(IMP[0], IMP[1], 5 + e * 8, .9))
        for k in range(3):
            d = e * 9 - k * 3
            if d > 0: shock_ring(cr, cx, cy, R, IMP[0], IMP[1], d, VLON, .3, a=max(0, .9 - k * .25), w=10 - k * 3)
        post(cr, t, grain=.06); return
    bunker_cut(cr, t, dust=prog(t, 49.3, 50.5)); post(cr, t)

def rain_fire(cr, t):
    sky_r(cr, hexc('#2A1810'), hexc('#7A3A1E'), hexc('#C2692E'))
    iso = IsoR(cr, 3, 3, 0, keys(t, [(53.7, 40), (59.9, 48)]), oy=.58, light=(1.0, .4), shadow=.18)
    iso.ground(hexc('#4E5E3A'))
    r = random.Random(5); trees = []
    for k in range(40):
        x, y = r.uniform(-10, 14), r.uniform(-10, 14); s = r.uniform(.9, 1.4); trees.append((x, y, s, r.uniform(55.0, 60.0)))
        v1.tree(iso, x, y, s)
    iso.draw(night=.3)
    for x, y, s, st in trees:
        if t < st: continue
        px, py = iso.P(x, y, 2.2 * s); f = min(1, (t - st) * 1.5)
        g = cairo.RadialGradient(px, py, 0, px, py, 90 * f); g.add_color_stop_rgba(0, 1, .7, .2, .8); g.add_color_stop_rgba(1, 1, .3, 0, 0); cr.set_source(g); cr.arc(px, py, 90 * f, 0, 7); cr.fill()
        for k in range(4):
            h = (40 + 25 * math.sin(t * 15 + k + x)) * f
            cr.move_to(px - 30 + k * 18, py + 20); cr.line_to(px - 22 + k * 18, py + 20 - h); cr.line_to(px - 14 + k * 18, py + 20); cr.close_path(); fill(cr, (1, .55 + .15 * (k % 2), .15))
    smoke_puffs(cr, W / 2, 900, t, n=30, spread=500, rise=900, col=(.15, .12, .1), a=.4, seed=2)
    r = random.Random(9)
    for k in range(22):
        sp = r.uniform(700, 1100); st = r.uniform(0, 3)
        ph = ((t - 53.7) * sp / 1500 + st) % 1
        x0 = r.uniform(-200, W + 200); x = x0 - ph * 500; y = -100 + ph * 1600
        fireball(cr, x, y, 6, math.atan2(1600, -500), 160, t, heat=.9)
    post(cr, t, warm=.08)

def shelter(cr, t):
    sky_r(cr, hexc('#2A1810'), hexc('#6A3A22'), hexc('#A8602E'))
    iso = IsoR(cr, 1, 1, .8, 78, oy=.55, light=(1.0, .4), shadow=.2)
    iso.ground(hexc('#6A6A5A'))
    def dd(i, *b): i.frect(b, 'x', .4, 0, .65, .7, hexc('#3A3F48'))
    iso.box(-2, -2, 0, 4, 3.4, 2.2, hexc('#9AA0A8'), deco=dd)
    for k in range(3): iso.box(2.6 + k * .9, 1.8, 0, .7, .7, 1.0, hexc('#2F7BC4'), top=hexc('#3E8ED8'))
    person(iso, 2.4, .2, jacket=C['orange'])
    iso.draw(night=.25)
    r = random.Random(int(t * 10))
    for k in range(40):
        circle(cr, r.uniform(0, W), r.uniform(0, H), r.uniform(2, 5), (1, .6, .2), r.uniform(.3, .9))
    post(cr, t, warm=.08)

def s5(cr, t):
    if t < 59.9: rain_fire(cr, t)
    else: shelter(cr, t)

def s6(cr, t):
    if t < 72.66:
        space(cr, t, sun_at=(-80, 300, 50 * (1 - prog(t, 70.8, 72.3))) if t < 72.3 else None)
        hz = 25 + 150 * ease(prog(t, 66.7, 71.3))
        dim = 1 - .6 * prog(t, 70.8, 72.3)
        draw_globe(cr, W / 2, H / 2 + 40, 470, lon0=VLON + (t - 64.9) * 1.2, tilt=.3, sun=(-.6, -.45, .7), haze=(IMP[0], IMP[1], hz, .95), bright=dim)
        post(cr, t, grain=.06); return
    sky_r(cr, hexc('#3B3632'), hexc('#5E5852'), hexc('#857C72'))
    iso = IsoR(cr, 6, 6, 0, keys(t, [(72.66, 32), (78.9, 40)]), oy=.52, light=(.6, .2), shadow=.06)
    roads(iso)
    draw_ents(iso, CITY, R=60)
    iso.draw(night=.35)
    cr.save(); cr.set_operator(cairo.OPERATOR_SCREEN); cr.set_source_rgba(.6, .6, .65, .18 * prog(t, 74, 77)); cr.paint(); cr.restore()
    r = random.Random(1)
    for k in range(160):
        sp = r.uniform(60, 160); x = (r.uniform(0, W) + math.sin(t + k) * 30) % W; y = (r.uniform(0, H) + t * sp) % H
        circle(cr, x, y, r.uniform(2, 5), (.95, .95, .95), .8)
    if t > 75.0:
        thermo(cr, W - 150, 1250, .6 - .5 * ease(prog(t, 75.0, 76.6)), hexc('#3B82D6'), prog(t, 75.0, 75.3))
    post(cr, t, vignette=.55)

def pantry(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2A1E16')); g.add_color_stop_rgb(1, *hexc('#120C08')); cr.set_source(g); cr.paint()
    iso = IsoR(cr, 1.5, 0, 1.4, keys(t, [(81.35, 120), (86.5, 140)]), oy=.5, light=(-1.0, -.4), shadow=.2)
    iso.ground(hexc('#5E4A3A'))
    for lv in range(3): iso.box(-1.5, -.6, lv * 1.2, 7, 1.0, .1, C['brown'])
    r = random.Random(3)
    for lv in range(3):
        for k in range(10):
            if lv == 1 and k % 2: iso.box(-1.3 + k * .62, -.4, .1 + lv * 1.2, .5, .6, .7, hexc('#D9C08A'))
            else: v1.can(iso, -1.2 + k * .6, -.1, .1 + lv * 1.2, s=.95)
    iso.draw()
    g = cairo.RadialGradient(W / 2, 500, 20, W / 2, 500, 1100); g.add_color_stop_rgba(0, 1, .85, .55, .35); g.add_color_stop_rgba(1, 1, .8, .5, 0)
    cr.save(); cr.set_operator(cairo.OPERATOR_SCREEN); cr.set_source(g); cr.paint(); cr.restore()
    post(cr, t, warm=.08)

def s7(cr, t):
    if t < 81.35:
        sky_r(cr, hexc('#3B3632'), hexc('#5E5852'), hexc('#857C72'))
        iso = IsoR(cr, 1, 1, 0, 52, oy=.55, light=(.6, .2), shadow=.06)
        field(iso, t, ease(prog(t, 79.0, 81.0))); iso.draw(night=.3); post(cr, t); return
    if t < 86.54: pantry(cr, t); return
    v4.greenhouse_shot(cr, t, S=keys(t, [(86.54, 60), (88.72, 72)]))

def dino(cr, x, y, s, col=(.05, .05, .07)):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    pts = [(-260, 0), (-120, -60), (-40, -150), (60, -170), (110, -240), (150, -330), (210, -360), (300, -350), (320, -320), (250, -300), (220, -260),
           (200, -200), (150, -120), (120, -40), (140, 0), (100, 0), (80, -60), (20, -60), (0, 0), (-40, 0), (-60, -60), (-140, -40)]
    cr.move_to(*pts[0]); [cr.line_to(*p) for p in pts[1:]]; cr.close_path(); fill(cr, col)
    cr.restore()

def s8(cr, t):
    if t < 94.54:
        sky_r(cr, hexc('#2A1A2E'), hexc('#B0503A'), hexc('#F2A15A'))
        p = prog(t, 88.7, 94.5)
        fireball(cr, W * .9 - p * 500, 200 + p * 500, 22 + 20 * p, math.atan2(500, -500), 600, t)
        cr.move_to(0, 1450)
        for x in range(0, W + 60, 60): cr.line_to(x, 1450 - 40 * math.sin(x * .005))
        cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); fill(cr, (.06, .05, .07))
        dino(cr, W * .42, 1470, 1.5)
        for k, (tx, ty, ss) in enumerate(((150, 1440, .5), (820, 1430, .6))): dino(cr, tx, ty, ss)
        post(cr, t, warm=.06); return
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#4A3A2E')); g.add_color_stop_rgb(1, *hexc('#2A1E16')); cr.set_source(g); cr.paint()
    g = cairo.LinearGradient(300, 0, 780, 0); g.add_color_stop_rgb(0, *hexc('#5B6573')); g.add_color_stop_rgb(.5, *hexc('#B3BDCA')); g.add_color_stop_rgb(1, *hexc('#4A5260'))
    rrect(cr, 300, 500, 480, 900, 30); cr.set_source(g); cr.fill()
    circle(cr, 540, 950, 110, hexc('#6E7884')); cr.set_line_width(16); cr.set_source_rgb(*hexc('#3A424C')); cr.arc(540, 950, 70, 0, 7); cr.stroke()
    rrect(cr, 360, 560, 360, 90, 14); fill(cr, C['red']); text_center(cr, 'FECHADO', 540, 595, 64, C['white'])
    knock = math.sin(t * 12) * 20 if t > 94.9 else 0
    dino(cr, 980 + knock, 1700, 1.6, col=hexc('#5E8A4A'))
    if t > 95.1: text_center(cr, '?', 900, 760, 220, C['yellow'], stroke=C['dark'], sw=14, scale=back((t - 95.1) / .3))
    post(cr, t)

def s9(cr, t):
    cuts = [(wt('Rádio', 96), 'r'), (wt('Água', 96), 'a'), (wt('Comida', 96), 'c'), (wt('Lanterna', 96), 'l'), (wt('Bunker', 100), 'b')]
    cur = cuts[0][1]
    for t0, k in cuts:
        if t >= t0 - .05: cur = k
    if cur in ('r', 'c'):
        v1.obj_shot(cr, t, 'radio', hexc('#FFE3A3')) if cur == 'r' else v1.cans_aisle(cr, 39.5)
        post(cr, t); return
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#1E2633')); g.add_color_stop_rgb(1, *hexc('#0A0E14')); cr.set_source(g); cr.paint()
    if cur == 'a':
        for k in range(5):
            x = 260 + k * 140
            g = cairo.LinearGradient(x - 50, 0, x + 50, 0); g.add_color_stop_rgba(0, .3, .6, .9, .7); g.add_color_stop_rgba(.4, .7, .9, 1, .85); g.add_color_stop_rgba(1, .2, .5, .8, .7)
            rrect(cr, x - 50, 760, 100, 380, 30); cr.set_source(g); cr.fill(); rrect(cr, x - 22, 700, 44, 70, 8); fill(cr, hexc('#2D4A86'))
    elif cur == 'l':
        cx, cy = 340, 1000
        g = cairo.LinearGradient(cx, cy, W, cy - 300); g.add_color_stop_rgba(0, 1, .97, .8, .7); g.add_color_stop_rgba(1, 1, .97, .8, 0)
        cr.move_to(cx + 120, cy - 40); cr.line_to(W + 100, cy - 600); cr.line_to(W + 100, cy + 200); cr.line_to(cx + 120, cy + 40); cr.close_path(); cr.set_source(g); cr.fill()
        g = cairo.LinearGradient(0, cy - 50, 0, cy + 50); g.add_color_stop_rgb(0, *hexc('#4A4F58')); g.add_color_stop_rgb(.5, *hexc('#9AA3AE')); g.add_color_stop_rgb(1, *hexc('#3A3F48'))
        rrect(cr, cx - 220, cy - 45, 300, 90, 20); cr.set_source(g); cr.fill(); rrect(cr, cx + 60, cy - 65, 70, 130, 16); cr.set_source(g); cr.fill()
    else:
        bunker_cut(cr, t)
    post(cr, t)

def hatch(cr, t):
    p = ease(prog(t, 105.6, 107.6)); clear = ease(prog(t, 107.6, 111.0))
    sky_r(cr, mix(hexc('#5A5550'), hexc('#3E7FC9'), clear), mix(hexc('#7A746C'), hexc('#8FC2EE'), clear), mix(hexc('#9A928A'), hexc('#FFE2B0'), clear),
          sun=(W / 2 + 120, 640, 70 * clear, (1, .85, .5)) if clear > 0 else None)
    if clear > 0:
        cr.save(); cr.translate(W / 2 + 120, 640)
        for k in range(14):
            a = k * math.pi / 7 + t * .05
            g = cairo.LinearGradient(0, 0, math.cos(a) * 1400, math.sin(a) * 1400); g.add_color_stop_rgba(0, 1, .9, .6, .35 * clear); g.add_color_stop_rgba(1, 1, .9, .6, 0)
            cr.move_to(0, 0); cr.line_to(math.cos(a - .06) * 1400, math.sin(a - .06) * 1400); cr.line_to(math.cos(a + .06) * 1400, math.sin(a + .06) * 1400); cr.close_path()
            cr.set_source(g); cr.fill()
        cr.restore()
    v1.clouds(cr, t, 4, alpha=.6 * (1 - clear * .6))
    # hatch frame (looking up from inside)
    R = 520 + 600 * p
    cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    cr.rectangle(0, 0, W, H); cr.new_sub_path(); cr.arc(W / 2, 900, R, 0, 7); fill(cr, hexc('#1E2229'))
    cr.set_fill_rule(cairo.FILL_RULE_WINDING)
    cr.new_path(); cr.set_line_width(40); cr.set_source_rgb(*hexc('#5B6573')); cr.arc(W / 2, 900, R, 0, 7); cr.stroke()
    if p < 1:
        cr.save(); cr.translate(W / 2, 900); cr.scale(1, max(.02, 1 - p));
        g = cairo.RadialGradient(-80, -80, 10, 0, 0, R); g.add_color_stop_rgb(0, *hexc('#A3ADBA')); g.add_color_stop_rgb(1, *hexc('#4A5260'))
        cr.new_path(); cr.arc(0, -R * p * 1.2, R * .98, 0, 7); cr.set_source(g); cr.fill(); cr.restore()
    post(cr, t, warm=.06 * clear)

def s10(cr, t): bunker_cut(cr, t, party=True); confetti(cr, t, 102.26); post(cr, t)

SCENES = [(0, 4.45, s1), (4.45, 21.92, s2), (21.92, 35.17, s3), (35.17, 53.7, s4), (53.7, 64.9, s5), (64.9, 78.89, s6),
          (78.89, 88.72, s7), (88.72, 96.66, s8), (96.66, 102.26, s9), (102.26, 105.55, s10), (105.55, 122.0, hatch)]
END = 122.0

def overlays(cr, t):
    G, R_, Y = C['green'], C['red'], C['yellow']
    if t < 4.45:
        s = int(86400 * (1 - .35 * prog(t, .3, 4.4)))
        counter(cr, t, .3, 4.45, f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}", 'ATÉ O IMPACTO')
    pill(cr, t, wt('2022'), 13.3, 'MISSÃO DART, 2022', W / 2, 330, Y)
    pill(cr, t, wt('mudou'), 13.3, 'ÓRBITA ALTERADA', W / 2, 440, G)
    pill(cr, t, wt('anos'), 18.71, 'ANOS DE PREPARAÇÃO', W / 2, 330, Y)
    pill(cr, t, wt('tempo', 17), 18.71, 'SEM TEMPO', W / 2, 1560, R_)
    title(cr, t, wt('caminho'), 21.92, 'SAIR DO CAMINHO', y=330)
    pill(cr, t, wt('calculam'), 26.0, 'ZONA DE IMPACTO', W / 2, 330, R_)
    pill(cr, t, wt('tsunami'), 31.33, 'TSUNAMI', W / 2, 330, R_)
    title(cr, t, wt('alto'), 35.17, 'PARA O ALTO', y=330)
    if 36.77 <= t < T_IMPACT:
        v = int(70000 * eout(prog(t, 36.77, 38.0)))
        counter(cr, t, 36.77, T_IMPACT, f"{v:,}".replace(',', '.') + ' KM/H', 'VELOCIDADE DE ENTRADA')
    pill(cr, t, wt('bilhões'), 45.6, 'BILHÕES DE BOMBAS ATÔMICAS', W / 2, 330, R_)
    pill(cr, t, wt('choque'), 49.3, 'ONDA DE CHOQUE', W / 2, 330, R_)
    title(cr, t, wt('subsolo'), 53.7, 'SUBSOLO', y=330)
    pill(cr, t, wt('chovem'), 59.9, 'CHUVA DE DETRITOS', W / 2, 330, R_)
    pill(cr, t, wt('água', 61), 64.9, 'ÁGUA GUARDADA', W / 2, 330, G)
    pill(cr, t, wt('poeira'), 72.66, 'POEIRA NA ATMOSFERA', W / 2, 330, R_)
    title(cr, t, wt('inverno'), 78.89, 'INVERNO DE IMPACTO', y=330, size=100)
    pill(cr, t, wt('lavouras'), 81.35, 'LAVOURAS FALHAM', W / 2, 330, R_)
    title(cr, t, wt('guardada', 80), 88.72, 'COMIDA GUARDADA', y=330)
    counter(cr, t, 88.72, 94.54, '66 MILHÕES', 'DE ANOS ATRÁS')
    for a, lbl in (('Rádio', 'RÁDIO'), ('Água', 'ÁGUA'), ('Comida', 'COMIDA ENLATADA'), ('Lanterna', 'LANTERNA'), ('Bunker', 'BUNKER')):
        t0 = wt(a, 96); nx = {'Rádio': wt('Água', 96), 'Água': wt('Comida', 96), 'Comida': wt('Lanterna', 96), 'Lanterna': wt('Bunker', 100), 'Bunker': 102.26}[a]
        pill(cr, t, t0, nx, lbl, W / 2, 330, G)
    title(cr, t, 102.3, 105.55, 'PARABÉNS!', y=360, size=150, sub='Você sobreviveu ao fim do mundo')
    if t >= 113.3:
        title(cr, t, 113.3, 999, 'COMENTE', y=1320, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 113.55), 113.55, 999, '"BUNKER"', y=1500, size=160, tilt=-.07)
        if t > 113.9:
            text_center(cr, 'se você sobreviveria', W / 2, 1670, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - 113.9) / .3))
    if t < 113.3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    sx, sy = shake_xy(t)
    cr.save()
    if sx or sy: cr.translate(sx, sy); cr.translate(W / 2, H / 2); cr.scale(1.03, 1.03); cr.translate(-W / 2, -H / 2)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    cr.restore()
    overlays(cr, t)
