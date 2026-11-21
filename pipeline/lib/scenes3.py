import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid3')
import cairo
from engine import *
from real import *
import scenes as v1
from scenes import city_ents, roads, draw_ents, confetti, PROD, ROAD

WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes3.json')))
def merge(first, last, disp, after=0.0):
    i = next(k for k, w in enumerate(WORDS) if w['t0'] >= after and w['w'].strip('.,') == first)
    j = next(k for k in range(i, len(WORDS)) if WORDS[k]['w'].strip('.,') == last)
    WORDS[i] = dict(WORDS[i], w=disp, key=True, t1=WORDS[j]['t1']); del WORDS[i + 1:j + 1]
merge('mil', 'setenta', '1.670 km/h'); merge('quilômetros', 'hora', 'por hora')
merge('mil', 'quinhentos', '1.500', after=13); merge('trezentos', 'cinco', '365', after=110)

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

CITY = city_ents(3, low={(0, 0), (-1, 0), (0, -1)})
JK = [hexc(c) for c in ('#3B82D6', '#2FAF6A', '#F59A3B', '#8E6CD8', '#F27AA6', '#E2453C', '#16A3A3', '#F2C13D')]
SNOW, SNOW2, ICE = hexc('#E4ECF4'), hexc('#CCD9E6'), hexc('#9FD0EC')
TW_TOP, TW_MID, TW_BOT = hexc('#1A2350'), hexc('#7A4C6E'), hexc('#F2995A')

# ---------- helpers ----------
def arrow(cr, x0, y0, x1, y1, c, w=14, a=1.0):
    cr.set_source_rgba(*c, a); cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(x0, y0); cr.line_to(x1, y1); cr.stroke()
    ang = math.atan2(y1 - y0, x1 - x0); L = w * 2.4
    cr.move_to(x1 + math.cos(ang) * w * .6, y1 + math.sin(ang) * w * .6)
    cr.line_to(x1 + math.cos(ang + 2.5) * L, y1 + math.sin(ang + 2.5) * L)
    cr.line_to(x1 + math.cos(ang - 2.5) * L, y1 + math.sin(ang - 2.5) * L); cr.close_path(); cr.fill()

def streaks(cr, t, n=60, seed=1, a=.45, speed=2600, ang=0.42, length=(180, 420), y0=0, y1=H):
    r = random.Random(seed); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(n):
        L = r.uniform(*length); sp = speed * r.uniform(.7, 1.3)
        x = (r.uniform(0, W + 800) + t * sp) % (W + 800) - 400; y = r.uniform(y0, y1)
        dx, dy = math.cos(ang) * L, math.sin(ang) * L
        g = cairo.LinearGradient(x - dx, y - dy, x, y); g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(1, 1, 1, 1, a)
        cr.set_source(g); cr.set_line_width(r.uniform(3, 8)); cr.move_to(x - dx, y - dy); cr.line_to(x, y); cr.stroke()

def snow_ground(iso, ext=60, seed=2, blocks=True):
    iso.ground(SNOW)
    r = random.Random(seed)
    for _ in range(40):
        x, y = r.uniform(-ext / 2, ext / 2), r.uniform(-ext / 2, ext / 2); s = r.uniform(1, 4)
        iso.quad(x, y, s * 1.6, s, SNOW2, z=.002)
    if blocks:
        for _ in range(16):
            x, y = r.uniform(-18, 22), r.uniform(-18, 22)
            if abs(x) < 4 and abs(y) < 4: continue
            s = r.uniform(.6, 1.8); iso.box(x, y, 0, s * 1.3, s, s * r.uniform(.5, 1.2), ICE)

def twilight_ground(iso, seed=4):
    iso.ground(hexc('#C9B9A6'))
    r = random.Random(seed)
    for _ in range(50):
        x, y = r.uniform(-40, 40), r.uniform(-40, 40); s = r.uniform(.8, 3)
        iso.quad(x, y, s * 1.5, s, hexc('#B8A792'), z=.002)
    for _ in range(26):
        x, y = r.uniform(-30, 40), r.uniform(-30, 40)
        if abs(x - 2) < 3 and abs(y - 2) < 3: continue
        s = r.uniform(.5, 2.0); iso.box(x, y, 0, s * 1.2, s, s * r.uniform(.4, 1.0), hexc('#9C8D7E'))

def front_char_r(cr, cx, by, s, expr='smile', arm='down', t=0.0, jacket=None):
    # soft contact shadow + rim light around the stylized character
    g = cairo.RadialGradient(cx, by - s * .02, 0, cx, by - s * .02, s * .35)
    g.add_color_stop_rgba(0, 0, 0, 0, .35); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    cr.save(); cr.translate(0, 0); cr.set_source(g); cr.arc(cx, by - s * .02, s * .35, 0, 7); cr.fill(); cr.restore()
    front_char(cr, cx, by, s, expr, arm=arm, t=t, jacket=jacket)

# ======================= SCENES =======================
LON = 120.0
def spin_lon(t):
    # fast spin, sudden stop at 3.05s
    if t < 3.05: return LON - t * 38
    return LON - 3.05 * 38 - 4 * (1 - math.exp(-(t - 3.05) * 30))

def s1(cr, t):
    space(cr, t)
    sh = (math.sin(t * 70) * 14 * math.exp(-(t - 3.05) * 5)) if t > 3.05 else 0
    R = keys(t, [(0, 400), (5.02, 430)])
    draw_globe(cr, W / 2 + sh, H / 2 + sh * .5, R, lon0=spin_lon(t), cloud_lon=t * 6 if t < 3.05 else 18)

def s2(cr, t):
    if t < 16.9:
        space(cr, t)
        R = keys(t, [(5.02, 430), (8.3, 470), (16.9, 480)])
        sh = (math.sin(t * 70) * 10 * math.exp(-(t - 15.6) * 4)) if t > 15.6 else 0
        cx, cy = W / 2 + sh, H / 2 + 40
        lon0 = spin_lon(5) - 40
        draw_globe(cr, cx, cy, R, lon0=lon0, tilt=.18)
        for lat, t0, col in ((0, 8.35, C['yellow']), (-23.5, 13.2, C['orange']), (75, 99, C['white'])):
            if t < t0: continue
            p = eout(prog(t, t0, t0 + .6))
            x, y, z = globe_point(cx, cy, R, lat, lon0, lon0, tilt=.18)
            L = 330 * math.cos(math.radians(lat)) * p
            circle(cr, x, y, 12, col)
            arrow(cr, x, y, x + L, y, col, w=14)
        return
    if t < 22.5:
        sky_r(cr, hexc('#6FA8DC'), hexc('#A9CBEA'), hexc('#DCEAF5'))
        iso = IsoR(cr, keys(t, [(16.9, 2), (22.5, 8)]), 0, 0, keys(t, [(16.9, 52), (22.5, 46)]), oy=.5, light=(1.6, .6), shadow=.32)
        roads(iso); draw_ents(iso, CITY, R=70)
        fl = lambda t0: max(0.0, t - t0)
        for k, (y, c) in enumerate(((-.6, C['red']), (.6, C['panel']), (13.4, C['orange']), (14.6, JK[1]))):
            e = fl(wt('carros') - .3)
            v1.car(iso, -6 + k * 5 + e * e * 30, y, c)
        r = random.Random(3)
        for k in range(10):
            e = fl(wt('prédios') - .2)
            x, y = r.uniform(0, 26), r.uniform(0, 26)
            iso.box(x + e * e * 22, y, 4 + e * 3 + r.uniform(0, 3), 1.2, 1.2, .5, hexc('#C9CED6'))
        for k in range(14):
            e = fl(wt('pessoas', 20) - .15)
            person(iso, r.uniform(-3, 20) + e * e * 26, r.choice((-1.6, 1.6, 12.4, 15.6)), z=min(1.5, e * 2), jacket=r.choice(JK))
        iso.draw()
        if t > wt('carros') - .3: streaks(cr, t, 70, seed=4, a=.6, speed=3200, ang=0.52)
        post(cr, t)
        return
    if t < 24.98:
        space(cr, t)
        R = keys(t, [(22.5, 480), (24.98, 620)])
        tilt = keys(t, [(22.5, .18), (24.9, .95)])
        draw_globe(cr, W / 2, H / 2 + keys(t, [(22.5, 40), (24.98, 260)]), R, lon0=spin_lon(5) - 40, tilt=tilt)
        x, y, z = globe_point(W / 2, H / 2 + keys(t, [(22.5, 40), (24.98, 260)]), R, 90, 0, 0, tilt=tilt)
        if t > 23.0:
            g = cairo.RadialGradient(x, y, 0, x, y, 90); g.add_color_stop_rgba(0, 1, .9, .3, .9); g.add_color_stop_rgba(1, 1, .9, .3, 0)
            cr.set_source(g); cr.arc(x, y, 90, 0, 7); cr.fill(); circle(cr, x, y, 12, C['yellow'])
        return
    sky_r(cr, hexc('#9DB8D3'), hexc('#CFDDEA'), hexc('#F1F5F9'), sun=(820, 360, 40, (1, .9, .7)))
    iso = IsoR(cr, 1, 1, .6, keys(t, [(24.98, 105), (28.31, 125)]), oy=.55, light=(1.2, .5), shadow=.2)
    snow_ground(iso)
    person(iso, .4, .4, jacket=C['orange'])
    iso.box(2.4, -1.8, 0, .08, .08, 2.2, C['metal']); iso.box(2.48, -1.8, 1.6, .02, .9, .55, C['red'])
    iso.draw()
    streaks(cr, t, 18, seed=9, a=.25, speed=500, ang=.3, length=(80, 160))
    post(cr, t, warm=.05)

def s3(cr, t):
    if t < 38.6:
        sky_r(cr, hexc('#4D5D73'), hexc('#7F8C9C'), hexc('#B5BEC8'))
        gust = prog(t, 29.8, 31.2)
        iso = IsoR(cr, keys(t, [(28.3, 4), (38.6, 9)]), 5, 0, keys(t, [(28.3, 34), (38.6, 40)]), oy=.52, light=(1.0, .3), shadow=.15)
        roads(iso)
        for e in CITY:
            if e[0] == 'tree':
                x, y, s = e[1], e[2], e[3]
                if abs(x - iso.cx) + abs(y - iso.cy) > 60: continue
                sway = gust * (.5 + .3 * math.sin(t * 9 + x))
                iso.box(x - .15 * s, y - .15 * s, 0, .3 * s, .3 * s, 1.0 * s, C['trunk'])
                iso.box(x - .6 * s + sway, y - .6 * s, .9 * s, 1.2 * s, 1.2 * s, 1.0 * s, C['leaf2'])
        draw_ents(iso, [e for e in CITY if e[0] != 'tree'], R=60)
        r = random.Random(5)
        for k in range(30):
            st = 30 + r.uniform(0, 6)
            if t < st: continue
            e = t - st
            x = r.uniform(-15, 25) + e * 18; y = r.uniform(-10, 25) - e * 3
            iso.box(x, y, 1 + 3 * math.sin(min(e, 3)) + r.uniform(0, 4), .6, .5, .12, r.choice((C['roof'], C['brown'], hexc('#C9CED6'))))
        iso.draw(night=.35 * gust)
        streaks(cr, t, int(30 + 120 * gust), seed=2, a=.4 + .35 * gust, speed=2400, ang=.38)
        cr.set_source_rgba(.75, .78, .82, .18 * gust); cr.paint()
        post(cr, t, vignette=.5)
        return
    # bunker cutaway
    g = cairo.LinearGradient(0, 0, 0, 700); g.add_color_stop_rgb(0, *hexc('#6E7F94')); g.add_color_stop_rgb(1, *hexc('#C3CCD6'))
    cr.set_source(g); cr.rectangle(0, 0, W, 700); cr.fill()
    streaks(cr, t, 40, seed=3, a=.4, speed=2400, ang=.12, y0=100, y1=650)
    layers = [(700, 780, SNOW), (780, 1000, hexc('#A9C7DC')), (1000, 1500, hexc('#7E6A58')), (1500, H, hexc('#5E4D40'))]
    for y0, y1, c in layers:
        g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgb(0, *shade(c, 1.05)); g.add_color_stop_rgb(1, *shade(c, .85))
        cr.set_source(g); cr.rectangle(0, y0, W, y1 - y0); cr.fill()
    r = random.Random(7)
    for _ in range(60): circle(cr, r.uniform(0, W), r.uniform(1010, H), r.uniform(4, 16), shade(hexc('#7E6A58'), r.uniform(.7, .9)))
    # shaft + bunker
    g = cairo.LinearGradient(500, 0, 580, 0); g.add_color_stop_rgb(0, *hexc('#5B6573')); g.add_color_stop_rgb(.5, *hexc('#A3ADBA')); g.add_color_stop_rgb(1, *hexc('#4A5260'))
    cr.set_source(g); cr.rectangle(500, 690, 80, 420); cr.fill()
    bx, by, bw, bh = 190, 1100, 700, 330
    rrect(cr, bx - 18, by - 18, bw + 36, bh + 36, 60); fill(cr, hexc('#3C434E'))
    g = cairo.LinearGradient(0, by, 0, by + bh); g.add_color_stop_rgb(0, *hexc('#FFD9A0')); g.add_color_stop_rgb(1, *hexc('#C98A4E'))
    rrect(cr, bx, by, bw, bh, 48); cr.set_source(g); cr.fill()
    lg = cairo.RadialGradient(bx + bw / 2, by + 40, 10, bx + bw / 2, by + 40, 320); lg.add_color_stop_rgba(0, 1, .95, .75, .9); lg.add_color_stop_rgba(1, 1, .9, .6, 0)
    cr.set_source(lg); rrect(cr, bx, by, bw, bh, 48); cr.fill()
    cr.rectangle(bx + 60, by + bh - 90, 220, 60); fill(cr, hexc('#7A5232')); cr.rectangle(bx + 70, by + bh - 130, 200, 40); fill(cr, hexc('#E9E2D5'))
    for k in range(4): cr.rectangle(bx + 430 + k * 50, by + 70, 36, 180 - k * 20); fill(cr, (hexc('#4E7FA8'), C['red'], hexc('#2F7A4E'), C['yellow'])[k])
    front_char(cr, bx + 340, by + bh - 6, 240, 'smile', t=t, jacket=C['orange'])
    post(cr, t)

def s4(cr, t):
    space(cr, t)
    cx, cy, R = W / 2, H / 2 + 20, keys(t, [(41.6, 440), (58.45, 470)])
    lon0 = 160 + (t - 41.6) * 1.5
    mig = ease(prog(t, 49.5, 55.6))
    draw_globe(cr, cx, cy, R, lon0=lon0, tilt=.12, mig=mig, clouds=.5)
    if 44.9 < t < 49.0:
        a = prog(t, 44.9, 45.3) * (1 - prog(t, 48.6, 49.0))
        for lat in (55, -55):
            for lon in (-35, 0, 35):
                x, y, z = globe_point(cx, cy, R, lat, lon0 + lon, lon0, tilt=.12)
                x2, y2, _ = globe_point(cx, cy, R, lat * .35, lon0 + lon, lon0, tilt=.12)
                arrow(cr, x, y, x2, y2, hexc('#7FD3FF'), w=12, a=a)
    if 49.3 < t < 56.0:
        a = prog(t, 49.3, 49.7) * (1 - prog(t, 55.6, 56.0))
        for lat in (12, -12):
            for lon in (-35, 0, 35):
                x, y, z = globe_point(cx, cy, R, lat, lon0 + lon, lon0, tilt=.12)
                x2, y2, _ = globe_point(cx, cy, R, lat * 4.6, lon0 + lon, lon0, tilt=.12)
                arrow(cr, x, y, x2, y2, hexc('#7FD3FF'), w=12, a=a)
    post(cr, t, grain=.06)

def twilight_fx(cr):
    g = cairo.LinearGradient(0, 0, W * .3, H)
    g.add_color_stop_rgb(0, *hexc('#4A4F8C')); g.add_color_stop_rgb(.55, *hexc('#C98A86')); g.add_color_stop_rgb(1, *hexc('#FFC48A'))
    cr.save(); cr.set_operator(cairo.OPERATOR_MULTIPLY); cr.set_source(g); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W * .95, H * .55, 20, W * .95, H * .55, 900)
    g.add_color_stop_rgba(0, 1, .7, .35, .45); g.add_color_stop_rgba(1, 1, .6, .3, 0)
    cr.save(); cr.set_operator(cairo.OPERATOR_SCREEN); cr.set_source(g); cr.paint(); cr.restore()

def thermo(cr, x, y, level, col, a=1.0):
    rrect(cr, x - 26, y - 300, 52, 320, 26); fill(cr, C['white'], a); circle(cr, x, y + 30, 46, C['white'], a)
    rrect(cr, x - 12, y - 280 + 280 * (1 - level), 24, 280 * level + 20, 12); fill(cr, col, a); circle(cr, x, y + 30, 32, col, a)

def s5(cr, t):
    if t < 72.65:
        space(cr, t, sun_at=(W + 120, H / 2 - 40, 70))
        cx, cy, R = W / 2 - 40, H / 2, 450
        glow = prog(t, 69.98, 71.0)
        draw_globe(cr, cx, cy, R, lon0=170, tilt=.12, sun=(1, -.05, .12), term_glow=glow * 1.2, night=.025, clouds=.6)
        if t > 67.5:
            a = prog(t, 67.5, 67.9) * (1 - prog(t, 69.6, 70.0))
            lv = prog(t, 67.5, 68.4)
            thermo(cr, cx + 270, cy + 80, .2 + .78 * lv, C['red'], a)
            thermo(cr, cx - 270, cy + 80, .55 - .5 * prog(t, 68.6, 69.4), hexc('#3B82D6'), a)
        post(cr, t, grain=.06); return
    sky_r(cr, TW_TOP, TW_MID, TW_BOT, sun=(980, 980, 46, (1, .55, .2)))
    iso = IsoR(cr, 2, 2, .6, keys(t, [(72.65, 85), (76.6, 100)]), oy=.6, light=(3.6, 1.6), shadow=.32)
    twilight_ground(iso)
    person(iso, 2, 2, jacket=C['orange'], bag=True)
    iso.draw(); twilight_fx(cr)
    post(cr, t, warm=.12)

def s6(cr, t):
    if t < 83.27:
        space(cr, t, sun_at=(W + 120, H / 2 - 40, 70))
        cx, cy, R = W / 2 - 40, H / 2, 450
        ang = (t - 76.6) * .05
        sun = (math.cos(ang), -.05, .12 + math.sin(ang))
        draw_globe(cr, cx, cy, R, lon0=170, tilt=.12, sun=sun, term_glow=1.2, night=.025, clouds=.6)
        # "you" on the terminator
        lon_term = 170 + 90 - math.degrees(ang) * 1.0
        x, y, z = globe_point(cx, cy, R, 30, lon_term - 0, 170, tilt=.12)
        g = cairo.RadialGradient(x, y, 0, x, y, 70); g.add_color_stop_rgba(0, 1, .9, .3, .9); g.add_color_stop_rgba(1, 1, .9, .3, 0)
        cr.set_source(g); cr.arc(x, y, 70, 0, 7); cr.fill(); circle(cr, x, y, 11, C['yellow'])
        post(cr, t, grain=.06); return
    sky_r(cr, TW_TOP, TW_MID, TW_BOT, sun=(980, 1000, 46, (1, .55, .2)))
    px = keys(t, [(83.27, 0), (87.9, 6)])
    iso = IsoR(cr, px + 1.2, 1.2, .6, 95, oy=.58, light=(3.6, 1.6), shadow=.32)
    twilight_ground(iso)
    person(iso, px, 1.0, phase=t * 9, jacket=C['orange'], bag=True)
    iso.draw(); twilight_fx(cr)
    post(cr, t, warm=.12)

def s7(cr, t):
    if t < 94.41:
        space(cr, t, sun_at=(W + 80, 380, 60))
        cx, cy, R = W / 2, H / 2 + 60, 360
        strength = 1 - .8 * prog(t, 93.16, 94.0)
        cr.set_line_width(5)
        for L in (1.5, 2.0, 2.6, 3.4):
            for side in (1, -1):
                cr.set_source_rgba(.45, .85, 1, .55 * strength * prog(t, 88.6, 89.3))
                first = True
                for k in range(0, 181, 3):
                    th = math.radians(k); r = L * math.sin(th) ** 2
                    if r < 1.0: first = True; continue
                    x = cx + side * r * math.sin(th) * R; y = cy - r * math.cos(th) * R
                    (cr.move_to if first else cr.line_to)(x, y); first = False
                cr.stroke()
        draw_globe(cr, cx, cy, R, lon0=200, tilt=.3, sun=(1, -.4, .3), clouds=.6)
        r = random.Random(2)
        for k in range(70):
            sp = r.uniform(500, 900); y0 = r.uniform(cy - 900, cy + 900)
            x = W + 100 - ((t * sp + r.uniform(0, 1400)) % 1500)
            y = y0
            dist = math.hypot(x - cx, y - cy)
            if strength > .5 and dist < R * 3.4:
                y = y0 + (y0 - cy) / max(1, abs(y0 - cy)) * (R * 3.4 - dist) * .6
            elif dist < R: continue
            circle(cr, x, y, 4, hexc('#FFE08A'), .8)
        post(cr, t, grain=.06); return
    sky_r(cr, TW_TOP, TW_MID, TW_BOT, sun=(980, 980, 46, (1, .55, .2)))
    iso = IsoR(cr, 2, 2, 1.2, 72, oy=.55, light=(3.0, 1.3), shadow=.3)
    twilight_ground(iso)
    rk = hexc('#8A7C70')
    for (x, y, w, d, h) in ((-3, -3, 4, 5, 3.5), (1, -3, 3, 3, 4.5), (-3, 2, 3, 2, 2.4), (4, -2, 2, 4, 2.6)):
        iso.box(x, y, 0, w, d, h, rk)
    iso.box(1, 0, 0, 3, 2, 2.2, rk, deco=lambda i, *b: i.frect(b, 'y', .25, 0, .75, .8, hexc('#1A1410'), edge=0))
    px = keys(t, [(94.41, 2.2), (97.6, 2.2)]); py = keys(t, [(94.41, 6), (97.6, 2.2)])
    if t < 97.7: person(iso, px, py, phase=t * 9, jacket=C['orange'], bag=True)
    iso.draw(); twilight_fx(cr)
    post(cr, t, warm=.1)

def compass(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2A3142')); g.add_color_stop_rgb(1, *hexc('#11151E')); cr.set_source(g); cr.paint()
    cx, cy, R = W / 2, 900, 360
    sh = cairo.RadialGradient(cx + 20, cy + 40, R * .8, cx + 20, cy + 40, R * 1.25); sh.add_color_stop_rgba(0, 0, 0, 0, .55); sh.add_color_stop_rgba(1, 0, 0, 0, 0)
    cr.set_source(sh); cr.arc(cx, cy, R * 1.3, 0, 7); cr.fill()
    g = cairo.LinearGradient(cx - R, cy - R, cx + R, cy + R); g.add_color_stop_rgb(0, *hexc('#F2D48A')); g.add_color_stop_rgb(.5, *hexc('#B8892F')); g.add_color_stop_rgb(1, *hexc('#6E4E18'))
    cr.set_source(g); cr.arc(cx, cy, R, 0, 7); cr.fill()
    g = cairo.RadialGradient(cx - 60, cy - 80, 20, cx, cy, R * .9); g.add_color_stop_rgb(0, *hexc('#FFFDF5')); g.add_color_stop_rgb(1, *hexc('#E2D8C2'))
    cr.set_source(g); cr.arc(cx, cy, R * .86, 0, 7); cr.fill()
    cr.set_source_rgb(*hexc('#3A3328'))
    for k in range(72):
        a = k * math.pi / 36; L = 34 if k % 9 == 0 else 16
        cr.set_line_width(5 if k % 9 == 0 else 2)
        cr.move_to(cx + math.cos(a) * R * .84, cy + math.sin(a) * R * .84); cr.line_to(cx + math.cos(a) * (R * .84 - L), cy + math.sin(a) * (R * .84 - L)); cr.stroke()
    for lbl, a in (('N', -90), ('L', 0), ('S', 90), ('O', 180)):
        text_center(cr, lbl, cx + math.cos(math.radians(a)) * R * .62, cy + math.sin(math.radians(a)) * R * .62 - 10, 64, hexc('#3A3328'))
    ang = t * 7 + math.sin(t * 3) * 2
    cr.save(); cr.translate(cx, cy); cr.rotate(ang)
    cr.move_to(0, -R * .7); cr.line_to(26, 0); cr.line_to(-26, 0); cr.close_path(); fill(cr, C['red'])
    cr.move_to(0, R * .7); cr.line_to(26, 0); cr.line_to(-26, 0); cr.close_path(); fill(cr, hexc('#E8E8E8'))
    cr.restore(); circle(cr, cx, cy, 20, hexc('#8A6A2A'))
    gl = cairo.LinearGradient(cx - R, cy - R, cx, cy); gl.add_color_stop_rgba(0, 1, 1, 1, .35); gl.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(gl); cr.arc(cx, cy, R * .86, 0, 7); cr.fill()

def s8(cr, t):
    cut = 'b' if t < wt('Mochila') else 'm' if t < wt('Roupa') else 'r' if t < wt('Bússola') else 'c'
    if cut == 'c': compass(cr, t); post(cr, t); return
    if cut == 'r':
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#C9D6E3')); g.add_color_stop_rgb(1, *hexc('#8FA3B8')); cr.set_source(g); cr.paint()
        front_char_r(cr, W / 2, 1950, 1450, 'happy', t=t, jacket=C['orange'])
        cr.set_line_width(10); cr.set_source_rgba(*shade(C['orange'], .75), .9)
        for k in range(5): cr.move_to(W / 2 - 250, 1180 + k * 70); cr.line_to(W / 2 + 250, 1180 + k * 70)
        cr.stroke(); post(cr, t); return
    sky_r(cr, hexc('#9DB8D3'), hexc('#CFDDEA'), hexc('#F1F5F9'))
    iso = IsoR(cr, 0, 0, .5, 150, oy=.52, light=(1.6, .7), shadow=.22)
    snow_ground(iso, blocks=False)
    if cut == 'b':
        iso.box(-1.2, -1.2, 0, 2.4, 2.4, .35, hexc('#7C8794'))
        def lid(i):
            x, y = i.P(0, 0, .36); rx = 1.0 * i.S * .87
            i.cr.save(); i.cr.translate(x, y); i.cr.scale(1, .5)
            g = cairo.RadialGradient(-rx * .3, -rx * .3, 5, 0, 0, rx); g.add_color_stop_rgb(0, *hexc('#C8D0DA')); g.add_color_stop_rgb(1, *hexc('#6E7884'))
            i.cr.set_source(g); i.cr.arc(0, 0, rx, 0, 7); i.cr.fill()
            i.cr.set_line_width(14); i.cr.set_source_rgb(*hexc('#4A525C')); i.cr.arc(0, 0, rx * .45, 0, 7); i.cr.stroke(); i.cr.restore()
        iso.custom(50, lid)
    else:
        iso.box(-.7, -1, 0, 1.4, 2.0, 2.2, hexc('#2F6B4F'), deco=lambda i, *b: (i.frect(b, 'x', .2, .1, .8, .5, hexc('#285A43')), i.frect(b, 'y', .2, .15, .8, .45, hexc('#285A43'))))
        iso.box(-.6, -.9, 2.2, 1.2, 1.8, .4, hexc('#3A7D5D'))
        iso.box(-.9, -.6, .4, .2, .2, 1.6, hexc('#1E2A24')); iso.box(-.9, .4, .4, .2, .2, 1.6, hexc('#1E2A24'))
    iso.draw(); post(cr, t)

def s9(cr, t):
    sky_r(cr, TW_TOP, TW_MID, TW_BOT, sun=(980, 980, 46, (1, .55, .2)))
    iso = IsoR(cr, 2, 2, .6, 95, oy=.62, light=(3.6, 1.6), shadow=.32)
    twilight_ground(iso)
    person(iso, 2, 2, z=abs(math.sin(t * 7)) * .5, arms_up=1, jacket=C['orange'], bag=True)
    iso.draw(); twilight_fx(cr); confetti(cr, t, 103.94); post(cr, t, warm=.12)

def cake(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2B2030')); g.add_color_stop_rgb(1, *hexc('#120D14')); cr.set_source(g); cr.paint()
    cx, cy = W / 2, 1180
    lg = cairo.RadialGradient(cx, cy - 420, 10, cx, cy - 420, 900); lg.add_color_stop_rgba(0, 1, .8, .45, .45); lg.add_color_stop_rgba(1, 1, .8, .45, 0)
    cr.set_source(lg); cr.paint()
    cr.save(); cr.translate(cx, cy + 210); cr.scale(1, .28); circle(cr, 0, 0, 430, hexc('#D8D2CC')); cr.restore()
    for (w, h, y0, c) in ((660, 230, cy, hexc('#E9B7C6')), (480, 180, cy - 190, hexc('#F3D3DC'))):
        g = cairo.LinearGradient(cx - w / 2, 0, cx + w / 2, 0); g.add_color_stop_rgb(0, *shade(c, .82)); g.add_color_stop_rgb(.45, *shade(c, 1.05)); g.add_color_stop_rgb(1, *shade(c, .75))
        cr.set_source(g); cr.rectangle(cx - w / 2, y0 - h / 2, w, h); cr.fill()
        cr.save(); cr.translate(cx, y0 + h / 2); cr.scale(1, .25); cr.arc(0, 0, w / 2, 0, math.pi); cr.restore(); cr.set_source(g); cr.fill()
        cr.save(); cr.translate(cx, y0 - h / 2); cr.scale(1, .25); circle(cr, 0, 0, w / 2, shade(c, 1.12)); cr.restore()
    cr.save(); cr.translate(cx, cy - 285); cr.scale(1, .25); circle(cr, 0, 0, 240, hexc('#FFF2F5')); cr.restore()
    rrect(cr, cx - 14, cy - 470, 28, 180, 8); fill(cr, hexc('#7FC4E8'))
    fl = 1 + .12 * math.sin(t * 23) + .06 * math.sin(t * 41)
    g = cairo.RadialGradient(cx, cy - 500, 0, cx, cy - 500, 160); g.add_color_stop_rgba(0, 1, .85, .4, .6); g.add_color_stop_rgba(1, 1, .7, .3, 0)
    cr.set_source(g); cr.arc(cx, cy - 500, 160, 0, 7); cr.fill()
    cr.save(); cr.translate(cx, cy - 500); cr.scale(1, 1.8 * fl)
    g = cairo.RadialGradient(0, 4, 2, 0, 0, 24); g.add_color_stop_rgb(0, 1, 1, .85); g.add_color_stop_rgb(.6, 1, .75, .25); g.add_color_stop_rgba(1, 1, .5, .1, 0)
    cr.set_source(g); cr.arc(0, 0, 24, 0, 7); cr.fill(); cr.restore()

def s10(cr, t):
    if t < 111.1:
        space(cr, t, sun_at=(W + 120, H / 2 - 40, 70))
        draw_globe(cr, W / 2 - 40, H / 2 + 60, 430, lon0=170, tilt=.12, sun=(1, -.05, .12), term_glow=1.2, night=.025, clouds=.6)
        post(cr, t, grain=.06); return
    if t < 116.2:
        cake(cr, t); post(cr, t); return
    space(cr, t)
    draw_globe(cr, W / 2, 1560, 330, lon0=170, tilt=.12, sun=(1, -.2, .3), term_glow=1.0, clouds=.6)
    post(cr, t, grain=.06)

SCENES = [(0, 5.02, s1), (5.02, 28.31, s2), (28.31, 41.6, s3), (41.6, 58.45, s4), (58.45, 76.63, s5),
          (76.63, 87.9, s6), (87.9, 98.18, s7), (98.18, 103.94, s8), (103.94, 107.54, s9), (107.54, 123.0, s10)]
END = 123.0

def overlays(cr, t):
    G, R_, Y = C['green'], C['red'], C['yellow']
    if t < 5.02:
        v = 1670 if t < 3.05 else int(1670 * (1 - eout(prog(t, 3.05, 3.5))))
        counter(cr, t, 0.3, 5.02, f"{v:,}".replace(',', '.') + ' KM/H', 'VELOCIDADE NO EQUADOR')
    pill(cr, t, 8.6, 16.9, 'EQUADOR: 1.670 KM/H', W / 2, 330, Y)
    pill(cr, t, 13.4, 16.9, 'SÃO PAULO: ~1.500 KM/H', W / 2, 440, C['orange'])
    pill(cr, t, 23.0, 28.31, 'POLO: QUASE 0 KM/H', W / 2, 330, G)
    title(cr, t, wt('polo'), 28.31, 'POLO', y=470)
    pill(cr, t, wt('ventania'), 38.6, 'VENTANIA', W / 2, 330, R_)
    title(cr, t, wt('bunker'), 41.6, 'BUNKER', y=330)
    pill(cr, t, 44.95, 48.6, 'HOJE: ÁGUA NO EQUADOR', W / 2, 300, hexc('#7FD3FF'))
    pill(cr, t, 49.3, 56.1, 'ÁGUA VAI PROS POLOS', W / 2, 300, hexc('#7FD3FF'))
    title(cr, t, wt('supercontinente'), 58.45, 'SUPERCONTINENTE', y=300, size=110)
    pill(cr, t, wt('virado'), 67.5, '6 MESES DE DIA', W / 2 + 230, 330, Y)
    pill(cr, t, wt('escuro') - .6, 67.5, '6 MESES DE NOITE', W / 2 - 230, 440, hexc('#3B82D6'))
    pill(cr, t, wt('torra'), 70.0, 'TORRA', W / 2 + 230, 330, R_); pill(cr, t, wt('congela'), 70.0, 'CONGELA', W / 2 - 230, 330, hexc('#3B82D6'))
    title(cr, t, wt('crepúsculo'), 76.63, 'CREPÚSCULO', y=330)
    pill(cr, t, 77.0, 83.2, 'A FAIXA SE MOVE', W / 2, 330, C['orange'])
    title(cr, t, wt('nômade'), 87.9, 'NÔMADE', y=330)
    pill(cr, t, wt('radiação'), 94.41, 'RADIAÇÃO', W / 2, 300, R_)
    pill(cr, t, wt('enfraquecer'), 94.41, 'ESCUDO MAIS FRACO', W / 2, 410, R_)
    for a, lbl in (('Bunker', 'BUNKER'), ('Mochila', 'MOCHILA'), ('Roupa', 'ROUPA TÉRMICA'), ('Bússola', 'BÚSSOLA')):
        t0 = wt(a, 98); nx = {'Bunker': wt('Mochila'), 'Mochila': wt('Roupa'), 'Roupa': wt('Bússola'), 'Bússola': 103.94}[a]
        pill(cr, t, t0, nx, lbl, W / 2, 330, G)
    title(cr, t, 103.98, 107.54, 'PARABÉNS!', y=360, size=150, sub='Você sobreviveu ao planeta parado')
    title(cr, t, wt('dia', 108), 111.1, '1 DIA = 1 ANO', y=330, size=120)
    if 111.9 <= t < 116.2:
        d = int(1 + 364 * eout(prog(t, 111.9, 115.8)))
        counter(cr, t, 111.9, 116.2, f'{d} DIAS' if d > 1 else '24 HORAS', 'DE ANIVERSÁRIO')
    if t >= 116.2:
        title(cr, t, 116.2, 999, 'COMENTE', y=520, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 116.45), 116.45, 999, '"POLO"', y=700, size=170, tilt=-.07)
        if t > 116.8:
            text_center(cr, 'se você iria pra lá', W / 2, 880, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - 116.8) / .3))
    if t < 116.1: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    overlays(cr, t)
