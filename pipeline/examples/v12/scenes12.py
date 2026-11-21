import os
import sys, math, random, json
sys.path.insert(0, '/home/claude/vid'); sys.path.insert(0, '/home/claude/vid5'); sys.path.append('/home/claude/vid6')
import cairo
from engine import *
from real import *
from scenes6 import capsule

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.json')))
DUR = 102.191
END = DUR + 1.6
R_STARS = random.Random(9)
FIELD = [(R_STARS.uniform(0, W), R_STARS.uniform(0, H), R_STARS.uniform(1, 3.2), R_STARS.uniform(.4, 1)) for _ in range(380)]

def warped_space(cr, t, cx, cy, Rbh, pull=1.0, red=0.0):
    cr.set_source_rgb(.01, .01, .03); cr.paint()
    for x, y, r, a in FIELD:
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy) + 1e-3
        if Rbh > 0:
            k = 1 + pull * (Rbh * 1.6) ** 2 / (d * d)
            nd = d * k  # lensing pushes apparent position out
            x2, y2 = cx + dx / d * nd, cy + dy / d * nd
        else: x2, y2 = x, y
        col = mix((1, 1, 1), (1, .4, .3), red)
        circle(cr, x2, y2, r, col, a * (.7 + .3 * math.sin(t * 2 + x)))

def black_hole(cr, cx, cy, R, t, disk=1.0, tilt=.28):
    # glow
    g = cairo.RadialGradient(cx, cy, R * .9, cx, cy, R * 3.2); g.add_color_stop_rgba(0, 1, .6, .2, .55 * disk); g.add_color_stop_rgba(1, 1, .4, .1, 0)
    cr.set_source(g); cr.arc(cx, cy, R * 3.2, 0, 7); cr.fill()
    def ring(back):
        cr.save(); cr.translate(cx, cy); cr.scale(1, tilt)
        for k in range(28):
            rr = R * (1.35 + k * .055)
            a0 = (t * (2.2 - k * .04)) % 6.28
            col = mix(hexc('#FFF2C2'), hexc('#E2561E'), k / 28)
            cr.set_line_width(R * .07)
            if back: cr.arc(cx * 0, 0, rr, math.pi, 2 * math.pi)
            else: cr.arc(0, 0, rr, 0, math.pi)
            cr.set_source_rgba(*col, disk * (.55 - k * .015) * (.8 + .2 * math.sin(a0 + k))); cr.stroke()
        cr.restore()
    ring(True)
    # lensed upper arc of disk over the hole
    cr.save(); cr.translate(cx, cy)
    for k in range(10):
        cr.set_line_width(R * .06); cr.set_source_rgba(*mix(hexc('#FFE7A8'), hexc('#F07A2A'), k / 10), disk * (.5 - k * .04))
        cr.arc(0, 0, R * (1.12 + k * .05), math.pi * 1.05, math.pi * 1.95); cr.stroke()
    cr.restore()
    circle(cr, cx, cy, R, (0, 0, 0))
    cr.set_line_width(R * .04); cr.set_source_rgba(1, .85, .55, .9 * disk); cr.arc(cx, cy, R * 1.03, 0, 7); cr.stroke()
    ring(False)

def astro(cr, x, y, s, stretch=1.0, rot=0.0, tint=0.0, a=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(1 / math.sqrt(stretch), stretch)
    if tint or a < 1:
        cr.push_group()
    W_, G_ = hexc('#F2F2F0'), hexc('#C9CCD2')
    u = s / 10
    rrect(cr, -1.8 * u, -2 * u, 3.6 * u, 4.2 * u, 1 * u); fill(cr, W_)
    rrect(cr, -2.4 * u, -1.6 * u, 1.0 * u, 3.2 * u, .5 * u); fill(cr, G_)
    rrect(cr, 1.4 * u, -1.6 * u, 1.0 * u, 3.2 * u, .5 * u); fill(cr, G_)
    rrect(cr, -1.5 * u, 2 * u, 1.2 * u, 2.8 * u, .5 * u); fill(cr, W_)
    rrect(cr, .3 * u, 2 * u, 1.2 * u, 2.8 * u, .5 * u); fill(cr, W_)
    circle(cr, 0, -3.4 * u, 1.9 * u, W_)
    cr.save(); cr.translate(0, -3.4 * u); cr.scale(1, .75); circle(cr, 0, 0, 1.4 * u, hexc('#E0A92E')); cr.restore()
    circle(cr, -.5 * u, -3.8 * u, .4 * u, (1, 1, 1), .6)
    if tint or a < 1:
        cr.pop_group_to_source(); cr.paint_with_alpha(a)
        if tint:
            cr.set_operator(cairo.OPERATOR_ATOP); cr.set_source_rgba(.9, .1, .05, tint * .7)
            cr.rectangle(-5 * u, -6 * u, 10 * u, 12 * u); cr.fill()
    cr.restore()

def ship(cr, x, y, s, t, alarm=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-60, 120); cr.line_to(-60, -40); cr.curve_to(-60, -120, 0, -170, 0, -170); cr.curve_to(0, -170, 60, -120, 60, -40); cr.line_to(60, 120); cr.close_path(); fill(cr, hexc('#E8ECF2'))
    circle(cr, 0, -40, 30, hexc('#3B82D6')); circle(cr, -8, -48, 10, (1, 1, 1), .6)
    for sx in (-1, 1):
        cr.move_to(sx * 60, 40); cr.line_to(sx * 110, 140); cr.line_to(sx * 60, 120); cr.close_path(); fill(cr, C['red'])
    fl = 40 + 20 * math.sin(t * 30)
    cr.move_to(-35, 120); cr.line_to(0, 120 + fl * 2); cr.line_to(35, 120); cr.close_path(); fill(cr, C['orange'], .9)
    if alarm: circle(cr, 0, -110, 14, C['red'], alarm)
    cr.restore()

def galaxy(cr, cx, cy, R, t, glow=1.0):
    r = random.Random(4)
    for k in range(900):
        arm = k % 2; d = r.uniform(.05, 1) ** .7
        a = arm * math.pi + d * 5.5 + t * .05 + r.gauss(0, .25)
        x, y = cx + math.cos(a) * d * R, cy + math.sin(a) * d * R * .45
        col = mix(hexc('#FFE7C2'), hexc('#8EB8FF'), d)
        circle(cr, x, y, r.uniform(1, 3.5), col, .8 * (1 - d * .5))
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, R * .35); g.add_color_stop_rgba(0, 1, .9, .7, .9 * glow); g.add_color_stop_rgba(1, 1, .8, .5, 0)
    cr.set_source(g); cr.arc(cx, cy, R * .35, 0, 7); cr.fill()

def clock_small(cr, x, y, R, ang, col=None):
    circle(cr, x, y, R, C['dark']); circle(cr, x, y, R * .86, col or C['white'])
    cr.set_source_rgb(*C['dark']); cr.set_line_width(R * .1); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(x, y); cr.line_to(x + math.sin(ang) * R * .65, y - math.cos(ang) * R * .65); cr.stroke()
    cr.move_to(x, y); cr.line_to(x + math.sin(ang / 12) * R * .4, y - math.cos(ang / 12) * R * .4); cr.stroke()

# ---------------- scenes ----------------
def s1(cr, t):
    bx, by = W / 2, 520
    Rb = keys(t, [(0, 30), (3.9, 60), (6.5, 150)])
    warped_space(cr, t, bx, by, Rb, pull=.6)
    black_hole(cr, bx, by, Rb, t, disk=prog(t, 3.8, 5.0))
    alarm = .5 + .5 * math.sin(t * 12) if t > 2.6 else 0
    shake = math.sin(t * 40) * 8 * (1 if t > 2.6 else 0)
    ship(cr, W / 2 + shake, 1250 - (t * 10), 1.4, t, alarm)
    if t > 2.6:
        cr.set_source_rgba(1, 0, 0, .18 * alarm); cr.paint()
    post(cr, t)

def s2(cr, t):
    bx, by = W / 2, 560
    if t < 13.2:
        Rb = keys(t, [(6.5, 150), (9.8, 170), (12.3, 120)])
        warped_space(cr, t, bx, by, Rb, pull=.8)
        black_hole(cr, bx, by, Rb, t)
        if t > 11.4:
            a = prog(t, 11.4, 11.9)
            r = random.Random(2); x = 120
            cr.set_source_rgba(.6, .7, .9, .85 * a)
            while x < W - 120:
                w = r.uniform(40, 90); h = r.uniform(120, 420)
                cr.rectangle(x, 1250 - h, w, h); cr.fill(); x += w + 8
            cr.set_line_width(6); cr.set_source_rgba(1, 1, 1, a)
            cr.move_to(bx - Rb, by + Rb + 60); cr.line_to(bx - Rb, by + Rb + 90); cr.line_to(bx + Rb, by + Rb + 90); cr.line_to(bx + Rb, by + Rb + 60); cr.stroke()
        post(cr, t); return
    # spaghettification: astronaut feet toward hole (below)
    by2 = 1700
    warped_space(cr, t, W / 2, by2, 260, pull=.6)
    black_hole(cr, W / 2, by2, 260, t)
    st = 1 + 3.2 * ease(prog(t, 14.3, 21.5)) + .25 * math.sin(t * 6) * prog(t, 16, 18)
    y = 820 + 200 * ease(prog(t, 13.2, 27))
    astro(cr, W / 2, y, 300, stretch=st, rot=math.sin(t) * .05)
    if 14.0 < t < 17.4:
        a = prog(t, 14.0, 14.4)
        for yy, L, col in ((y - 200 * st, 60, C['yellow']), (y + 160 * st, 160, C['red'])):
            cr.set_source_rgba(*col, a); cr.set_line_width(18); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(W / 2 + 260, yy); cr.line_to(W / 2 + 260, yy + L); cr.stroke()
            cr.move_to(W / 2 + 230, yy + L); cr.line_to(W / 2 + 260, yy + L + 40); cr.line_to(W / 2 + 290, yy + L); cr.close_path(); fill(cr, col, a)
    post(cr, t)

def s3(cr, t):
    if t < 37.0:
        cr.set_source_rgb(.01, .01, .03); cr.paint()
        for x, y, r, a in FIELD: circle(cr, x, y, r * .7, (1, 1, 1), a * .6)
        z = keys(t, [(28.4, 700), (32.2, 900), (37.0, 2600)])
        galaxy(cr, W / 2, 900, z, t)
        if t > 35.0:
            Rb = 60 * ease(prog(t, 35.0, 37.0))
            black_hole(cr, W / 2, 900, Rb, t)
        if 32.0 < t < 35:
            a = prog(t, 32.0, 32.4)
            cr.set_source_rgba(1, 1, 1, a); cr.set_line_width(5); cr.arc(W / 2, 900, 90, 0, 7); cr.stroke()
            text_center(cr, 'VOCÊ ESTÁ AQUI →', W / 2 - 260, 900 + z * .25, 40, C['white'], alpha=a * .0)
        post(cr, t); return
    bx, by = W / 2, 700
    Rb = keys(t, [(37, 380), (46.6, 520)])
    warped_space(cr, t, bx, by, Rb * .6, pull=.6)
    black_hole(cr, bx, by, Rb, t)
    # horizon dashed line & astronaut drifting in calmly
    cr.set_dash([24, 16]); cr.set_line_width(6); cr.set_source_rgba(1, 1, 1, .8 * prog(t, 40.6, 41.2))
    cr.arc(bx, by, Rb * 1.0, 0, 7); cr.stroke(); cr.set_dash([])
    ay = keys(t, [(37, 1500), (43.0, by + Rb * .95), (46.6, by + Rb * .6)])
    astro(cr, W / 2 + 120 * math.sin(t * .4), ay, 200, rot=math.sin(t * .8) * .2, a=1 - prog(t, 45.0, 46.5) * .6)
    if t > 42.5:
        text_center(cr, '...', W / 2 + 200, ay - 160, 80, C['white'], alpha=prog(t, 42.5, 43))
    post(cr, t)

def s4(cr, t):
    # inside: all paths lead to the center
    cr.set_source_rgb(0, 0, 0); cr.paint()
    cx, cy = W / 2, 900
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 900); g.add_color_stop_rgba(0, .9, .3, .1, .0); g.add_color_stop_rgba(.6, .4, .1, .05, .35); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    cr.set_source(g); cr.paint()
    n = 18
    for k in range(n):
        a0 = k / n * 6.28
        ph = ((t - 46.6) * .5 + k / n) % 1
        cr.set_line_width(8); cr.set_source_rgba(1, .9, .4, .8 * prog(t, 49.8, 50.4))
        r1 = 900 * (1 - ph); r2 = max(0, r1 - 160)
        cr.move_to(cx + math.cos(a0 + ph * 1.5) * r1, cy + math.sin(a0 + ph * 1.5) * r1)
        cr.line_to(cx + math.cos(a0 + ph * 1.5 + .2) * r2, cy + math.sin(a0 + ph * 1.5 + .2) * r2); cr.stroke()
    circle(cr, cx, cy, 30 + 6 * math.sin(t * 5), (1, .95, .8), .9)
    if t < 50:
        cr.set_line_width(14); cr.set_source_rgba(*C['red'], .9); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        x0 = W / 2; y0 = 1300
        cr.move_to(x0 - 150, y0 - 150); cr.line_to(x0 + 150, y0 + 150); cr.move_to(x0 + 150, y0 - 150); cr.line_to(x0 - 150, y0 + 150); cr.stroke()
    post(cr, t, vignette=.7)

def s5(cr, t):
    bx, by = W / 2, 650
    warped_space(cr, t, bx, by, 300, pull=.6)
    black_hole(cr, bx, by, 360, t)
    p = ease(prog(t, 58.0, 66.5))
    ay = keys(t, [(55.5, 1500), (66.5, by + 380)])
    fade = prog(t, 66.8, 68.8)
    astro(cr, W / 2, ay, 220 * (1 - .3 * p), stretch=1 - .45 * p, tint=prog(t, 64.5, 66.0), a=1 - fade)
    # observer far away with telescope eye + frozen clock
    clock_small(cr, 200, 1700, 90, (2 * math.pi) * (1 - math.exp(-(t - 55.5) * .25)) * 4)
    text_center(cr, 'DE FORA', 200, 1560, 44, C['white'], stroke=C['dark'], sw=8)
    if t > 61.6:
        a = prog(t, 61.6, 62)
        for k in range(3):
            ph = ((t * .3) + k / 3) % 1
            cr.set_source_rgba(1, 1, 1, a * (1 - ph) * .6); cr.set_line_width(5)
            cr.arc(W / 2, ay, 140 + ph * 160 * (1 - p), 0, 7); cr.stroke()
    post(cr, t)

def s6(cr, t):
    cr.set_source_rgb(0, 0, 0); cr.paint()
    shrink = ease(prog(t, 73.5, 77.5))
    cx, cy = W / 2, 620
    rad = keys(t, [(69.4, 1400), (73.5, 1400), (77.5, 230)])
    cr.save(); cr.arc(cx, cy, rad, 0, 7); cr.clip()
    rr_ = random.Random(21)
    for k in range(420):
        an = rr_.uniform(0, 6.283); dd = math.sqrt(rr_.random()); r = rr_.uniform(1, 3); a = rr_.uniform(.4, 1)
        x2 = cx + math.cos(an) * dd * rad; y2 = cy + math.sin(an) * dd * rad
        circle(cr, x2, y2, max(1, r * (1 + shrink)), (1, .95, .85), a)
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, rad); g.add_color_stop_rgba(0, 1, 1, 1, .25 * shrink); g.add_color_stop_rgba(1, .6, .7, 1, .1)
    cr.set_source(g); cr.paint()
    cr.restore()
    if shrink > 0:
        cr.set_line_width(10); cr.set_source_rgba(1, .9, .7, shrink); cr.arc(cx, cy, rad, 0, 7); cr.stroke()
    astro(cr, W / 2, 1300, 340, rot=math.sin(t * .6) * .1)
    clock_small(cr, W - 200, 1700, 90, (t - 69.4) * 2 * math.pi / 4)
    text_center(cr, 'PRA VOCÊ', W - 200, 1560, 44, C['white'], stroke=C['dark'], sw=8)
    post(cr, t)

def s7(cr, t):
    big = t > 86.0
    warped_space(cr, t, W / 2, 800, 200 if not big else 120, pull=.6)
    black_hole(cr, W / 2, 800, 260 if not big else keys(t, [(86, 260), (88.5, 470)]), t)
    if not big:
        secs = max(0, 60 - (t - 82.4) * 18) if t > 82.4 else 60
        p = prog(t, 81.0, 81.5)
        rrect(cr, W / 2 - 230, 1550, 460, 170, 40); fill(cr, (0, 0, 0), .6 * p)
        text_center(cr, f'00:{int(secs):02d}', W / 2, 1635, 110, C['white'] if secs > 10 else C['red'], alpha=p)
    post(cr, t)

def s8(cr, t):
    cr.set_source_rgb(0, 0, 0); cr.paint()
    r = random.Random(int(t * 8))
    glitch = prog(t, 93.5, 98.5)
    eqs = ['E = mc²', 'F = ma', 'G·m₁m₂/r²', 'Δt', '∞', 'ρ → ∞', '?']
    for k, e in enumerate(eqs):
        x = W / 2 + math.cos(k * .9 + t * .4) * 330; y = 900 + math.sin(k * 1.3 + t * .4) * 420
        if glitch > 0: x += r.uniform(-30, 30) * glitch; y += r.uniform(-20, 20) * glitch
        text_center(cr, e, x, y, 70, C['white'], alpha=(1 - glitch * .6))
    circle(cr, W / 2, 900, 18 + 10 * math.sin(t * 7), (1, 1, 1))
    g = cairo.RadialGradient(W / 2, 900, 0, W / 2, 900, 200); g.add_color_stop_rgba(0, 1, 1, 1, .6); g.add_color_stop_rgba(1, 1, 1, 1, 0); cr.set_source(g); cr.paint()
    if glitch > 0:
        for k in range(6):
            y = r.uniform(0, H); h = r.uniform(10, 60)
            cr.save(); cr.rectangle(0, y, W, h); cr.clip(); cr.set_source_rgba(r.random(), .2, r.random(), .25 * glitch); cr.paint(); cr.restore()
    if t > 92.0 and t < 93.5:
        for k in range(5):
            text_center(cr, '?', 200 + k * 170, 600 + (k % 2) * 120, 140, C['yellow'], stroke=C['dark'], sw=10, scale=back((t - 92 - k * .08) / .3))
    post(cr, t)

def s9(cr, t):
    warped_space(cr, t, W / 2, 1150, 260, pull=.7)
    black_hole(cr, W / 2, 1150, 300, t)
    post(cr, t)

SCENES = [(0, 6.5, s1), (6.5, 28.4, s2), (28.4, 46.6, s3), (46.6, 55.5, s4), (55.5, 69.4, s5), (69.4, 79.2, s6),
          (79.2, 90.3, s7), (90.3, 99.6, s8), (99.6, 999, s9)]

def overlays(cr, t):
    R_, Y, G = C['red'], C['yellow'], C['green']
    pill(cr, t, 2.6, 6.4, 'ALERTA: BURACO NEGRO', W / 2, 330, R_)
    title(cr, t, 8.4, 9.8, 'O TAMANHO IMPORTA', y=330)
    pill(cr, t, 11.4, 13.1, 'DO TAMANHO DE UMA CIDADE', W / 2, 330, Y)
    title(cr, t, 19.4, 23.0, 'MACARRÃO!', y=330)
    title(cr, t, 23.0, 28.3, 'ESPAGUETIFICAÇÃO', y=330, size=100, col=hexc('#FF9A5A'))
    title(cr, t, 30.3, 33.7, 'GIGANTE', y=330)
    counter(cr, t, 33.7, 37.0, '4 MILHÕES', 'DE SÓIS')
    pill(cr, t, 40.8, 46.5, 'HORIZONTE DE EVENTOS', W / 2, 330, C['white'])
    title(cr, t, 48.4, 50.2, 'SEM VOLTA', y=330, col=R_)
    pill(cr, t, 50.2, 55.4, 'NEM A LUZ ESCAPA', W / 2, 330, Y)
    title(cr, t, 56.8, 60.0, 'BIZARRO', y=330)
    pill(cr, t, 60.0, 65.6, 'VOCÊ NUNCA ENTRA', W / 2, 330, Y)
    title(cr, t, 65.8, 69.3, 'CONGELADO NA BORDA', y=330, size=96, col=R_)
    pill(cr, t, 70.6, 73.0, 'O TEMPO PASSA NORMAL', W / 2, 330, G)
    pill(cr, t, 74.2, 79.1, 'O UNIVERSO NUM CÍRCULO', W / 2, 330, Y)
    counter(cr, t, 82.4, 86.0, '~1 MINUTO', 'ATÉ O CENTRO')
    counter(cr, t, 87.4, 90.2, 'HORAS', 'EM BURACOS MAIORES')
    title(cr, t, 92.0, 93.5, 'NINGUÉM SABE', y=330)
    pill(cr, t, 94.5, 99.5, 'A FÍSICA PARA DE FUNCIONAR', W / 2, 330, R_)
    if t >= 99.6:
        title(cr, t, 99.6, 999, 'VOCÊ ENTRARIA?', y=420, size=120, tilt=-.05)
        if t > 101.5: title(cr, t, 101.5, 999, 'COMENTA', y=580, size=110, tilt=0, col=C['white'])
    if t < DUR + .3: caption(cr, t, WORDS)

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cr, t); break
    overlays(cr, t)
