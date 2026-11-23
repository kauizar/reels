import os, sys, math, random
pass  # md.py fica em pipeline/lib
import cairo
from engine import *
from real import post, IsoR
from md import *

D = os.path.dirname(os.path.abspath(__file__))
WORDS = load_words(D)
DUR = 76.042
END = DUR + 1.5
PARCH = hexc('#F1E2BE'); INK = hexc('#3A2412'); SEA = hexc('#1D5F8A')

def caravel(cr, x, y, s, t, rock=True):
    cr.save(); cr.translate(x, y); cr.rotate(.05 * math.sin(t * 1.5) if rock else 0); cr.scale(s, s)
    cr.move_to(-220, 0); cr.line_to(220, 0); cr.line_to(170, 90); cr.line_to(-170, 90); cr.close_path(); fill(cr, hexc('#7A4A28'))
    cr.rectangle(-220, -10, 440, 20); fill(cr, hexc('#5A3418'))
    for mx, h in ((-90, 300), (60, 360)):
        cr.rectangle(mx - 6, -h, 12, h); fill(cr, hexc('#4A2A12'))
        cr.move_to(mx - 110, -h + 40); cr.curve_to(mx - 60, -h + 80, mx + 60, -h + 80, mx + 110, -h + 40); cr.line_to(mx + 110, -60); cr.curve_to(mx + 60, -30, mx - 60, -30, mx - 110, -60); cr.close_path()
        fill(cr, hexc('#F5EBD6'))
        cy = (-h + 60 - 45) / 2
        cr.set_source_rgb(*hexc('#C0392B')); cr.set_line_width(16); cr.move_to(mx, cy - 55); cr.line_to(mx, cy + 55); cr.move_to(mx - 45, cy - 10); cr.line_to(mx + 45, cy - 10); cr.stroke()
    cr.restore()

def waves(cr, t, y0, col=None, a=1.0, amp=18):
    col = col or SEA
    for k in range(4):
        yy = y0 + k * 60
        cr.move_to(0, H)
        for i in range(41):
            x = i * W / 40; cr.line_to(x, yy + math.sin(i * .7 + t * 2 + k) * amp)
        cr.line_to(W, H); cr.close_path(); fill(cr, shade(col, 1 - k * .1), a)

def calendar(cr, x, y, s, top, big, col=None):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rrect(cr, -190, -200, 380, 400, 30); fill(cr, (1, 1, 1))
    rrect(cr, -190, -200, 380, 110, 30); fill(cr, col or C['red']); cr.rectangle(-190, -130, 380, 40); fill(cr, col or C['red'])
    label(cr, top, 0, -145, 52, (1, 1, 1), 'b')
    label(cr, big, 0, 50, fit_s(cr, big, 170, 330), INK, 'b')
    cr.restore()

def microbe(cr, x, y, r, t, col):
    cr.save(); cr.translate(x, y); cr.rotate(t * .8)
    cr.set_source_rgba(*col, 1); cr.set_line_width(r * .18)
    for k in range(8):
        a = k * math.pi / 4; cr.move_to(math.cos(a) * r, math.sin(a) * r); cr.line_to(math.cos(a) * r * 1.45, math.sin(a) * r * 1.45)
    cr.stroke()
    for k in range(8):
        a = k * math.pi / 4; circle(cr, math.cos(a) * r * 1.5, math.sin(a) * r * 1.5, r * .18, col)
    circle(cr, 0, 0, r, col); circle(cr, -r * .3, -r * .2, r * .22, shade(col, .6)); circle(cr, r * .35, r * .25, r * .16, shade(col, .6))
    cr.restore()

def bubble(cr, x, y, w, h, txt, size, tail=-1, a=1.0, col=None):
    rrect(cr, x - w / 2, y - h / 2, w, h, 36); fill(cr, col or (1, 1, 1), a)
    cr.move_to(x + tail * w * .25, y + h / 2 - 2); cr.line_to(x + tail * w * .32, y + h / 2 + 60); cr.line_to(x + tail * w * .1, y + h / 2 - 2); cr.close_path(); fill(cr, col or (1, 1, 1), a)
    label(cr, txt, x, y, fit_s(cr, txt, size, w - 60), INK, 'b', a)

def oca(iso, x, y, s=1.0):
    def fn(i):
        cx, cy = i.P(x, y, 0)
        cr = i.cr; r = 70 * s * i.S / 60
        cr.save(); cr.translate(cx, cy); cr.scale(1, 1)
        cr.move_to(-r, 0); cr.curve_to(-r, -r * 1.4, r, -r * 1.4, r, 0); cr.close_path()
        g = cairo.LinearGradient(-r, 0, r, 0); g.add_color_stop_rgb(0, .85, .7, .4); g.add_color_stop_rgb(1, .6, .45, .22); cr.set_source(g); cr.fill()
        cr.set_source_rgba(.45, .32, .15, .7); cr.set_line_width(3)
        for k in range(1, 5): cr.move_to(-r * (1 - k * .03), -r * k * .2); cr.line_to(r * (1 - k * .03), -r * k * .2)
        cr.stroke()
        rrect(cr, -r * .18, -r * .45, r * .36, r * .45, r * .1); fill(cr, hexc('#3A2412'))
        cr.restore()
    iso.custom(x + y, fn)

# ---------- cenas ----------
def s0(cr, t):
    bg(cr, t, 'sepia')
    waves(cr, t, 1450, a=.9)
    caravel(cr, W / 2, 1450, 1.4, t)
    label(cr, 'ANO', W / 2, 330, 150, (1, 1, 1), 'b')
    label(cr, '1500?!', W / 2, 560, 240, C['yellow'], 'b')
    post(cr, t, vignette=.5, warm=.15)

def s1(cr, t):
    bg(cr, t, 'sepia')
    cr.save(); cam(cr, t, .4, 7.0, 1.0, 1.1)
    if t < 3.7:
        yr = int(keys(t, [(.4, 2026), (3.0, 1500)]))
        calendar(cr, W / 2, 1000, 1.6, 'HOJE', str(yr), col=hexc('#B5451B'))
        if t > 3.0: stamp(cr, t, 3.0, '1500', W / 2, 1380, col=C['yellow'], size=90)
    else:
        # mesa de pergaminho com celular virando peso de papel
        rrect(cr, 120, 820, W - 240, 560, 20); fill(cr, PARCH)
        cr.set_source_rgba(*INK, .35); cr.set_line_width(4)
        for k in range(8): cr.move_to(170, 880 + k * 60); cr.line_to(W - 170 - (k % 3) * 80, 880 + k * 60)
        cr.stroke()
        def scr(cr_, w, h, m):
            cr_.rectangle(m, m, w, h); fill(cr_, hexc('#1A1A1A'))
            label(cr_, 'SEM SINAL', m + w / 2, m + h / 2, 52, (.7, .7, .7), 'b')
        tilt = ease(prog(t, 4.8, 5.6))
        cr.save(); cr.translate(W / 2, keys(t, [(3.7, 700), (4.8, 760), (5.6, 1000)])); cr.rotate(-.6 * tilt); cr.scale(1, 1 - .35 * tilt)
        phone(cr, 0, 0, .7, scr, t); cr.restore()
    cr.restore()
    ktext(cr, t, .5, [[('Você', 's', 76), ('acorda', 'b', 100)], [('em', 's', 76), ('1500.', 'i', 150)]], y=170, t1=3.6)
    ktext(cr, t, 3.8, [[('O', 's', 72), ('celular', 'b', 100), ('virou', 's', 72)], [('peso', 'i', 110), ('de', 's', 64), ('papel.', 'i', 110)]], y=170)
    post(cr, t, warm=.12)

def medieval(iso):
    iso.quad(-12, -12, 30, 30, hexc('#8C7A5C'))
    iso.quad(-12, 2.2, 30, 2.6, hexc('#6E5A3E'))
    cols = [hexc('#E9D9B6'), hexc('#D8C49A'), hexc('#EFE3C8')]
    for k in range(6):
        house(iso, -8 + k * 3.6, -2.5, 3, 3.6, 2.8 + (k % 2) * .9, wall=cols[k % 3], roof=hexc('#8E3B22'))
        house(iso, -8 + k * 3.6, 6.2, 3, 3.6, 2.4 + (k % 3) * .6, wall=cols[(k + 1) % 3], roof=hexc('#7A3320'))

def stink(cr, x, y, t, s=1.0, a=1.0):
    cr.set_source_rgba(.55, .75, .2, .8 * a); cr.set_line_width(10 * s); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(3):
        ph = (t * .5 + k / 3) % 1
        xx = x + (k - 1) * 50 * s
        cr.move_to(xx, y - ph * 200 * s)
        for i in range(12):
            cr.line_to(xx + math.sin(i * .9 + t * 4) * 18 * s, y - ph * 200 * s - i * 14 * s)
        cr.stroke()

def s2(cr, t):
    bg(cr, t, 'sepia', grid=False)
    progress_days(cr, t, ['1 minuto', '1 dia', '1 mês', 'volta?'], 0)
    S = keys(t, [(7.0, 46), (14.9, 60)])
    iso = IsoR(cr, keys(t, [(7.0, 0), (14.9, 4)]), 3.5, 0, S, oy=.6)
    medieval(iso)
    iso.draw()
    for k in range(5):
        p = iso.P(-6 + k * 4.5, 3.5, .2); stink(cr, p[0], p[1], t + k, .9, prog(t, 8.2, 8.8))
    for k, (lbl, t0) in enumerate((('SEM ESGOTO', 9.7), ('SEM DESCARGA', 10.8), ('BANHO? RARO', 11.9))):
        if t >= t0: chip(cr, t, t0, 999, lbl, W / 2, 1180 + k * 120 - 400, col=[hexc('#7A3320'), hexc('#8E5A1B'), hexc('#4C6B1F')][k], size=48)
    ktext(cr, t, 7.2, [[('Primeiro:', 's', 72)], [('o', 's', 72), ('cheiro.', 'i', 150)]], y=200)
    post(cr, t, warm=.15)

def soap(cr, x, y, s, t):
    cr.save(); cr.translate(x, y); cr.rotate(-.08 + .03 * math.sin(t * 2)); cr.scale(s, s)
    rrect(cr, -200, -110, 400, 220, 60); fill(cr, hexc('#EADBC0'))
    rrect(cr, -180, -95, 360, 170, 50); fill(cr, hexc('#F5EBD6'))
    label(cr, 'SABÃO', 0, -10, 70, hexc('#9A7A4A'), 'b')
    for k in range(6):
        ph = (t * .4 + k / 6) % 1
        circle(cr, -150 + k * 60, -130 - ph * 220, 18 + k % 3 * 8, (1, 1, 1), .5 * (1 - ph))
    cr.restore()

def s3(cr, t):
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, 14.9, 18.8, 1.0, 1.12)
    soap(cr, W / 2, 950, 1.4 * back(prog(t, 15.0, 15.4)), t)
    if t > 16.5: chip(cr, t, 16.5, 999, 'ARTESANAL', W / 2 - 200, 1260, col=hexc('#8E5A1B'), size=46)
    if t > 17.7:
        a = back(prog(t, 17.7, 18.0))
        for k in range(5): circle(cr, W / 2 + 120 + k * 50, 1260 - k * 20, 34 * a, hexc('#F5C542')); label(cr, '$', W / 2 + 120 + k * 50, 1260 - k * 20, 40 * a, hexc('#8A6A10'), 'b')
        stamp(cr, t, 17.7, 'CARO', W / 2 + 200, 700, col=C['red'], size=90)
    cr.restore()
    ktext(cr, t, 15.0, [[('Sabão', 'i', 150), ('existe...', 'b', 90)]], y=200)
    post(cr, t)

def s4(cr, t):
    bg(cr, t, 'vinho')
    progress_days(cr, t, ['1 minuto', '1 dia', '1 mês', 'volta?'], ease(prog(t, 18.8, 19.6)))
    cr.save(); cam(cr, t, 18.8, 27.9, 1.0, 1.08, dy=-30)
    front_char(cr, 260, 1520, 520, expr='O' if t > 22.0 else 'smile', t=t)
    front_char(cr, 820, 1520, 520, expr='disgust' if t > 21.5 else 'smile', t=t, jacket=hexc('#3E5A2A'))
    if t > 20.4: bubble(cr, 330, 760, 460, 170, 'E aí, beleza?', 56, tail=-1, a=prog(t, 20.4, 20.7))
    if t > 21.6: bubble(cr, 760, 960, 480, 170, 'Vossa mercê... ?', 56, tail=1, a=prog(t, 21.6, 21.9), col=PARCH)
    if t > 22.2: label(cr, '?', 820, 760, 140, C['yellow'], 'b', prog(t, 22.2, 22.5))
    cr.restore()
    ktext(cr, t, 19.0, [[('Quase', 's', 72), ('ninguém', 'b', 100)], [('te', 's', 72), ('entende.', 'i', 130)]], y=200, t1=23.5)
    ktext(cr, t, 23.6, [[('Outro', 's', 72), ('sotaque,', 'i', 120)], [('outras', 's', 72), ('palavras.', 'b', 100)]], y=200)
    post(cr, t)

def coast(cr, t, p):
    cr.rectangle(0, 0, W, H); fill(cr, SEA)
    waves(cr, t, 400, col=shade(SEA, 1.15), a=.4, amp=10)
    cr.move_to(0, 0); cr.line_to(330, 0)
    for i in range(20):
        y = i * H / 19; cr.line_to(330 + 60 * math.sin(i * 1.3) + 30 * math.cos(i * 2.7), y)
    cr.line_to(0, H); cr.close_path(); fill(cr, hexc('#3E8E3A'))
    cr.move_to(330, 0)
    for i in range(20):
        y = i * H / 19; cr.line_to(330 + 60 * math.sin(i * 1.3) + 30 * math.cos(i * 2.7), y)
    cr.set_source_rgb(*hexc('#E8D7A0')); cr.set_line_width(26); cr.stroke()
    r = random.Random(3)
    for k in range(40):
        x, y = r.uniform(20, 280), r.uniform(0, H); circle(cr, x, y, r.uniform(20, 44), hexc('#2E7A30'))

def s5(cr, t):
    cr.save(); cam(cr, t, 27.9, 33.5, 1.0, 1.15, dx=-80)
    coast(cr, t, 0)
    for k in range(3):
        x = keys(t, [(27.9, W + 300 + k * 250), (31.5, 620 + k * 160)]); y = 900 + k * 230
        caravel(cr, x, y, .55, t + k)
    cr.restore()
    if t > 32.6: calendar(cr, 800, 1380, .7 * back(prog(t, 32.6, 33.0)), 'ABRIL', '1500')
    ktext(cr, t, 28.1, [[('Aqui', 's', 72), ('no', 's', 72), ('Brasil...', 'b', 100)]], y=170, t1=30.7)
    if t > 30.8: title(cr, t, 30.8, 999, 'CABRAL CHEGOU', y=300, size=110)
    post(cr, t)

def s6(cr, t):
    bg(cr, t, 'verde', grid=False)
    S = keys(t, [(33.5, 54), (39.8, 66)])
    iso = IsoR(cr, 2, 2, 0, S, oy=.62)
    iso.quad(-14, -14, 32, 32, hexc('#5FA34A'))
    iso.quad(-3, -3, 10, 10, hexc('#C9A86A'))
    for k in range(6):
        a = k * math.pi / 3; oca(iso, 2 + math.cos(a) * 3.5, 2 + math.sin(a) * 3.5, 1.0)
    r = random.Random(5)
    for k in range(26):
        x, y = r.uniform(-12, 16), r.uniform(-12, 16)
        if -4 < x < 8 and -4 < y < 8: continue
        tree(iso, x, y, s=r.uniform(1.0, 1.6))
    iso.draw()
    if t > 36.3:
        n = int(keys(t, [(36.3, 0), (37.2, 3)]))
        a = clamp((t - 36.3) / .3)
        rrect(cr, 90, 1220, 420, 200, 30); fill(cr, hexc('#0B2A1E'), .85 * a)
        label(cr, 'MILHÕES', 300, 1290, 64, C['yellow'], 'b', a); label(cr, 'de pessoas', 300, 1365, 44, (1, 1, 1), 's', a)
    if t > 37.7:
        a = clamp((t - 37.7) / .3)
        rrect(cr, W - 510, 1220, 420, 200, 30); fill(cr, hexc('#0B2A1E'), .85 * a)
        label(cr, 'CENTENAS', W - 300, 1290, 64, C['yellow'], 'b', a); label(cr, 'de línguas', W - 300, 1365, 44, (1, 1, 1), 's', a)
    ktext(cr, t, 33.7, [[('Quem', 's', 72), ('vive', 's', 72), ('aqui:', 'b', 100)], [('povos', 'b', 96), ('indígenas', 'i', 104)]], y=170)
    post(cr, t)

def s7(cr, t):
    bg(cr, t, 'vinho')
    progress_days(cr, t, ['1 minuto', '1 dia', '1 mês', 'volta?'], 1 + ease(prog(t, 39.8, 40.6)))
    r = random.Random(8)
    vis = ease(prog(t, 41.3, 42.4))
    for k in range(16):
        x = (r.uniform(0, W) + t * r.uniform(-30, 30)) % W; y = 500 + (r.uniform(0, 900) + t * r.uniform(-20, 20)) % 900
        cr.save(); cr.push_group(); microbe(cr, x, y, r.uniform(26, 60), t * r.uniform(.5, 1.5), r.choice([hexc('#7BD15A'), hexc('#C86BFA'), hexc('#F59A3B')])); cr.pop_group_to_source(); cr.paint_with_alpha(.85 * vis); cr.restore()
    for k, (lbl, t0) in enumerate((('VACINA', 44.0), ('ANTIBIÓTICO', 45.2))):
        if t < t0: continue
        a = back(prog(t, t0, t0 + .3)); cr.save(); cr.translate(W / 2, 760 + k * 260); cr.scale(a, a)
        card(cr, -400, -100, 800, 200, fillc=hexc('#2A1030'), border=(1, .6, .75))
        label(cr, lbl, -40, 0, fit_s(cr, lbl, 80, 560), (1, 1, 1), 'b')
        cr.set_source_rgba(*C['red'], 1); cr.set_line_width(18); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(280, -50); cr.line_to(370, 50); cr.move_to(370, -50); cr.line_to(280, 50); cr.stroke(); cr.restore()
    ktext(cr, t, 40.0, [[('O', 's', 72), ('perigo', 'b', 100), ('é', 's', 72)], [('invisível.', 'i', 140)]], y=190, t1=46.3)
    ktext(cr, t, 46.4, [[('Um', 's', 72), ('corte', 'b', 100)], [('pode', 's', 72), ('te', 's', 72), ('matar.', 'o', 130)]], y=190)
    post(cr, t)

def s8(cr, t):
    bg(cr, t, 'sepia')
    cr.save(); cam(cr, t, 49.3, 56.0, 1.0, 1.06)
    card(cr, 90, 560, W - 180, 640, fillc=hexc('#2A1A0C'), border=(1, .8, .5))
    label(cr, 'EXPECTATIVA DE VIDA AO NASCER', W / 2, 640, 38, (1, .85, .6), 'b')
    v = 30 * ease(prog(t, 51.3, 52.4))
    label(cr, f'≈{int(round(v))}', W / 2 - 70, 860, 220, C['yellow'], 'b')
    label(cr, 'anos', W / 2 + 250, 900, 70, (1, 1, 1), 'i')
    # barra
    rrect(cr, 170, 1050, W - 340, 50, 25); fill(cr, (1, 1, 1), .15)
    rrect(cr, 170, 1050, (W - 340) * v / 80, 50, 25); fill(cr, C['yellow'])
    cr.restore()
    if t > 53.2:
        a = back(prog(t, 53.2, 53.6)); cr.save(); cr.translate(W / 2, 1370); cr.scale(a, a)
        rrect(cr, -440, -80, 880, 160, 40); fill(cr, hexc('#7A3320'))
        label(cr, 'puxada pra baixo pela', 0, -28, 40, (1, 1, 1), 's'); label(cr, 'MORTE DE BEBÊS', 0, 32, 56, (1, 1, 1), 'b')
        cr.restore()
    ktext(cr, t, 49.5, [[('Em', 's', 72), ('torno', 's', 72), ('de', 's', 72)], [('trinta', 'i', 140), ('anos.', 'b', 100)]], y=170)
    post(cr, t, warm=.1)

def lemon(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.save(); cr.scale(1.3, 1); cr.arc(0, 0, 80, 0, 7); cr.restore(); fill(cr, hexc('#F5D33B'))
    circle(cr, -30, -25, 18, (1, 1, .8), .7)
    cr.move_to(95, -10); cr.line_to(125, 0); cr.line_to(95, 10); cr.close_path(); fill(cr, hexc('#E0B82A'))
    cr.restore()

def s9(cr, t):
    dark = .4 + .3 * math.sin(t * .5)
    sky_ = cairo.LinearGradient(0, 0, 0, H); sky_.add_color_stop_rgb(0, .15, .2, .3); sky_.add_color_stop_rgb(1, .3, .35, .45); cr.set_source(sky_); cr.paint()
    cr.save(); cam(cr, t, 56.0, 68.4, 1.0, 1.1)
    for k in range(6):
        cr.set_source_rgba(1, 1, 1, .08); cr.set_line_width(4)
        x = (k * 230 - t * 300) % (W + 200); cr.move_to(x, 0); cr.line_to(x - 200, H); cr.stroke()
    caravel(cr, W / 2, 1180, 1.25, t)
    waves(cr, t, 1180, col=hexc('#1B4A6E'), amp=26)
    cr.restore()
    if t < 62.7:
        if t > 59.0: calendar(cr, 820, 520, .62 * back(prog(t, 59.0, 59.4)), 'VIAGEM', '+1 MÊS', col=SEA)
        if t > 61.2: chip(cr, t, 61.2, 62.7, 'COMIDA ESTRAGADA', 330, 620, col=hexc('#5A6B1F'), size=42)
        ktext(cr, t, 56.2, [[('Voltar', 'b', 100), ('pra', 's', 72)], [('Europa?', 'i', 140)]], y=170, t1=62.7)
    else:
        a = back(prog(t, 64.9, 65.3))
        if t > 65.4:
            cr.save(); cr.translate(W / 2, 680); cr.scale(a, a)
            card(cr, -420, -150, 840, 300, fillc=hexc('#14243A'))
            label(cr, 'ESCORBUTO', 90, -40, fit_s(cr, 'ESCORBUTO', 90, 540), C['yellow'], 'b'); label(cr, '= falta de vitamina C', 90, 60, 44, (1, 1, 1), 's')
            lemon(cr, -310, 0, .65 * back(prog(t, 67.2, 67.6)))
            cr.restore()
        ktext(cr, t, 62.9, [[('Marinheiros', 'b', 100)], [('morriam', 'i', 130)]], y=170, t1=65.3)
    post(cr, t, vignette=.55)

def s10(cr, t):
    bg(cr, t, 'sepia')
    for k, (num, txt, sub, t0) in enumerate((('1', 'Tentar voltar pra', 'EUROPA', 70.3), ('2', 'Ficar com os', 'POVOS DA TERRA', 72.3))):
        if t < t0: continue
        a = back(prog(t, t0, t0 + .35)); y = 760 + k * 400
        cr.save(); cr.translate(W / 2, y); cr.scale(a, a)
        card(cr, -430, -160, 860, 320, fillc=hexc('#3A2412'), border=(1, .8, .5))
        circle(cr, -300, 0, 95, ACC); label(cr, num, -300, 0, 120, (1, 1, 1), 'b')
        label(cr, txt, 90, -55, 50, (1, .9, .75), 's'); label(cr, sub, 90, 45, fit_s(cr, sub, 90, 560), (1, 1, 1), 'b')
        cr.restore()
    ktext(cr, t, 68.7, [[('E', 's', 72), ('você?', 'i', 140)]], y=200)
    if t > 75.2: title(cr, t, 75.2, 999, 'UM OU DOIS?', y=1470, size=130)
    post(cr, t, warm=.1)

SCENES = [(0, .4, s0), (.4, 7.0, s1), (7.0, 14.9, s2), (14.9, 18.8, s3), (18.8, 27.9, s4), (27.9, 33.5, s5),
          (33.5, 39.8, s6), (39.8, 49.3, s7), (49.3, 56.0, s8), (56.0, 68.4, s9), (68.4, 999, s10)]

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
