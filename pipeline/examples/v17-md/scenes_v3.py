import os, sys, math, random
pass  # md.py fica em pipeline/lib
import cairo
from engine import *
from real import post, IsoR
from scenes import tree as _t, stars
from md import *

D = os.path.dirname(os.path.abspath(__file__))
WORDS = load_words(D)
DUR = 73.169
END = DUR + 1.5
ZC = hexc('#B9C8FF')

def zzz(cr, t, x, y, s=1.0, a=1.0, seed=0):
    for k in range(3):
        ph = ((t * .6 + k / 3 + seed * .17) % 1)
        label(cr, 'z', x + ph * 60 * s + k * 6, y - ph * 120 * s, (30 + k * 12) * s, ZC, 'b', a * (1 - ph))

def city(iso, t, lights=None, night=False, seed=2, ext=4, skip=None):
    r = random.Random(seed)
    for gx in range(-ext, ext + 1):
        for gy in range(-ext, ext + 1):
            if gx == 0 or gy == 0: continue
            if skip and skip(gx, gy): continue
            x, y = gx * 4.5, gy * 4.5
            fl = r.randint(2, 7)
            col = r.choice([hexc('#8FA3B8'), hexc('#6E829A'), hexc('#B7A58F'), hexc('#9AA7C7')])
            idx = (gx + ext) * 20 + gy
            lit = (lambda rr, cc, f, idx=idx: ((rr * 3 + cc + idx) % 4 != 0) and (lights is None or lights(idx))) if night else None
            building(iso, x - 1.5, y - 1.5, 3, 3, fl, col, lit=lit)

def sleeper(iso, x, y, jacket):
    """pessoa deitada (caixas) no chão."""
    iso.box(x, y, 0, 1.6, .55, .35, jacket); iso.box(x + 1.6, y + .05, 0, .45, .45, .4, C['skin'])
    iso.box(x - .5, y + .05, 0, .5, .45, .25, C['pants'])

def s0(cr, t):
    bg(cr, t, 'noite')
    zzz(cr, 2.0, 760, 980, 2.4); zzz(cr, 3.1, 300, 1150, 1.8, seed=3)
    front_char(cr, W / 2, 1560, 640, expr='shock', t=t)
    label(cr, 'SÓ VOCÊ', W / 2, 340, 170, (1, 1, 1), 'b')
    label(cr, 'ACORDADO', W / 2, 540, fit_s(cr, 'ACORDADO', 190, 980), C['yellow'], 'b')
    post(cr, t, vignette=.5)

def s1(cr, t):
    bg(cr, t, 'gelo', grid=False)
    S = keys(t, [(.4, 44), (8.8, 56)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.6)
    iso.quad(-30, -30, 60, 60, hexc('#5E6670'))
    iso.quad(-8, -8, 16, 16, hexc('#9AA3AE'))
    city(iso, t, skip=lambda gx, gy: abs(gx) <= 1 and abs(gy) <= 1 or (gx > 0 and gy > 0))
    r = random.Random(4)
    pts = []
    for k in range(10):
        x, y = r.uniform(-6, 5), r.uniform(-6, 5)
        sl = t > 1.6 + k * .05
        if sl: sleeper(iso, x - .8, y - .3, r.choice([C['jacket'], hexc('#2F80ED'), C['green'], C['orange']]))
        else: person(iso, x, y, jacket=C['orange'])
        pts.append((x, y))
    iso.draw()
    if t > 1.8:
        for k, (x, y) in enumerate(pts):
            p = iso.P(x, y, .8); zzz(cr, t, p[0], p[1], .9, seed=k)
    # relógio
    card(cr, W / 2 - 170, 140, 340, 130, r=30, fillc=hexc('#0F2236'))
    label(cr, '15:00', W / 2, 205, 84, C['yellow'], 'b')
    if t > 3.6:
        n = int(8e9 * ease(prog(t, 3.6, 5.2)))
        s = f'{n:,}'.replace(',', '.')
        a = clamp((7.2 - t) / .3)
        rrect(cr, 60, 330, W - 120, 250, 36); fill(cr, hexc('#071726'), .8 * a)
        label(cr, s, W / 2, 420, fit_s(cr, s, 120, 960) * back(prog(t, 3.6, 3.9)), (1, 1, 1), 'b', a)
        label(cr, 'dormindo', W / 2, 520, 64, ZC, 'i', a)
    if t > 7.2:
        g = cairo.RadialGradient(W / 2, 1100, 50, W / 2, 1100, 700)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .85 * prog(t, 7.2, 7.6)); cr.set_source(g); cr.paint()
        front_char(cr, W / 2, 1500, 560 * back(prog(t, 7.3, 7.7)), expr='shock', t=t)
        label(cr, 'MENOS VOCÊ', W / 2, 460, 110 * back(prog(t, 7.4, 7.8)), C['yellow'], 'b')
    post(cr, t)

def bed(cr, x, y, s, t, eyes_open=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rrect(cr, -360, -40, 720, 200, 30); fill(cr, hexc('#6B4A35'))
    rrect(cr, -340, -90, 680, 150, 30); fill(cr, hexc('#F1F1F6'))
    rrect(cr, -320, -150, 220, 110, 40); fill(cr, (1, 1, 1))
    # cabeça
    circle(cr, -210, -150, 80, C['skin']); cr.arc(-210, -165, 84, math.pi * 1.05, math.pi * 1.95); fill(cr, hexc('#3A2A1E'))
    cr.set_source_rgb(.2, .15, .1); cr.set_line_width(7)
    for ex in (-245, -175): cr.arc(ex, -150, 16, .2, math.pi - .2); cr.stroke()
    # cobertor respirando
    b = 1 + .03 * math.sin(t * 2.2)
    cr.save(); cr.translate(60, -60); cr.scale(1, b); rrect(cr, -180, -70, 450, 140, 50); cr.restore(); fill(cr, hexc('#7A5CFF'))
    cr.restore()

def ecg(cr, t, x, y, w, h, col):
    cr.set_source_rgba(*col, 1); cr.set_line_width(7); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    n = 80
    for i in range(n + 1):
        u = i / n; ph = (u * 3 - t * .9) % 1
        v = 0
        if .40 < ph < .45: v = -.3
        elif .45 < ph < .5: v = 1.0
        elif .5 < ph < .55: v = -.5
        px, py = x + u * w, y - v * h
        cr.line_to(px, py) if i else cr.move_to(px, py)
    cr.stroke()

def s2(cr, t):
    bg(cr, t, 'noite')
    cr.save(); cam(cr, t, 8.8, 17.0, 1.0, 1.12, dy=-40)
    bed(cr, W / 2 + 60, 1100, 1.0, t)
    zzz(cr, t, W / 2 - 160, 900, 1.6)
    if t < 13.0:
        front_char(cr, 200, 1500, 520, expr='O' if t > 10.4 else 'smile', arm='up' if t > 10.4 else 'down', t=t)
        if t > 10.5:
            card(cr, 300, 560, 380, 150, r=40, fillc=hexc('#FFFFFF'), border=(1, 1, 1))
            label(cr, 'MÃE!!', 490, 635, 84, hexc('#1B2C5E'), 'b')
    cr.restore()
    if t > 13.1:
        a = back(prog(t, 13.1, 13.5))
        cr.save(); cr.translate(W / 2, 560); cr.scale(a, a); cr.translate(-W / 2, -560)
        card(cr, 110, 380, W - 220, 360, fillc=hexc('#0B1A2E'), border=(.4, 1, .6))
        ecg(cr, t, 150, 600, W - 300, 110, hexc('#3CE08A'))
        label(cr, 'RESPIRA: SIM', 330, 440, 40, hexc('#3CE08A'), 'b')
        if t > 14.4: label(cr, 'PULSO: SIM', 770, 440, 40, hexc('#3CE08A'), 'b')
        if t > 15.4: label(cr, 'OLHOS: FECHADOS', W / 2, 700, 46, C['red'], 'b')
        cr.restore()
    ktext(cr, t, 9.0, [[('Ela', 's', 72), ('não', 'b', 100)], [('acorda.', 'i', 130)]], y=160, t1=13.0)
    post(cr, t)

def s3(cr, t):
    bg(cr, t, 'azul', grid=False)
    S = keys(t, [(17.0, 60), (22.5, 84)])
    cxx = keys(t, [(17.0, -2), (22.5, 0.5)])
    iso = IsoR(cr, cxx, 1, 0, S, oy=.58)
    iso.quad(-30, -30, 60, 60, hexc('#7A8794'))
    iso.quad(-30, -2, 60, 6, C['road'])
    for k in range(-6, 7): iso.quad(k * 4, .9, 2, .2, C['line'])
    city(iso, t, seed=5, ext=3, skip=lambda gx, gy: gy > 0 and abs(gx) <= 2)
    car(iso, -1.2, -.4, C['red'])
    car(iso, -9, 1.6, hexc('#2F80ED')); car(iso, 6, 1.6, C['yellow'])
    iso.draw()
    p = iso.P(0, 0, 1.4)
    zzz(cr, t, p[0], p[1] - 20, 1.6)
    if t > 18.3: stamp(cr, t, 18.3, 'PARADO', W / 2, 1250, size=70, col=C['red'])
    ktext(cr, t, 17.2, [[('Lá', 's', 72), ('fora...', 'i', 120)]], y=170)
    post(cr, t)

def bird(cr, x, y, s, t):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1.3, 1); cr.arc(0, 0, 40, 0, 7); cr.restore(); fill(cr, hexc('#E85D3A'))
    circle(cr, 42, -28, 26, hexc('#E85D3A')); circle(cr, 50, -34, 6, C['dark'])
    cr.move_to(66, -28); cr.line_to(92, -22); cr.line_to(66, -16); cr.close_path(); fill(cr, C['yellow'])
    wing = math.sin(t * 9) * .4
    cr.save(); cr.rotate(wing); cr.scale(1.2, .6); cr.arc(-10, -20, 34, 0, 7); cr.restore(); fill(cr, hexc('#B8442A'))
    cr.restore()

def s4(cr, t):
    bg(cr, t, 'gelo')
    progress_days(cr, t, ['1 minuto', '1 hora', '1 dia', '1 semana'], ease(prog(t, 22.5, 23.3)))
    cr.save(); cam(cr, t, 22.5, 28.8, 1.0, 1.08)
    # onda sonora indo ao zero
    amp = 1 - ease(prog(t, 23.9, 25.4))
    cr.set_source_rgba(*ACC, 1); cr.set_line_width(8)
    for i in range(121):
        u = i / 120; x = 80 + u * (W - 160)
        y = 620 + math.sin(u * 40 + t * 12) * 120 * amp * math.sin(u * math.pi) + math.sin(u * 13 - t * 5) * 40 * amp
        cr.line_to(x, y) if i else cr.move_to(x, y)
    cr.stroke()
    for k, (lbl, t0) in enumerate((('ÔNIBUS', 25.8), ('OBRA', 26.8), ('BUZINA', 27.5))):
        if t < t0: continue
        x = W / 2 + (k - 1) * 310; y = 950
        a = back(prog(t, t0, t0 + .3))
        cr.save(); cr.translate(x, y); cr.scale(a, a)
        card(cr, -140, -110, 280, 220, fillc=hexc('#12304D'))
        label(cr, lbl, 0, 0, 44, (1, 1, 1), 'b')
        cr.set_source_rgba(*C['red'], 1); cr.set_line_width(14); cr.move_to(-110, 80); cr.line_to(110, -80); cr.stroke()
        cr.restore()
    cr.restore()
    ktext(cr, t, 23.8, [[('O', 's', 72), ('silêncio', 'i', 140)], [('assusta.', 'b', 100)]], y=180, t1=28.8)
    if t >= 28.8:
        pass
    post(cr, t)

def s4b(cr, t):
    bg(cr, t, 'gelo', grid=False)
    S = keys(t, [(28.8, 60), (32.1, 80)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.66)
    iso.quad(-30, -30, 60, 60, hexc('#7A8794'))
    city(iso, t, seed=9, ext=2, skip=lambda gx, gy: gx > 0 and gy > 0)
    tree(iso, 0, 0, s=1.6)
    iso.draw()
    p = iso.P(0, 0, 4.4)
    bird(cr, p[0], p[1] - 40 + 10 * math.sin(t * 3), 1.4, t)
    for k in range(4):
        ph = (t * .7 + k / 4) % 1
        nx, ny = p[0] + 90 + ph * 200 + k * 10, p[1] - 120 - ph * 260
        circle(cr, nx, ny, 16, (1, 1, 1), 1 - ph); cr.set_source_rgba(1, 1, 1, 1 - ph); cr.set_line_width(6); cr.move_to(nx + 14, ny); cr.line_to(nx + 14, ny - 60); cr.line_to(nx + 40, ny - 45); cr.stroke()
    ktext(cr, t, 29.0, [[('Passarinho', 'i', 120)], [('no', 's', 70), ('centro', 'b', 100)]], y=170)
    post(cr, t)

def tower(cr, x, y, s, steam=1.0, t=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-120, 0); cr.curve_to(-80, -150, -80, -220, -95, -330); cr.line_to(95, -330); cr.curve_to(80, -220, 80, -150, 120, 0); cr.close_path()
    g = cairo.LinearGradient(-120, 0, 120, 0); g.add_color_stop_rgb(0, .85, .87, .9); g.add_color_stop_rgb(1, .55, .58, .64); cr.set_source(g); cr.fill()
    for k in range(5):
        ph = (t * .4 + k / 5) % 1
        circle(cr, math.sin(k * 2) * 30, -350 - ph * 260, 60 + ph * 70, (1, 1, 1), .5 * (1 - ph) * steam)
    cr.restore()

def gauge(cr, x, y, r, v, label_):
    cr.set_source_rgba(1, 1, 1, .2); cr.set_line_width(18); cr.arc(x, y, r, math.pi, 0); cr.stroke()
    col = mix(hexc('#3CE08A'), C['red'], clamp(v))
    cr.set_source_rgba(*col, 1); cr.arc(x, y, r, math.pi, math.pi + math.pi * clamp(v)); cr.stroke()
    a = math.pi + math.pi * clamp(v)
    cr.set_source_rgb(1, 1, 1); cr.set_line_width(8); cr.move_to(x, y); cr.line_to(x + math.cos(a) * r * .8, y + math.sin(a) * r * .8); cr.stroke()
    label(cr, label_, x, y + 50, 30, (.8, .85, 1), 's')

def s5(cr, t):
    bg(cr, t, 'azul')
    progress_days(cr, t, ['1 minuto', '1 hora', '1 dia', '1 semana'], 1 + ease(prog(t, 32.1, 32.9)))
    cr.save(); cam(cr, t, 32.1, 40.4, 1.0, 1.1, dy=-30)
    if t < 37.0:
        card(cr, 90, 520, W - 180, 640, fillc=hexc('#0B1A2E'))
        label(cr, 'PAINEL DA USINA', W / 2, 590, 40, (.8, .85, 1), 'b')
        for k in range(3):
            v = .3 + ease(prog(t, 34.0 + k * .5, 36.0 + k * .4)) * .7 + .03 * math.sin(t * 7 + k)
            gauge(cr, 250 + k * 290, 820, 110, v, ['PRESSÃO', 'CARGA', 'TEMP.'][k])
        cadeira_x = W / 2
        rrect(cr, 180, 960, W - 360, 140, 20); fill(cr, hexc('#13263F'))
        label(cr, 'OPERADOR: Zzz', W / 2, 1030, 46, ZC, 'b')
        if t > 35.0 and int(t * 4) % 2: rrect(cr, 90, 520, W - 180, 640, 34); cr.set_source_rgba(*C['red'], .9); cr.set_line_width(10); cr.stroke()
    else:
        steam = 1 - ease(prog(t, 38.0, 39.5))
        tower(cr, W / 2 - 200, 1250, 1.3, steam, t); tower(cr, W / 2 + 200, 1250, 1.3, steam, t)
        rrect(cr, 120, 1250, W - 240, 60, 10); fill(cr, hexc('#3A4A5E'))
        if t > 39.1:
            a = back(prog(t, 39.1, 39.5)); cr.save(); cr.translate(W / 2, 820); cr.scale(a, a)
            cr.move_to(0, -150); cr.line_to(120, -100); cr.line_to(110, 40); cr.curve_to(80, 110, 30, 140, 0, 160); cr.curve_to(-30, 140, -80, 110, -110, 40); cr.line_to(-120, -100); cr.close_path()
            fill(cr, hexc('#3CE08A')); cr.set_source_rgb(1, 1, 1); cr.set_line_width(20); cr.move_to(-50, 0); cr.line_to(-10, 45); cr.line_to(60, -50); cr.stroke(); cr.restore()
    cr.restore()
    ktext(cr, t, 32.4, [[('As', 's', 72), ('usinas', 'i', 130)], [('começam', 's', 72), ('a', 's', 72), ('falhar', 'b', 100)]], y=170, t1=37.0)
    ktext(cr, t, 37.1, [[('Nucleares', 'b', 100)], [('se', 's', 72), ('desligam', 'i', 120)]], y=170)
    post(cr, t)

def s6(cr, t):
    bg(cr, t, 'noite', grid=False)
    stars(cr, a=prog(t, 43.4, 45.0))
    off = ease(prog(t, 40.6, 44.4))
    S = keys(t, [(40.4, 34), (45.7, 30)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.6)
    iso.quad(-30, -30, 60, 60, hexc('#3A4150'))
    city(iso, t, night=True, lights=lambda idx: ((idx * 37) % 100) / 100 > off * 1.05 and t < 44.5, seed=3)
    iso.draw(night=.75)
    if t > 44.5:
        cr.set_source_rgba(0, 0, 0, .55 * prog(t, 44.5, 44.7)); cr.paint()
        title(cr, t, 44.5, 999, 'APAGÃO', y=520, size=170, col=C['white'])
    ktext(cr, t, 40.6, [[('Uma', 'b', 100), ('a', 's', 72), ('uma...', 'i', 120)]], y=200, t1=44.4)
    post(cr, t, vignette=.6)

def head_sleep(cr, x, y, r, hair, t, k):
    circle(cr, x, y, r, C['skin']); cr.arc(x, y - r * .15, r * 1.04, math.pi * 1.05, math.pi * 1.95); fill(cr, hair)
    cr.set_source_rgb(.2, .15, .1); cr.set_line_width(r * .08)
    for ex in (-.35, .35): cr.arc(x + ex * r, y, r * .2, .2, math.pi - .2); cr.stroke()
    zzz(cr, t, x + r * .7, y - r, r / 70, seed=k)

def spoon(cr, x, y, s, rot):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    rrect(cr, -12, 0, 24, 220, 12); fill(cr, hexc('#C9D1DA'))
    cr.save(); cr.scale(1, 1.3); cr.arc(0, -30, 50, 0, 7); cr.restore(); fill(cr, hexc('#C9D1DA'))
    cr.save(); cr.scale(1, 1.2); cr.arc(0, -32, 36, 0, 7); cr.restore(); fill(cr, hexc('#4AA8F0'))
    cr.restore()

def s7(cr, t):
    bg(cr, t, 'vinho')
    progress_days(cr, t, ['1 minuto', '1 hora', '1 dia', '1 semana'], 2 + ease(prog(t, 45.7, 46.5)))
    cr.save(); cam(cr, t, 45.7, 56.2, 1.0, 1.08)
    if t < 52.0:
        for k, (lbl, t0, col) in enumerate((('NÃO COME', 50.3, C['orange']), ('NÃO BEBE', 51.0, hexc('#4AA8F0')))):
            if t < t0: continue
            a = back(prog(t, t0, t0 + .3)); cr.save(); cr.translate(W / 2, 760 + k * 300); cr.scale(a, a)
            card(cr, -380, -110, 760, 220, fillc=hexc('#2A1030'), border=(1, .6, .75)); label(cr, lbl, 0, 0, 90, col, 'b'); cr.restore()
    else:
        heads = [(W / 2 - 300, 1050, hexc('#3A2A1E')), (W / 2, 1000, hexc('#8A5A35')), (W / 2 + 300, 1050, hexc('#1E1E22'))]
        for k, (x, y, hc) in enumerate(heads): head_sleep(cr, x, y, 110, hc, t, k)
        i = int(clamp((t - 54.3) / .6, 0, 2.99)) if t > 54.3 else 0
        tx = heads[i][0] + 80; ty = heads[i][1] - 40 + 10 * math.sin(t * 6)
        spoon(cr, tx, ty, .9, -2.4)
        for k in range(3):
            if t > 55.1 + k * .2: label(cr, str(k + 1), heads[k][0], heads[k][1] + 200, 80, C['yellow'], 'b', prog(t, 55.1 + k * .2, 55.3 + k * .2))
    cr.restore()
    ktext(cr, t, 47.0, [[('Agora', 's', 72), ('o', 's', 72), ('problema', 'b', 100)], [('é', 's', 72), ('SEU.', 'i', 140)]], y=180, t1=51.9)
    ktext(cr, t, 52.1, [[('Água', 'b', 100), ('de', 's', 72), ('colher', 'i', 120)]], y=200)
    post(cr, t)

def s8(cr, t):
    bg(cr, t, 'noite')
    n = int(3 + 1500 * ease(prog(t, 56.3, 57.8)))
    r = random.Random(2)
    for k in range(n):
        x, y = r.uniform(30, W - 30), r.uniform(560, 1500)
        circle(cr, x, y, 7, ZC, .6)
    circle(cr, W / 2, 1030, 26, C['yellow'])
    label(cr, 'você', W / 2, 1090, 40, C['yellow'], 'b')
    s = '8.000.000.000'
    label(cr, s, W / 2, 300, fit_s(cr, s, 140, 980) * back(prog(t, 56.8, 57.2)), (1, 1, 1), 'b')
    if t > 58.3:
        label(cr, 'Você não dá conta.', W / 2, 440, 72 * back(prog(t, 58.3, 58.6)), ACC, 'i')
    post(cr, t)

def s9(cr, t):
    bg(cr, t, 'azul', grid=False)
    sp = ease(prog(t, 62.8, 63.6))
    # metade de cima: amanhecer / de baixo: noite eterna
    g = cairo.LinearGradient(0, 520, 0, 1020); g.add_color_stop_rgb(0, 1, .7, .35); g.add_color_stop_rgb(1, 1, .45, .3)
    if t > 62.8:
        cr.rectangle(0, 520, W * sp, 500); cr.set_source(g); cr.fill()
        circle(cr, W * sp - 300, 900, 120, hexc('#FFE08A'))
        label(cr, 'AMANHÃ?', W * sp - 300, 650, 90, (1, 1, 1), 'b')
    if t > 64.9:
        sp2 = ease(prog(t, 64.9, 65.6))
        cr.rectangle(W * (1 - sp2), 1040, W, 460); fill(cr, hexc('#05061A'))
        cr.save(); cr.rectangle(W * (1 - sp2), 1040, W, 460); cr.clip(); stars(cr, seed=9); cr.restore()
        label(cr, 'NUNCA?', W * (1 - sp2) + 300, 1270, 110, C['red'], 'b')
    ktext(cr, t, 59.9, [[('A', 's', 72), ('pergunta', 'b', 100)], [('que', 's', 64), ('não', 's', 64), ('te', 's', 64), ('deixa', 's', 64), ('dormir:', 'i', 92)]], y=170)
    post(cr, t)

def s10(cr, t):
    bg(cr, t, 'noite')
    for k, (num, txt, sub, t0) in enumerate((('1', 'Cuidar da', 'FAMÍLIA', 67.3), ('2', 'Sair pra', 'DESCOBRIR', 69.9))):
        if t < t0: continue
        a = back(prog(t, t0, t0 + .35)); y = 760 + k * 400
        cr.save(); cr.translate(W / 2, y); cr.scale(a, a)
        card(cr, -430, -160, 860, 320, fillc=hexc('#1A1450'), border=(.7, .6, 1))
        circle(cr, -300, 0, 95, ACC); label(cr, num, -300, 0, 120, (1, 1, 1), 'b')
        label(cr, txt, 90, -55, 56, (.8, .85, 1), 's'); label(cr, sub, 90, 45, fit_s(cr, sub, 100, 560), (1, 1, 1), 'b')
        cr.restore()
    ktext(cr, t, 67.0, [[('E', 's', 72), ('você?', 'i', 140)]], y=200)
    if t > 72.4:
        title(cr, t, 72.4, 999, 'UM OU DOIS?', y=1500 - 30, size=130)
    post(cr, t)

SCENES = [(0, .4, s0), (.4, 8.8, s1), (8.8, 17.0, s2), (17.0, 22.5, s3), (22.5, 28.8, s4), (28.8, 32.1, s4b),
          (32.1, 40.4, s5), (40.4, 45.7, s6), (45.7, 56.2, s7), (56.2, 59.7, s8), (59.7, 66.8, s9), (66.8, 999, s10)]

def overlays(cr, t):
    if t >= .4 and t < DUR + .3:
        cr.save(); cr.translate(0, 230); caption(cr, t, WORDS); cr.restore()

def render(t, surf):
    cr = ctx_for(surf)
    for a, b, fn in SCENES:
        if a <= t < b:
            cr.save(); fn(cr, t); cr.restore(); break
    for a, b, fn in SCENES[1:]:
        flash_cut(cr, t, a, .15)
    overlays(cr, t)
