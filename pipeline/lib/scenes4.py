import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid4')
import cairo
from engine import *
from real import *
import scenes as v1
from scenes import city_ents, roads, draw_ents, confetti, PROD, ROAD
sys.path.append('/home/claude/vid3')
import scenes3 as v3
from scenes3 import arrow, snow_ground, thermo, SNOW, SNOW2, ICE

WORDS = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'words_scenes4.json')))
def merge(first, last, disp, after=0.0):
    i = next(k for k, w in enumerate(WORDS) if w['t0'] >= after and w['w'].strip('.,') == first)
    j = next(k for k in range(i, len(WORDS)) if WORDS[k]['w'].strip('.,') == last)
    WORDS[i] = dict(WORDS[i], w=disp, key=True, t1=WORDS[j]['t1']); del WORDS[i + 1:j + 1]
merge('oito', 'segundos', '8 min 20 s'); merge('cento', 'milhões', '150 milhões')
merge('dezoito', 'negativos', '-18 °C'); merge('setenta', 'negativos', '-70 °C')

def wt(word, after=0.0):
    for w in WORDS:
        if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()): return w['t0']
    raise KeyError(word)

CITY = city_ents(4, low={(0, 0), (-1, 0), (0, -1)})
JK = v3.JK
NIGHT_TOP, NIGHT_BOT = hexc('#05070F'), hexc('#121A33')

def night_sky(cr, t, density=1.0, milky=0.0):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *NIGHT_TOP); g.add_color_stop_rgb(1, *NIGHT_BOT); cr.set_source(g); cr.paint()
    if milky > 0:
        cr.save(); cr.translate(W / 2, H * .38); cr.rotate(-.6); cr.scale(1, .22)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 1100); g.add_color_stop_rgba(0, .75, .7, .95, .35 * milky); g.add_color_stop_rgba(.5, .45, .4, .7, .15 * milky); g.add_color_stop_rgba(1, 0, 0, 0, 0)
        cr.set_source(g); cr.arc(0, 0, 1100, 0, 7); cr.fill(); cr.restore()
    r = random.Random(11)
    n = int(250 + 900 * density * milky) if milky else int(300 * density)
    for k in range(n):
        if milky and k > 250:
            d = r.gauss(0, 140); a = r.uniform(-1100, 1100)
            x = W / 2 + a * math.cos(-.6) - d * math.sin(-.6); y = H * .38 + a * math.sin(-.6) + d * math.cos(-.6)
        else:
            x, y = r.uniform(0, W), r.uniform(0, H)
        tw = .7 + .3 * math.sin(t * 3 + k)
        circle(cr, x, y, r.uniform(.6, 2.4), (1, 1, 1), r.uniform(.3, 1) * tw)

def sun_obj(cr, x, y, r, a=1.0):
    if a <= 0: return
    g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
    g.add_color_stop_rgba(0, 1, .98, .9, a); g.add_color_stop_rgba(.25, 1, .85, .45, a * .95); g.add_color_stop_rgba(.5, 1, .6, .2, a * .35); g.add_color_stop_rgba(1, 1, .5, .1, 0)
    cr.set_source(g); cr.arc(x, y, r * 4, 0, 7); cr.fill()
    g = cairo.RadialGradient(x - r * .2, y - r * .2, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, .9, a); g.add_color_stop_rgba(1, 1, .75, .3, a); cr.set_source(g); cr.arc(x, y, r, 0, 7); cr.fill()

def moon(cr, x, y, r, a):
    g = cairo.RadialGradient(x, y, r * .9, x, y, r * 2.5); g.add_color_stop_rgba(0, .8, .85, 1, .25 * a); g.add_color_stop_rgba(1, .8, .85, 1, 0)
    cr.set_source(g); cr.arc(x, y, r * 2.5, 0, 7); cr.fill()
    g = cairo.RadialGradient(x - r * .3, y - r * .3, 0, x, y, r); g.add_color_stop_rgba(0, .95, .95, .9, a); g.add_color_stop_rgba(1, .7, .7, .68, a)
    cr.set_source(g); cr.arc(x, y, r, 0, 7); cr.fill()
    for dx, dy, cr_ in ((-.3, -.2, .18), (.25, .1, .12), (-.05, .35, .1), (.35, -.35, .08)):
        circle(cr, x + dx * r, y + dy * r, cr_ * r, (.55, .55, .53), a * .6)

def dark_city(cr, t, lit_frac=0.0, S=40, cx=6, cy=6, flash=False, night=.9):
    night_sky(cr, t)
    iso = IsoR(cr, cx, cy, 0, S, oy=.5, light=(.8, .3), shadow=.05)
    lit = (lambda x, y: (int(x * 7 + y * 13) % 100) < lit_frac * 100) if lit_frac > 0 else None
    roads(iso); draw_ents(iso, CITY, lit=lit, R=60)
    iso.draw(night=night)
    return iso

# ======================= SCENES =======================
def s1(cr, t):
    space(cr, t)
    a = 1 - ease(prog(t, 2.6, 3.3))
    r = 230 * (1 - .35 * ease(prog(t, 2.6, 3.3)))
    sun_obj(cr, W / 2, 760, r, a)
    if t > 3.3: circle(cr, W / 2, 760, r, (.08, .05, .04), clamp((t - 3.3) * 3))
    draw_globe(cr, W / 2, 1180, 150, lon0=140, tilt=.3, sun=(0, -1, .3), clouds=.6)
    post(cr, t, grain=.06)

def s2(cr, t):
    if t < 14.1:
        space(cr, t)
        circle(cr, 140, 760, 110, (.08, .05, .04))
        # last sunlight traveling toward Earth
        p = prog(t, 6.8, 14.1)
        front = 140 + (W - 120 - 140) * p
        g = cairo.LinearGradient(front - 600, 0, front, 0); g.add_color_stop_rgba(0, 1, .85, .5, 0); g.add_color_stop_rgba(1, 1, .9, .6, .55)
        cr.set_source(g); cr.rectangle(max(140, front - 600), 700, min(600, front - 140), 120); cr.fill()
        circle(cr, front, 760, 16, (1, .95, .8))
        lit = p > .97
        draw_globe(cr, W - 120, 760, 100, lon0=140, tilt=.3, sun=(-1, 0, .2), clouds=.6, bright=1.0)
        sec = int(500 * (1 - prog(t, 6.8, 17.5)))
        if t > 6.8: counter(cr, t, 6.8, 14.1, f"{sec // 60} MIN {sec % 60:02d} S", 'ATÉ A LUZ ACABAR', y=1100)
        post(cr, t, grain=.06); return
    dark = t > 18.55
    if not dark:
        sky_r(cr, hexc('#6FA8DC'), hexc('#A9CBEA'), hexc('#DCEAF5'))
        iso = IsoR(cr, 6, 6, 0, keys(t, [(14.1, 38), (18.5, 44)]), oy=.5, light=(1.4, .5), shadow=.3)
        roads(iso); draw_ents(iso, CITY, R=60)
        r = random.Random(2)
        for k in range(16): person(iso, r.uniform(-1.4, 1.4) + r.choice((0, 14)), r.uniform(-6, 22), phase=t * 8 + k, jacket=r.choice(JK))
        iso.draw()
        sec = int(500 * (1 - prog(t, 6.8, 17.5)))
        counter(cr, t, 14.1, 18.55, f"{sec // 60} MIN {sec % 60:02d} S", 'ATÉ A LUZ ACABAR')
    else:
        dark_city(cr, t, S=44, night=.95)
        if t < 18.8: cr.set_source_rgba(1, 1, 1, (18.8 - t) * 3); cr.paint()
    post(cr, t)

def s3(cr, t):
    if t < 27.84:
        night_sky(cr, t, density=1.3)
        a = 1 - ease(prog(t, 21.6, 23.0))
        moon(cr, W / 2, 700, 150, a)
        post(cr, t, grain=.06); return
    if t < 35.2:
        iso = dark_city(cr, t, lit_frac=keys(t, [(27.84, .0), (31.0, .08), (34.0, .12)]), S=keys(t, [(27.84, 42), (35.2, 56)]), cx=3, cy=3, night=.92)
        r = random.Random(5)
        for k in range(5):
            x, y = iso.P(r.uniform(-4, 10), r.uniform(-4, 10), 1.2)
            ang = 1.2 + math.sin(t * 1.5 + k) * .5
            g = cairo.RadialGradient(x, y, 5, x, y, 260); g.add_color_stop_rgba(0, 1, .95, .7, .5); g.add_color_stop_rgba(1, 1, .95, .7, 0)
            cr.move_to(x, y); cr.arc(x, y, 260, ang - .25, ang + .25); cr.close_path(); cr.set_source(g); cr.fill()
        post(cr, t); return
    night_sky(cr, t)
    iso = IsoR(cr, 1, 1, .8, 120, oy=.52, light=(.8, .3), shadow=.05)
    iso.ground(hexc('#5E6B5A'))
    def pd(i, *b):
        for u in (.25, .5, .75): i.frect(b, 't', u - .01, 0, u + .01, 1, hexc('#4A5A80'), edge=0)
    iso.box(-1.5, -1, .6, 3.2, 2.2, .12, C['panel'], deco=pd); iso.box(-.1, -.1, 0, .2, .2, .6, C['metal'])
    iso.draw(night=.8)
    x, y = iso.P(.1, .1, .9); xmark(cr, x, y - 40, 130, back((t - 35.4) / .3))
    post(cr, t)

def xmark(cr, x, y, r, p=1.0, lw=30):
    cr.set_line_width(lw * p); cr.set_source_rgb(*C['red']); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(x - r, y - r); cr.line_to(x + r, y + r); cr.move_to(x + r, y - r); cr.line_to(x - r, y + r); cr.stroke()

def cold_globe(cr, t, freeze, R=430, cy=None):
    space(cr, t)
    draw_globe(cr, W / 2, cy or H / 2, R, lon0=140, tilt=.3, sun=(-.3, -.4, .9), clouds=.4, freeze=freeze, bright=.5, tint=(.75, .85, 1.1), atmo=.25, night=.3)

def s4(cr, t):
    if t < 48.41:
        cold_globe(cr, t, keys(t, [(37.3, .0), (48.4, .35)]))
        if t > 43.0:
            a = prog(t, 43.0, 43.4); lv = .7 - .5 * ease(prog(t, 43.4, 47.8))
            thermo(cr, W - 170, 1250, lv, hexc('#3B82D6'), a)
        post(cr, t, grain=.06); return
    if t < 50.5:
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#3A4150')); g.add_color_stop_rgb(1, *hexc('#1C212B')); cr.set_source(g); cr.paint()
        y0 = 820
        g = cairo.LinearGradient(0, y0, 0, y0 + 280); g.add_color_stop_rgb(0, *hexc('#B9C2CC')); g.add_color_stop_rgb(.5, *hexc('#E8EDF2')); g.add_color_stop_rgb(1, *hexc('#7E8894'))
        cr.set_source(g); cr.rectangle(-10, y0, W + 20, 280); cr.fill()
        p = ease(prog(t, 48.5, 49.6))
        g = cairo.LinearGradient(0, y0 + 30, 0, y0 + 250); g.add_color_stop_rgb(0, *hexc('#E9F6FF')); g.add_color_stop_rgb(1, *hexc('#A9D6F2'))
        cr.set_source(g); cr.rectangle(-10, y0 + 30, (W + 20) * p, 220); cr.fill()
        if t > 49.6:
            cr.set_line_width(6); cr.set_source_rgb(*hexc('#2A2F38'))
            r = random.Random(3); x = 540
            for k in range(3):
                cr.move_to(x + k * 30 - 30, y0); xx, yy = x + k * 30 - 30, y0
                for s_ in range(6): xx += r.uniform(-30, 30); yy += 45; cr.line_to(xx, yy)
                cr.stroke()
        post(cr, t); return
    # fireplace room
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#2A1E1A')); g.add_color_stop_rgb(1, *hexc('#120C0A')); cr.set_source(g); cr.paint()
    iso = IsoR(cr, 1, 1, 1.2, 92, oy=.52, light=(-1.2, -.6), shadow=.25)
    iso.ground(hexc('#6E4C36'))
    iso.box(-3, -3, 0, .3, 7, 4, hexc('#8C7462')); iso.box(-3, -3, 0, 7, .3, 4, hexc('#9A806C'))
    def fp(i, *b): i.frect(b, 'x', .2, 0, .8, .55, hexc('#1A0F0A'), edge=0)
    iso.box(-2.7, -1, 0, .9, 2.4, 2.4, hexc('#7A6A60'), deco=fp)
    person(iso, 1.2, 1.4, jacket=C['orange'])
    iso.draw()
    x, y = iso.P(-1.8, .2, .5)
    fl = 1 + .15 * math.sin(t * 19) + .08 * math.sin(t * 33)
    g = cairo.RadialGradient(x, y, 10, x, y, 700 * fl); g.add_color_stop_rgba(0, 1, .7, .3, .55); g.add_color_stop_rgba(1, 1, .5, .2, 0)
    cr.save(); cr.set_operator(cairo.OPERATOR_SCREEN); cr.set_source(g); cr.paint(); cr.restore()
    for k in range(5):
        h = 50 + 30 * math.sin(t * 17 + k * 1.3)
        cr.move_to(x - 50 + k * 22, y + 20); cr.line_to(x - 40 + k * 22, y + 20 - h); cr.line_to(x - 30 + k * 22, y + 20); cr.close_path()
        fill(cr, (1, .6 + .1 * (k % 2), .2))
    post(cr, t, warm=.12)

def field(iso, t, dead):
    iso.ground(mix(hexc('#3E5A35'), hexc('#3A3A36'), dead))
    for row in range(6):
        for k in range(8):
            x, y = -6 + k * 1.6, -5 + row * 1.9
            iso.quad(x, y, 1.2, 1.4, hexc('#4A3828'), z=.01)
            h = .9 * (1 - .6 * dead)
            iso.box(x + .2, y + .2, 0, .8, 1.0, h, mix(hexc('#4FA54A'), hexc('#6E5E44'), dead))

def s5(cr, t):
    night_sky(cr, t)
    if t < 62.26:
        iso = IsoR(cr, 1, 1, 0, keys(t, [(55.2, 46), (62.2, 56)]), oy=.55, light=(.6, .2), shadow=.06)
        field(iso, t, ease(prog(t, 56.5, 61.0))); iso.draw(night=.55); post(cr, t); return
    if t < 67.66:
        iso = IsoR(cr, 1, 1, .8, 52, oy=.55, light=(.6, .2), shadow=.06)
        iso.ground(hexc('#3A3A36'))
        dead = ease(prog(t, 62.5, 67.0))
        r = random.Random(4)
        for k in range(12):
            x, y = r.uniform(-8, 8), r.uniform(-8, 8); s = r.uniform(1.0, 1.6) * (1 - .25 * dead)
            iso.box(x - .15 * s, y - .15 * s, 0, .3 * s, .3 * s, 1.4 * s, C['trunk'])
            iso.box(x - .7 * s, y - .7 * s, 1.3 * s, 1.4 * s, 1.4 * s, 1.3 * s * (1 - .5 * dead), mix(hexc('#3E8E3A'), hexc('#7A6A44'), dead))
        iso.draw(night=.55); post(cr, t); return
    greenhouse_shot(cr, t, S=keys(t, [(67.66, 48), (71.9, 62)]))

def greenhouse_shot(cr, t, S=60, party=False):
    night_sky(cr, t)
    iso = IsoR(cr, 1.5, 1.5, 1, S, oy=.55, light=(.6, .2), shadow=.05)
    snow_ground(iso, blocks=False)
    for row in range(3):
        for k in range(4): iso.box(-1 + k * 1.1, -1.2 + row * 1.3, 0, .7, .9, .6, hexc('#4FB548'))
    person(iso, 4.6, 3.6, z=abs(math.sin(t * 7)) * .5 if party else 0, arms_up=1 if party else 0, jacket=C['orange'])
    iso.draw(night=.65)
    pts = [iso.P(x, y, z) for x, y, z in ((-1.6, -1.8, 0), (3.6, -1.8, 0), (3.6, 2.6, 0), (-1.6, 2.6, 0))]
    top = [iso.P(x, y, 2.4) for x, y, _ in ((-1.6, -1.8, 0), (3.6, -1.8, 0), (3.6, 2.6, 0), (-1.6, 2.6, 0))]
    ridge = (iso.P(-1.6, .4, 3.4), iso.P(3.6, .4, 3.4))
    cx, cy = iso.P(1, .4, 1.4)
    g = cairo.RadialGradient(cx, cy, 20, cx, cy, S * 9); g.add_color_stop_rgba(0, 1, .95, .8, .55); g.add_color_stop_rgba(1, 1, .9, .7, 0)
    cr.save(); cr.set_operator(cairo.OPERATOR_SCREEN); cr.set_source(g); cr.paint(); cr.restore()
    cr.set_source_rgba(.85, .95, 1, .18)
    for face in ((pts[1], pts[2], top[2], top[1]), (pts[2], pts[3], top[3], top[2]), (top[0], top[1], ridge[1], ridge[0]), (top[3], top[2], ridge[1], ridge[0])):
        cr.move_to(*face[0]); [cr.line_to(*q) for q in face[1:]]; cr.close_path(); cr.fill_preserve(); cr.set_source_rgba(.9, .95, 1, .6); cr.set_line_width(3); cr.stroke(); cr.set_source_rgba(.85, .95, 1, .18)
    post(cr, t)

def s6(cr, t):
    if t < 77.81:
        cold_globe(cr, t, keys(t, [(71.9, .45), (76.0, 1.05)]))
        if t > 72.0:
            thermo(cr, W - 170, 1250, .15 - .1 * prog(t, 72.8, 75.5), hexc('#3B82D6'), prog(t, 72.0, 72.4))
        post(cr, t, grain=.06); return
    g = cairo.LinearGradient(0, 0, 0, 760); g.add_color_stop_rgb(0, *NIGHT_TOP); g.add_color_stop_rgb(1, *hexc('#202A44')); cr.set_source(g); cr.rectangle(0, 0, W, 760); cr.fill()
    r = random.Random(1)
    for _ in range(120): circle(cr, r.uniform(0, W), r.uniform(0, 700), r.uniform(.6, 2), (1, 1, 1), r.uniform(.3, 1))
    layers = [(760, 840, SNOW), (840, 1250, hexc('#4A4038')), (1250, 1600, hexc('#3A302A')), (1600, H, hexc('#2A201C'))]
    for y0, y1, c in layers:
        g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgb(0, *shade(c, 1.05)); g.add_color_stop_rgb(1, *shade(c, .8)); cr.set_source(g); cr.rectangle(0, y0, W, y1 - y0); cr.fill()
    gl = .8 + .2 * math.sin(t * 2)
    g = cairo.RadialGradient(W / 2, 1820, 20, W / 2, 1820, 520); g.add_color_stop_rgba(0, 1, .75, .25, .95 * gl); g.add_color_stop_rgba(.4, 1, .35, .05, .7 * gl); g.add_color_stop_rgba(1, .6, .1, 0, 0)
    cr.set_source(g); cr.arc(W / 2, 1820, 520, 0, 7); cr.fill()
    for hx in (220, 540, 860):
        cr.set_line_width(22); cr.set_source_rgb(*hexc('#8D96A3')); cr.move_to(W / 2 + (hx - W / 2) * .3, 1600); cr.line_to(hx, 800); cr.stroke()
        cr.set_line_width(10); cr.set_dash([30, 40], -t * 160); cr.set_source_rgba(1, .55, .2, .9); cr.move_to(W / 2 + (hx - W / 2) * .3, 1600); cr.line_to(hx, 800); cr.stroke(); cr.set_dash([])
        rrect(cr, hx - 110, 640, 220, 140, 10); fill(cr, hexc('#E9E2D5'))
        cr.move_to(hx - 130, 650); cr.line_to(hx, 560); cr.line_to(hx + 130, 650); cr.close_path(); fill(cr, hexc('#B04A35'))
        rrect(cr, hx - 70, 680, 50, 45, 6); fill(cr, hexc('#FFD27A')); rrect(cr, hx + 20, 680, 50, 45, 6); fill(cr, hexc('#FFD27A'))
        g = cairo.RadialGradient(hx, 700, 10, hx, 700, 200); g.add_color_stop_rgba(0, 1, .8, .4, .35); g.add_color_stop_rgba(1, 1, .8, .4, 0); cr.set_source(g); cr.arc(hx, 700, 200, 0, 7); cr.fill()
    for k in range(10):
        ph = (t * .35 + k * .1) % 1; x = 380 + (k % 3) * 160
        circle(cr, x + math.sin(t + k) * 20, 760 - ph * 500, 30 + ph * 70, (1, 1, 1), .25 * (1 - ph))
    post(cr, t, warm=.06)

def s7(cr, t):
    pan = ease(prog(t, 95.0, 97.5))
    cr.save(); cr.translate(0, -1350 * pan)
    g = cairo.LinearGradient(0, 0, 0, 340); g.add_color_stop_rgb(0, *NIGHT_TOP); g.add_color_stop_rgb(1, *hexc('#1A2240')); cr.set_source(g); cr.rectangle(0, 0, W, 340); cr.fill()
    g = cairo.LinearGradient(0, 340, 0, 3300); g.add_color_stop_rgb(0, *hexc('#1B4F78')); g.add_color_stop_rgb(.4, *hexc('#0C2A48')); g.add_color_stop_rgb(1, *hexc('#030A16')); cr.set_source(g); cr.rectangle(0, 340, W, 2960); cr.fill()
    ice_h = 180 * ease(prog(t, 87.3, 89.2))
    g = cairo.LinearGradient(0, 340, 0, 340 + ice_h + 1); g.add_color_stop_rgb(0, *hexc('#F1F7FC')); g.add_color_stop_rgb(1, *hexc('#A8D3EE')); cr.set_source(g); cr.rectangle(0, 340, W, ice_h); cr.fill()
    if t > 89.6:
        a = prog(t, 89.6, 90.0)
        for k in range(6): arrow(cr, 120 + k * 170, 900, 120 + k * 170, 620, hexc('#FFB45A'), w=10, a=a * .8)
    # sea floor + vent
    fy = 3000
    cr.move_to(0, fy);
    for x in range(0, W + 60, 60): cr.line_to(x, fy - 30 * math.sin(x * .01) - (120 if 380 < x < 700 else 0))
    cr.line_to(W, 3300); cr.line_to(0, 3300); cr.close_path(); fill(cr, hexc('#2A2A30'))
    vx, vy = 540, fy - 120
    cr.move_to(vx - 90, vy + 40); cr.line_to(vx - 40, vy - 260); cr.line_to(vx + 40, vy - 260); cr.line_to(vx + 90, vy + 40); cr.close_path(); fill(cr, hexc('#3B3530'))
    g = cairo.RadialGradient(vx, vy - 250, 5, vx, vy - 250, 180); g.add_color_stop_rgba(0, 1, .55, .15, .9); g.add_color_stop_rgba(1, 1, .3, 0, 0); cr.set_source(g); cr.arc(vx, vy - 250, 180, 0, 7); cr.fill()
    for k in range(26):
        ph = (t * .5 + k / 26) % 1
        circle(cr, vx + math.sin(k * 2.1 + t) * (20 + ph * 140), vy - 270 - ph * 700, 26 + ph * 90, (.12, .1, .1), .55 * (1 - ph))
    for k in range(9):
        x = vx - 300 + k * 70 + (40 if k > 4 else 0)
        h = 90 + 30 * math.sin(k)
        cr.set_line_width(14); cr.set_source_rgb(.9, .88, .85); cr.move_to(x, fy - 60); cr.line_to(x + math.sin(t * 2 + k) * 8, fy - 60 - h); cr.stroke()
        circle(cr, x + math.sin(t * 2 + k) * 8, fy - 60 - h, 14, C['red'])
    if t > 101.3:
        r = random.Random(2); a = prog(t, 101.3, 102.0)
        for k in range(160):
            x = vx + r.gauss(0, 260); y = vy - 100 + r.gauss(0, 200)
            circle(cr, x, y, 4, hexc('#9BF2A0'), a * .8)
    r = random.Random(9)
    for k in range(7):
        x = (r.uniform(0, W) + t * r.uniform(30, 70)) % (W + 200) - 100; y = fy - r.uniform(200, 700)
        cr.save(); cr.translate(x, y); cr.scale(1, .55); circle(cr, 0, 0, 34, hexc('#7FA2B8')); cr.restore()
        cr.move_to(x - 30, y); cr.line_to(x - 60, y - 18); cr.line_to(x - 60, y + 18); cr.close_path(); fill(cr, hexc('#6A8CA2'))
    cr.restore()
    post(cr, t)

def bulb(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#14161C')); g.add_color_stop_rgb(1, *hexc('#05060A')); cr.set_source(g); cr.paint()
    cx, cy = W / 2, 820
    g = cairo.RadialGradient(cx, cy, 20, cx, cy, 700); g.add_color_stop_rgba(0, 1, .9, .6, .6); g.add_color_stop_rgba(1, 1, .8, .5, 0); cr.set_source(g); cr.paint()
    g = cairo.RadialGradient(cx - 60, cy - 80, 10, cx, cy, 230); g.add_color_stop_rgb(0, 1, 1, .95); g.add_color_stop_rgb(.7, 1, .9, .6); g.add_color_stop_rgb(1, 1, .8, .45)
    cr.set_source(g); cr.arc(cx, cy, 230, 0, 7); cr.fill()
    cr.rectangle(cx - 110, cy + 190, 220, 160); fill(cr, hexc('#9AA3AE'))
    for k in range(4): cr.rectangle(cx - 110, cy + 210 + k * 36, 220, 12); fill(cr, hexc('#6E7884'))

def layers_char(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#C9D6E3')); g.add_color_stop_rgb(1, *hexc('#8FA3B8')); cr.set_source(g); cr.paint()
    front_char(cr, W / 2, 1950, 1450, 'happy', t=t, jacket=C['orange'])
    n = int(1 + 4 * prog(t, wt('Muita') - .1, wt('Muita') + 1.3))
    cols = [hexc(c) for c in ('#2F5DA8', '#2FAF6A', '#8E6CD8', '#E2453C', '#F2C13D')]
    for k in range(n):
        w = 560 + k * 90; h = 520 + k * 50
        rrect(cr, W / 2 - w / 2, 1060 - k * 20, w, h, 160); fill(cr, cols[k])
        rrect(cr, W / 2 - w / 2 + w * .55, 1060 - k * 20, w * .45, h, 160); fill(cr, shade(cols[k], .88))

def s8(cr, t):
    cuts = [(wt('Gerador', 106), 'g'), (wt('Lenha', 106), 'l'), (wt('Estufa', 106), 'e'), (wt('Lâmpada', 106), 'b'), (wt('Muita', 106), 'r')]
    cur = cuts[0][1]
    for t0, k in cuts:
        if t >= t0 - .05: cur = k
    if cur == 'b': bulb(cr, t); post(cr, t); return
    if cur == 'r': layers_char(cr, t); post(cr, t); return
    if cur == 'e': greenhouse_shot(cr, t, S=110); return
    night_sky(cr, t)
    iso = IsoR(cr, 0, 0, .7, 150, oy=.52, light=(.8, .3), shadow=.08)
    snow_ground(iso, blocks=False)
    if cur == 'g':
        def gd(i, *b): i.frect(b, 'x', .1, .3, .5, .8, C['dark']); i.frect(b, 'y', .15, .5, .85, .8, hexc('#2D7F3E'))
        iso.box(-1, -.7, 0, 2.0, 1.4, 1.3, hexc('#F2B33D'), deco=gd)
    else:
        for lv in range(3):
            for k in range(4 - lv): iso.box(-1.5 + k * .8 + lv * .4, -1, lv * .55, .7, 2.4, .55, C['brown'], top=hexc('#E3B77E'))
    iso.draw(night=.45); post(cr, t)

def s9(cr, t): greenhouse_shot(cr, t, S=70, party=True); confetti(cr, t, 111.89)

def switch(cr, t, flip):
    cx, cy = W / 2, 1120
    sh = cairo.RadialGradient(cx + 20, cy + 30, 50, cx + 20, cy + 30, 400); sh.add_color_stop_rgba(0, 0, 0, 0, .6); sh.add_color_stop_rgba(1, 0, 0, 0, 0); cr.set_source(sh); cr.arc(cx, cy, 420, 0, 7); cr.fill()
    g = cairo.LinearGradient(cx - 200, cy - 300, cx + 200, cy + 300); g.add_color_stop_rgb(0, *hexc('#F4F4F2')); g.add_color_stop_rgb(1, *hexc('#C8C8C4'))
    rrect(cr, cx - 200, cy - 300, 400, 600, 40); cr.set_source(g); cr.fill()
    rrect(cr, cx - 80, cy - 170, 160, 340, 24); fill(cr, hexc('#B0B0AC'))
    up = 1 - flip
    g = cairo.LinearGradient(0, cy - 160, 0, cy + 160); g.add_color_stop_rgb(0, *hexc('#FFFFFF')); g.add_color_stop_rgb(1, *hexc('#D4D4D0'))
    rrect(cr, cx - 66, cy - 156 + (1 - up) * 150, 132, 160, 20); cr.set_source(g); cr.fill()
    circle(cr, cx, cy - 250, 14, hexc('#9A9A96')); circle(cr, cx, cy + 250, 14, hexc('#9A9A96'))

def s10(cr, t):
    if t < 120.6:
        night_sky(cr, t, density=1.0, milky=prog(t, 115.5, 117.5))
        cr.move_to(0, 1650)
        for x in range(0, W + 40, 40): cr.line_to(x, 1650 - 40 * math.sin(x * .006))
        cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); fill(cr, hexc('#0A0D16'))
        cr.save(); cr.translate(W / 2, 1600)
        rrect(cr, -45, -260, 90, 130, 30); fill(cr, hexc('#0A0D16')); rrect(cr, -70, -150, 140, 160, 30); fill(cr, hexc('#0A0D16'))
        cr.restore()
        post(cr, t, grain=.07); return
    space(cr, t)
    switch(cr, t, ease(prog(t, 122.6, 122.9)))
    post(cr, t, grain=.06)

SCENES = [(0, 4.62, s1), (4.62, 20.5, s2), (20.5, 37.28, s3), (37.28, 55.21, s4), (55.21, 71.9, s5),
          (71.9, 86.69, s6), (86.69, 106.55, s7), (106.55, 111.89, s8), (111.89, 115.57, s9), (115.57, 125.0, s10)]
END = 125.0

def overlays(cr, t):
    G, R_, Y = C['green'], C['red'], C['yellow']
    pill(cr, t, wt('150'), 14.1, '150 MILHÕES DE KM', W / 2, 330, Y)
    pill(cr, t, wt('Lua'), 27.84, 'LUA APAGADA', W / 2, 330, R_)
    title(cr, t, wt('luz', 27), 35.2, 'LUZ ARTIFICIAL', y=330)
    pill(cr, t, wt('Painel'), 37.28, 'PAINEL SOLAR: INÚTIL', W / 2, 330, R_)
    counter(cr, t, 42.97, 48.41, 'SEMANA 1')
    if 44.0 <= t < 48.41:
        v = int(15 - 33 * ease(prog(t, 44.0, 47.8)))
        text_center(cr, f"{v} °C", W / 2, 1180, 170, hexc('#9FD0FF'), stroke=C['dark'], sw=16)
    pill(cr, t, wt('canos'), 50.5, 'CANOS CONGELADOS', W / 2, 330, R_)
    title(cr, t, wt('calor', 50), 55.21, 'CALOR', y=330)
    pill(cr, t, wt('fotossíntese'), 62.26, 'SEM FOTOSSÍNTESE', W / 2, 330, R_)
    pill(cr, t, wt('reservas'), 67.66, 'ÁRVORES MORRENDO', W / 2, 330, R_)
    title(cr, t, wt('estufas'), 71.9, 'ESTUFA', y=330)
    counter(cr, t, 71.95, 77.81, 'ANO 1')
    if 72.8 <= t < 77.81:
        v = int(-18 - 52 * ease(prog(t, 72.8, 75.8)))
        text_center(cr, f"{v} °C", W / 2, 1600, 170, hexc('#9FD0FF'), stroke=C['dark'], sw=16)
    title(cr, t, wt('vulcânicas'), 86.69, 'CALOR DA TERRA', y=330)
    pill(cr, t, wt('Islândia'), 86.69, 'EX.: ISLÂNDIA', W / 2, 460, Y)
    pill(cr, t, wt('cobertor'), 95.0, 'GELO = COBERTOR', W / 2, 1050, C['orange'])
    pill(cr, t, 91.95, 95.0, 'ÁGUA LÍQUIDA', W / 2, 1180, hexc('#7FD3FF'))
    title(cr, t, wt('hidrotermais'), 101.3, 'VIDA SEM SOL', y=330)
    pill(cr, t, wt('bactérias'), 106.55, 'BACTÉRIAS', W / 2, 330, G)
    for a, lbl in (('Gerador', 'GERADOR'), ('Lenha', 'LENHA'), ('Estufa', 'ESTUFA'), ('Lâmpada', 'LÂMPADA'), ('Muita', 'MUITA ROUPA')):
        t0 = wt(a, 106); nx = {'Gerador': wt('Lenha', 106), 'Lenha': wt('Estufa', 106), 'Estufa': wt('Lâmpada', 106), 'Lâmpada': wt('Muita', 106), 'Muita': 111.89}[a]
        pill(cr, t, t0, nx, lbl, W / 2, 330, G)
    title(cr, t, 111.95, 115.57, 'PARABÉNS!', y=360, size=150, sub='Você sobreviveu ao mundo sem Sol')
    if t >= 121.3:
        title(cr, t, 121.3, 999, 'COMENTE', y=420, size=120, tilt=0, col=C['white'])
        title(cr, max(t, 121.55), 121.55, 999, '"LUZ"', y=600, size=170, tilt=-.07)
        if t > 121.9:
            text_center(cr, 'se você sobreviveria', W / 2, 770, 64, C['white'], stroke=C['dark'], sw=10, scale=back((t - 121.9) / .3))
    if t < 124.0: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    else: SCENES[-1][2](cr, t)
    overlays(cr, t)
