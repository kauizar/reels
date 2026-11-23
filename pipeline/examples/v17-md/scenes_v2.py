import os, sys, math, random
pass  # md.py fica em pipeline/lib
import cairo
from engine import *
from real import post, IsoR
from md import *

D = os.path.dirname(os.path.abspath(__file__))
WORDS = load_words(D)
DUR = 70.426
END = DUR + 1.5
PIX = hexc('#32BCAD'); GOLD = hexc('#F5C542'); MONEY = hexc('#7BC96F')

# ---------- props ----------
def pix_logo(cr, x, y, s, a=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(math.pi / 4)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        rrect(cr, dx * 34 * s - 28 * s, dy * 34 * s - 28 * s, 56 * s, 56 * s, 16 * s); fill(cr, PIX, a)
    cr.restore()

def card_icon(cr, x, y, s, a=1.0):
    rrect(cr, x - 120 * s, y - 75 * s, 240 * s, 150 * s, 18 * s); fill(cr, hexc('#5B6BFF'), a)
    cr.rectangle(x - 120 * s, y - 40 * s, 240 * s, 30 * s); fill(cr, hexc('#1A1F3A'), a)
    rrect(cr, x - 95 * s, y + 10 * s, 50 * s, 36 * s, 6 * s); fill(cr, GOLD, a)

def note(cr, x, y, s, rot=0.0, gray=0.0, a=1.0, val='100'):
    col = mix(MONEY, hexc('#8C8C8C'), gray)
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    rrect(cr, -150, -72, 300, 144, 10); fill(cr, col, a)
    rrect(cr, -136, -58, 272, 116, 8); cr.set_source_rgba(*shade(col, .7), a); cr.set_line_width(4); cr.stroke()
    circle(cr, 0, 0, 40, shade(col, .8), a)
    label(cr, val, -95, -28, 34, shade(col, .45), 'b', a); label(cr, val, 95, 30, 34, shade(col, .45), 'b', a)
    cr.restore()

def bank_screen(val, red=0.0):
    def f(cr, w, h, m):
        cr.rectangle(m, m, w, h); fill(cr, hexc('#F4F6FB'))
        cr.rectangle(m, m, w, h * .34); fill(cr, hexc('#7A3CFF'))
        label(cr, 'Olá!', m + 40, m + 110, 34, (1, 1, 1), 'b', align='l')
        label(cr, 'Saldo disponível', m + 40, m + 190, 26, (1, 1, 1), 's', .85, align='l')
        col = mix((1, 1, 1), hexc('#FF4F5E'), red)
        label(cr, val, m + 40, m + 255, fit_s(cr, val, 64, w - 80), col, 'b', align='l')
        for k in range(4):
            rrect(cr, m + 30 + k * (w - 60) / 4 + 8, m + h * .4, (w - 60) / 4 - 16, 90, 20); fill(cr, hexc('#E3E6F0'))
        for k in range(4):
            rrect(cr, m + 30, m + h * .55 + k * 95, w - 60, 75, 16); fill(cr, hexc('#E9ECF4'))
    return f

def can(cr, x, y, s, col=None):
    col = col or hexc('#E8EEF5')
    rrect(cr, x - 55 * s, y - 80 * s, 110 * s, 160 * s, 14 * s); fill(cr, col)
    cr.rectangle(x - 55 * s, y - 30 * s, 110 * s, 60 * s); fill(cr, hexc('#2F80ED'))
    label(cr, 'LEITE', x, y, 24 * s, (1, 1, 1), 'b')
    cr.save(); cr.translate(x, y - 80 * s); cr.scale(1, .3); cr.arc(0, 0, 55 * s, 0, 7); cr.restore(); fill(cr, shade(col, .8))

def rice(cr, x, y, s):
    cr.move_to(x - 90 * s, y + 120 * s); cr.line_to(x - 80 * s, y - 100 * s); cr.line_to(x + 80 * s, y - 100 * s); cr.line_to(x + 90 * s, y + 120 * s); cr.close_path()
    fill(cr, hexc('#F7F2E4'))
    rrect(cr, x - 70 * s, y - 30 * s, 140 * s, 80 * s, 10 * s); fill(cr, hexc('#E2453C'))
    label(cr, 'ARROZ', x, y + 10 * s, 30 * s, (1, 1, 1), 'b')
    cr.rectangle(x - 80 * s, y - 120 * s, 160 * s, 24 * s); fill(cr, hexc('#D8CFB8'))

def bread(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1.6, 1); cr.arc(0, 0, 70, math.pi, 0); cr.restore(); cr.line_to(112, 20); cr.line_to(-112, 20); cr.close_path(); fill(cr, hexc('#D99A4E'))
    cr.set_source_rgb(*hexc('#B5762E')); cr.set_line_width(8)
    for k in (-50, 0, 50): cr.move_to(k - 15, -45); cr.line_to(k + 15, -15); cr.stroke()
    cr.restore()

def truck(iso, x, y, c):
    iso.box(x, y, .2, 3.4, 1.4, 1.6, hexc('#ECECEC'))
    iso.box(x + 3.5, y + .05, .2, 1.2, 1.3, 1.2, c, deco=lambda i, *b: i.frect(b, 'x', .1, .45, .9, .9, C['glass']))
    for dx in (.4, 2.4, 3.8): iso.box(x + dx, y - .06, 0, .5, 1.52, .45, C['dark'])

def qmark(cr, t, t0, x, y, size=110, col=None):
    if t < t0: return
    text_center(cr, '?', x, y + 6 * math.sin(t * 5), size, col or C['yellow'], stroke=C['dark'], sw=10, scale=back((t - t0) / .3))

def xmark(cr, x, y, r, p):
    cr.set_source_rgba(*C['red'], 1); cr.set_line_width(26); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    p1 = clamp(p * 2); p2 = clamp(p * 2 - 1)
    cr.move_to(x - r, y - r); cr.line_to(x - r + 2 * r * p1, y - r + 2 * r * p1); cr.stroke()
    if p2 > 0: cr.move_to(x + r, y - r); cr.line_to(x + r - 2 * r * p2, y - r + 2 * r * p2); cr.stroke()

# ---------- cenas ----------
def s0(cr, t):  # capa
    bg(cr, t, 'verde')
    for k in range(9):
        note(cr, 140 + (k % 3) * 400, 1000 + (k // 3) * 240, .9, rot=-.3 + k * .07, gray=.6)
    phone(cr, W / 2, 1180, .75, bank_screen('R$ 0,00', 1), t)
    label(cr, 'SEM', W / 2, 360, 170, (1, 1, 1), 'b')
    label(cr, 'DINHEIRO?', W / 2, 560, fit_s(cr, 'DINHEIRO?', 190, 980), C['yellow'], 'b')
    post(cr, t, vignette=.5)

def s1(cr, t):
    bg(cr, t, 'verde')
    cr.save(); cam(cr, t, .4, 8.7, 1.0, 1.1, dy=-30)
    bal = 12430.0 * (1 - ease(prog(t, 2.8, 3.8)))
    val = 'R$ ' + f'{bal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    if t < 4.8:
        phone(cr, W / 2, 1000, 1.0, bank_screen(val, prog(t, 3.3, 3.8)), t)
    else:
        n = 1 + int(5 * ease(prog(t, 4.9, 7.2)))
        pos = [(W / 2, 1180), (W / 2 - 320, 1180), (W / 2 + 320, 1180), (W / 2 - 320, 720), (W / 2, 720), (W / 2 + 320, 720)]
        sc = keys(t, [(4.8, 1.0), (5.6, .44)])
        for k in range(n - 1, -1, -1):
            x, y = pos[k]
            if k == 0: y = keys(t, [(4.8, 1060), (5.6, 1180)])
            phone(cr, x, y, sc * (1 if k == 0 else back(prog(t, 4.9 + k * .3, 5.2 + k * .3))), bank_screen('R$ 0,00', 1), t)
    cr.restore()
    ktext(cr, t, .5, [[('Você', 'b', 100), ('acorda', 'b', 100)], [('e', 's', 70), ('o', 's', 70), ('saldo', 'b', 100), ('é...', 'i', 110)]], y=150, t1=4.7)
    stamp(cr, t, 3.7, 'ZERO', W / 2, 1520 - 200, size=110) if t < 4.7 else None
    ktext(cr, t, 4.8, [[('O', 's', 60), ('seu.', 'b', 90), ('O', 's', 60), ('do', 's', 60), ('vizinho.', 'i', 96)], [('O', 's', 60), ('do', 's', 60), ('PAÍS.', 'y', 110)]], y=130, stagger=.25)
    post(cr, t)

def s2(cr, t):
    bg(cr, t, 'azul')
    progress_days(cr, t, ['1 hora', '1 dia', '1 semana', '1 mês'], 0)
    cr.save(); cam(cr, t, 8.7, 16.1, 1.0, 1.1, dx=-30)
    a = back(prog(t, 9.0, 9.4))
    card(cr, 120, 420, 380, 380); card(cr, 580, 420, 380, 380)
    pix_logo(cr, 310, 610, 1.3 * a)
    card_icon(cr, 770, 610, 1.1 * back(prog(t, 10.7, 11.1)))
    xmark(cr, 310, 610, 110, prog(t, 10.4, 10.9)); xmark(cr, 770, 610, 110, prog(t, 11.4, 11.9))
    # notas caindo e ficando cinza
    r = random.Random(3)
    for k in range(10):
        st = 12.3 + k * .12
        if t < st: continue
        y = 900 + min(1, (t - st) / 1.2) * r.uniform(150, 420)
        note(cr, r.uniform(150, W - 150), y, .75, rot=r.uniform(-.5, .5) + (t - st) * .2, gray=ease(prog(t, 13.4, 14.4)))
    cr.restore()
    stamp(cr, t, 14.6, 'NINGUÉM ACEITA', W / 2, 1400, col=C['red'], size=70)
    post(cr, t)

def s3(cr, t):
    bg(cr, t, 'sepia', grid=False)
    S = keys(t, [(16.1, 64), (20.5, 76)])
    iso = IsoR(cr, 3, 3, 0, S, oy=.56)
    iso.quad(-6, -6, 18, 18, hexc('#C9B38E'))
    house(iso, 0, 0, 5, 4, 2.6, wall=hexc('#F2D6A8'), roof=hexc('#C2462E'), lit=True)
    person(iso, 6.2, 2.0, phase=None, jacket=C['white'])
    person(iso, 7.6, 3.6, phase=t * 6 if t < 17.5 else None, jacket=hexc('#2F80ED'))
    iso.draw()
    P = iso.P(2.5, 2.0, 5.2)
    rrect(cr, P[0] - 190, P[1] - 60, 380, 90, 20); fill(cr, hexc('#3A2412'))
    label(cr, 'PADARIA', P[0], P[1] - 15, 50, C['yellow'], 'b')
    bx, by = iso.P(6.2, 2.0, 3.3)
    if t > 17.4:
        bread(cr, bx + 120, by - 60, .9 * back(prog(t, 17.4, 17.8)))
        qmark(cr, t, 18.1, bx - 40, by - 140)
    ktext(cr, t, 16.2, [[('O', 's', 70), ('padeiro', 'b', 104)], [('não', 's', 66), ('sabe', 's', 66), ('o', 's', 66), ('que', 's', 66), ('cobrar.', 'i', 104)]])
    post(cr, t, warm=.15)

def s4(cr, t):
    bg(cr, t, 'azul')
    progress_days(cr, t, ['1 hora', '1 dia', '1 semana', '1 mês'], ease(prog(t, 20.5, 21.3)))
    cr.save(); cam(cr, t, 20.5, 26.0, 1.0, 1.1, dy=-40)
    ktext(cr, t, 21.6, [[('Começa', 'b', 90), ('a', 'b', 90)], [('TROCA', 'i', 190)]], y=300, align='c')
    sw = ease(prog(t, 25.3, 25.9))
    lx, rx = W / 2 - 250 + 500 * sw, W / 2 + 250 - 500 * sw
    lift = math.sin(sw * math.pi) * 160
    if t > 23.1:
        a = back(prog(t, 23.1, 23.5))
        can(cr, lx - 65, 1020 - lift, a); can(cr, lx + 65, 1020 - lift, a * back(prog(t, 23.3, 23.7)))
    if t > 24.4: rice(cr, rx, 1020 + lift, back(prog(t, 24.4, 24.8)))
    if 24.0 < t:
        cr.set_source_rgba(1, 1, 1, .9 * (1 - sw)); cr.set_line_width(10)
        cr.arc(W / 2, 880, 120, math.pi * 1.15, math.pi * 1.85); cr.stroke()
        cr.arc(W / 2, 1160, 120, math.pi * .15, math.pi * .85); cr.stroke()
    cr.restore()
    post(cr, t)

def s5(cr, t):
    bg(cr, t, 'verde')
    cr.save(); cam(cr, t, 26.0, 32.4, 1.05, 1.0)
    tilt = keys(t, [(26.0, 0.0), (28.3, -.22), (29.8, -.22), (31.3, -.32)])
    cx, cy = W / 2, 1000
    cr.set_source_rgb(*hexc('#D9DDE6')); cr.set_line_width(22)
    cr.move_to(cx, cy); cr.line_to(cx, cy + 380); cr.stroke()
    rrect(cr, cx - 160, cy + 370, 320, 40, 12); fill(cr, hexc('#D9DDE6'))
    cr.save(); cr.translate(cx, cy); cr.rotate(tilt)
    cr.move_to(-380, 0); cr.line_to(380, 0); cr.stroke()
    lx, ly = -330 * math.cos(tilt) * 0 - 330, 0
    cr.restore()
    for side in (-1, 1):
        px = cx + side * 330 * math.cos(tilt); py = cy + side * 330 * math.sin(tilt)
        cr.set_line_width(5); cr.move_to(px, py); cr.line_to(px - 120, py + 200); cr.move_to(px, py); cr.line_to(px + 120, py + 200); cr.stroke()
        cr.save(); cr.translate(px, py + 200); cr.scale(1, .3); cr.arc(0, 0, 150, 0, math.pi); cr.restore(); fill(cr, hexc('#D9DDE6'))
        if side == -1 and t > 26.3:
            a = back(prog(t, 26.3, 26.7)); can(cr, px - 60, py + 120, .8 * a); rice(cr, px + 60, py + 110, .7 * a)
            if t > 28.2: crown(cr, px, py - 40, back(prog(t, 28.2, 28.6)))
        if side == 1 and t > 29.6:
            phone(cr, px, py + 50, .32 * back(prog(t, 29.6, 30.0)), bank_screen('R$ 0,00', 1), t)
    cr.restore()
    ktext(cr, t, 26.1, [[('Quem', 's', 72), ('tem', 's', 72), ('comida', 'b', 104)], [('é', 's', 72), ('RICO.', 'i', 150)]], y=170, t1=29.0)
    ktext(cr, t, 29.1, [[('Quem', 's', 72), ('tem', 's', 72), ('salário', 'b', 104)], [('não', 's', 72), ('tem', 's', 72), ('NADA.', 'o', 150)]])
    post(cr, t)

def crown(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-70, 30); cr.line_to(-80, -40); cr.line_to(-35, 0); cr.line_to(0, -60); cr.line_to(35, 0); cr.line_to(80, -40); cr.line_to(70, 30); cr.close_path()
    fill(cr, GOLD); cr.restore()

def s6(cr, t):
    bg(cr, t, 'noite', grid=False)
    progress_days(cr, t, ['1 hora', '1 dia', '1 semana', '1 mês'], 1 + ease(prog(t, 32.4, 33.2)))
    S = keys(t, [(32.4, 40), (36.8, 46), (40.8, 52)])
    cxw = keys(t, [(32.4, 2.0), (36.8, 6.0), (40.8, 9.0)])
    iso = IsoR(cr, cxw, 4, 0, S, oy=.6)
    iso.quad(-10, -6, 30, 22, hexc('#4C5466'))
    iso.quad(-10, 6, 30, 3, C['road'])
    # mercado vazio
    iso.box(-4, -2, 0, 6, 5, 2.4, hexc('#F4F4F4'), deco=lambda i, *b: (i.frect(b, 'y', .08, .05, .92, .75, hexc('#2A3346')), i.frect(b, 'x', .3, 0, .7, .7, hexc('#2A3346'))))
    # posto
    iso.box(5, -1, 2.4, 5, 4, .4, C['red']); iso.box(5.3, -.7, 0, .3, .3, 2.4, C['concrete']); iso.box(9.4, 2.6, 0, .3, .3, 2.4, C['concrete'])
    iso.box(7, 1, 0, .8, .6, 1.3, hexc('#E5E5E5'))
    for k in range(3): truck(iso, 3 + k * 6.5, 6.6, [C['red'], hexc('#2F80ED'), C['orange']][k])
    iso.draw(night=.35)
    p = iso.P(-1, -2, 3.4); label(cr, 'MERCADO', p[0], p[1] - 10, 40, C['white'], 'b')
    if t > 34.9: stamp(cr, t, 34.9, 'VAZIO', p[0], p[1] + 160, size=60)
    p2 = iso.P(7.5, -1, 3.3)
    if t > 36.1: stamp(cr, t, 36.1, 'FECHADO', p2[0], p2[1] - 40, size=56)
    if t > 37.6:
        for k in range(3):
            q = iso.P(3 + k * 6.5 + 4, 6.6, 2.6); qmark(cr, t, 37.6 + k * .25, q[0], q[1] - 60, 90)
    ktext(cr, t, 32.6, [[('Supermercados', 'b', 96)], [('vazios.', 'i', 120)]], y=230, t1=37.0)
    ktext(cr, t, 37.1, [[('Caminhões', 'b', 96)], [('param.', 'i', 130)]], y=230, t1=40.7)
    post(cr, t, vignette=.55)

def s7(cr, t):
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, 40.7, 48.8, 1.0, 1.12)
    m = ease(prog(t, 44.6, 45.9))
    if m < 1:
        note(cr, W / 2, 1000, 2.0 * (1 - m * .7), rot=-.06 + .05 * math.sin(t), gray=0, a=1 - m)
    if t > 43.9 and m < .4:
        stamp(cr, t, 43.9, 'NÃO É PAPEL', W / 2, 1300, size=70)
    if m > 0:
        hs(cr, W / 2, 1000, 1.4 * back(m))
    cr.restore()
    ktext(cr, t, 40.9, [[('Dinheiro', 'b', 110), ('nunca', 's', 76)], [('foi', 's', 76), ('papel.', 'i', 140)]], y=170, t1=44.7)
    ktext(cr, t, 44.9, [[('Dinheiro', 's', 72), ('é', 's', 72), ('uma', 's', 72)], [('PROMESSA', 'i', 150)], [('que', 's', 60), ('todo', 's', 60), ('mundo', 's', 60), ('aceita.', 'b', 76)]], y=150, stagger=.15)
    post(cr, t)

def hs(cr, x, y, s):
    """aperto de mão estilizado"""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 300); g.add_color_stop_rgba(0, 1, .85, .4, .5); g.add_color_stop_rgba(1, 1, .85, .4, 0)
    cr.set_source(g); cr.arc(0, 0, 300, 0, 7); cr.fill()
    rrect(cr, -330, -40, 200, 90, 20); fill(cr, hexc('#2F80ED'))
    rrect(cr, 130, -40, 200, 90, 20); fill(cr, hexc('#E2453C'))
    cr.save(); cr.rotate(-.25); rrect(cr, -150, -55, 190, 95, 45); fill(cr, hexc('#F2C29B')); cr.restore()
    cr.save(); cr.rotate(.25); rrect(cr, -40, -25, 190, 95, 45); fill(cr, hexc('#D9A27A')); cr.restore()
    for k in range(4):
        rrect(cr, -40 + k * 34, -58, 30, 60, 14); fill(cr, hexc('#F2C29B'))
    cr.restore()

def cig(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.rotate(-.3); cr.scale(s, s)
    rrect(cr, -150, -20, 230, 40, 8); fill(cr, (1, 1, 1)); rrect(cr, 80, -20, 70, 40, 8); fill(cr, hexc('#E39A4B'))
    circle(cr, -150, 0, 18, hexc('#FF6A2B'))
    for k in range(3): circle(cr, -170 - k * 25, -40 - k * 40 + 10 * math.sin(k), 16 + k * 6, (1, 1, 1), .25)
    cr.restore()

def gold(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for k, (dx, dy) in enumerate(((-70, 30), (70, 30), (0, -40))):
        cr.move_to(dx - 80, dy + 35); cr.line_to(dx - 55, dy - 35); cr.line_to(dx + 55, dy - 35); cr.line_to(dx + 80, dy + 35); cr.close_path(); fill(cr, GOLD)
        cr.move_to(dx - 55, dy - 35); cr.line_to(dx + 55, dy - 35); cr.line_to(dx + 45, dy - 20); cr.line_to(dx - 45, dy - 20); cr.close_path(); fill(cr, hexc('#FFE38A'))
    cr.restore()

def clock_ic(cr, x, y, s, t):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    circle(cr, 0, 0, 100, (1, 1, 1)); circle(cr, 0, 0, 84, hexc('#1B2C5E'))
    cr.set_source_rgb(1, 1, 1); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    a = t * 3; cr.move_to(0, 0); cr.line_to(math.sin(a) * 60, -math.cos(a) * 60); cr.stroke()
    cr.move_to(0, 0); cr.line_to(math.sin(a / 12) * 40, -math.cos(a / 12) * 40); cr.stroke()
    cr.restore()

def s8(cr, t):
    bg(cr, t, 'vinho')
    progress_days(cr, t, ['1 hora', '1 dia', '1 semana', '1 mês'], 2 + ease(prog(t, 48.8, 49.6)))
    cr.save(); cam(cr, t, 48.8, 60.7, 1.0, 1.08)
    ktext(cr, t, 49.2, [[('A', 's', 70), ('fome', 'i', 150), ('aperta.', 'b', 100)]], y=260, t1=53.4)
    if 50.4 < t < 53.6:
        a = clamp((53.6 - t) / .3)
        phone(cr, W / 2, 1000, .7 * back(prog(t, 50.4, 50.8)), bank_screen('R$ 0,00', 1), t, a)
    ktext(cr, t, 52.6, [[('Nova', 's', 70), ('moeda:', 'b', 110)]], y=260)
    items = [(54.2, 'CIGARRO', cig), (58.0, 'OURO', gold), (59.2, 'HORAS', None)]
    for k, (t0, lbl, fn) in enumerate(items):
        if t < t0: continue
        a = back(prog(t, t0, t0 + .35))
        x, y = W / 2, 660 + k * 280
        cr.save(); cr.translate(x, y); cr.scale(a, a); cr.translate(-x, -y)
        card(cr, 110, y - 120, W - 220, 240, fillc=hexc('#2A1030'), border=(1, .6, .75))
        if fn: fn(cr, 330, y, .8)
        else: clock_ic(cr, 330, y, .9, t)
        label(cr, lbl, 720, y, 80, C['white'], 'b')
        cr.restore()
    if t > 55.3: chip(cr, t, 55.3, 57.6, 'JÁ ACONTECEU EM PRISÕES E GUERRAS', W / 2, 1340, col=hexc('#B3264F'), size=34)
    cr.restore()
    post(cr, t)

def s9(cr, t):
    bg(cr, t, 'azul', glow=(.5, .45))
    cr.save(); cam(cr, t, 60.7, 65.7, .95, 1.12)
    r = random.Random(1)
    for k in range(14):
        ang = t * .5 + k * 2 * math.pi / 14; rad = 380 + 40 * math.sin(t + k)
        x, y = W / 2 + math.cos(ang) * rad, 900 + math.sin(ang) * rad * .55
        circle(cr, x, y, 34, GOLD, .9); label(cr, '$', x, y, 40, shade(GOLD, .55), 'b')
    if t > 64.0:
        hs(cr, W / 2, 900, 1.2 * back(prog(t, 64.0, 64.5)))
    cr.restore()
    ktext(cr, t, 61.0, [[('No', 's', 70), ('fim,', 's', 70), ('não', 's', 70), ('volta', 'b', 100)], [('o', 's', 70), ('dinheiro...', 'i', 120)]], y=160, t1=64.0)
    if t > 64.3:
        label(cr, 'volta a', W / 2, 1230, 60, (.8, .85, 1), 's')
        label(cr, 'CONFIANÇA', W / 2, 1340, fit_s(cr, 'CONFIANÇA', 150, 960, 'i') * back(prog(t, 64.4, 64.8)), ACC, 'i')
    post(cr, t)

def s10(cr, t):
    bg(cr, t, 'verde')
    def scr(cr, w, h, m):
        cr.rectangle(m, m, w, h); fill(cr, hexc('#F4F6FB'))
        pix_logo(cr, m + w / 2, m + h * .35, 1.1)
        label(cr, 'Pix', m + w / 2, m + h * .55, 70, hexc('#1B2C5E'), 'b')
        rrect(cr, m + 40, m + h * .7, w - 80, 110, 55); fill(cr, PIX)
        label(cr, 'ENVIAR', m + w / 2, m + h * .7 + 55, 46, (1, 1, 1), 'b')
    y = 1290 + 20 * math.sin(t * 2)
    phone(cr, W / 2, y, .62 * back(prog(t, 65.8, 66.2)), scr, t)
    # seta de compartilhar
    if t > 67.4:
        a = back(prog(t, 67.4, 67.8)); cr.save(); cr.translate(W - 200, 1150 - 20 * math.sin(t * 4)); cr.scale(a, a)
        circle(cr, 0, 0, 90, ACC); cr.set_source_rgb(1, 1, 1); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(-35, 30); cr.line_to(30, -30); cr.move_to(-5, -32); cr.line_to(32, -32); cr.line_to(32, 5); cr.stroke(); cr.restore()
    cta(cr, t, 65.9, 'Manda pro amigo que', 'não vive sem Pix')
    post(cr, t)

SCENES = [(0, .4, s0), (.4, 8.7, s1), (8.7, 16.1, s2), (16.1, 20.5, s3), (20.5, 26.0, s4), (26.0, 32.4, s5),
          (32.4, 40.7, s6), (40.7, 48.8, s7), (48.8, 60.7, s8), (60.7, 65.7, s9), (65.7, 999, s10)]

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
