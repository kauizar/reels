import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cairo
from engine import *
from real import post, IsoR
from md import *
from scenes import stars
from h25 import *

D = os.path.dirname(os.path.abspath(__file__))
T = Timing(D); WORDS = T.W; DUR = T.DUR; END = DUR + 1.5
b, wt = T.b, T.wt
TL = ['10 anos', '20 anos', '50 anos', '100 anos']
HAIR0 = C['hair']

def char(cr, cx, by, s, age=0.0, cane=False, **kw):
    """front_char com idade 0..1 (cabelo grisalho, rugas, bengala)."""
    C['hair'] = mix(HAIR0, hexc('#E6E6EA'), clamp(age * 1.3))
    front_char(cr, cx, by, s, **kw)
    C['hair'] = HAIR0
    u = s / 10
    if age > .25:
        cr.set_source_rgba(*shade(C['skin'], .6), clamp((age - .25) * 2)); cr.set_line_width(.09 * u)
        for k in range(2):
            y = by - 9.1 * u + k * .3 * u
            cr.move_to(cx - .9 * u, y); cr.curve_to(cx - .3 * u, y - .15 * u, cx + .3 * u, y + .15 * u, cx + .9 * u, y); cr.stroke()
        for sg in (-1, 1):
            cr.move_to(cx + sg * 1.35 * u, by - 7.6 * u); cr.line_to(cx + sg * 1.6 * u, by - 7.3 * u); cr.stroke()
    if cane:
        cr.set_source_rgb(*hexc('#6B4A35')); cr.set_line_width(.3 * u); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(cx + 2.4 * u, by); cr.line_to(cx + 2.3 * u, by - 3.6 * u); cr.curve_to(cx + 2.3 * u, by - 4.3 * u, cx + 1.7 * u, by - 4.3 * u, cx + 1.7 * u, by - 3.8 * u); cr.stroke()

def hourglass(cr, x, y, s, p, t=0.0, frozen=False):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rrect(cr, -150, -230, 300, 30, 10); fill(cr, hexc('#C98B55')); rrect(cr, -150, 200, 300, 30, 10); fill(cr, hexc('#C98B55'))
    cr.move_to(-120, -200); cr.line_to(120, -200); cr.curve_to(120, -60, 20, -30, 15, 0); cr.curve_to(20, 30, 120, 60, 120, 200); cr.line_to(-120, 200); cr.curve_to(-120, 60, -20, 30, -15, 0); cr.curve_to(-20, -30, -120, -60, -120, -200); cr.close_path()
    cr.set_source_rgba(.8, .9, 1, .25); cr.fill_preserve(); cr.set_source_rgba(1, 1, 1, .8); cr.set_line_width(6); cr.stroke()
    sand = hexc('#FFD23F')
    top = 1 - p
    if top > .02:
        cr.move_to(-100 * top, -20 - 150 * top); cr.line_to(100 * top, -20 - 150 * top); cr.line_to(0, -10); cr.close_path(); fill(cr, sand)
    cr.move_to(-110, 195); cr.line_to(110, 195); cr.line_to(0, 195 - 150 * max(.05, p)); cr.close_path(); fill(cr, sand)
    if not frozen and top > .02:
        cr.rectangle(-4, -10, 8, 200); fill(cr, sand, .9)
    cr.restore()

def s0(cr, t):
    def art(cr):
        hourglass(cr, W / 2, 1130, 1.9, .5, frozen=True)
        cr.set_source_rgba(1, 1, 1, .9)
        rrect(cr, W / 2 - 100, 1560, 70, 180, 14); fill(cr, (1, 1, 1)); rrect(cr, W / 2 + 30, 1560, 70, 180, 14); fill(cr, (1, 1, 1))
    cover(cr, t, 'noite', 'VOCÊ NÃO', 'ENVELHECE', art)

def s1(cr, t):  # 25 anos e para
    t0, t1 = .4, wt('nunca')
    bg(cr, t, 'noite')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-30)
    # bolo
    rrect(cr, W / 2 - 300, 1000, 600, 260, 40); fill(cr, hexc('#F27AA6'))
    rrect(cr, W / 2 - 300, 1000, 600, 70, 30); fill(cr, (1, 1, 1))
    label(cr, '25', W / 2, 840, 260 * back(prog(t, wt('vinte') - .1, wt('vinte') + .3)) if t > wt('vinte') - .1 else 1, C['yellow'], 'b')
    for k in (-1, 1):
        rrect(cr, W / 2 + k * 120 - 12, 940, 24, 70, 8); fill(cr, (1, 1, 1))
        fl = 1 + .15 * math.sin(t * 20 + k)
        cr.save(); cr.translate(W / 2 + k * 120, 925); cr.scale(fl, fl); cr.arc(0, 0, 16, 0, 7); cr.restore(); fill(cr, C['orange'])
    tp = wt('para')
    if t > tp:
        stamp(cr, t, tp, 'PAUSE', W / 2, 520, col=C['red'], size=110, rot=-.08)
    cr.restore()
    post(cr, t)

def s2(cr, t):  # corpo nunca mais envelhece
    t0, t1 = wt('nunca'), b(1)
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08)
    hourglass(cr, W / 2, 880, 1.6, .45, t, frozen=True)
    for k in range(5):
        ph = (t * .5 + k / 5) % 1
        circle(cr, W / 2 + math.cos(k * 1.3 + t) * 380, 880 + math.sin(k * 1.3 + t) * 420, 10, (.8, .9, 1), .6)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Nunca', 'b', 100), ('mais', 's', 72)], [('envelhece', 'i', 130)]], y=150)
    if t > wt('Só', after=t0): title(cr, t, wt('Só', after=t0), 999, 'SÓ O SEU', y=1400, size=120)
    post(cr, t)

def s3(cr, t):  # 10 anos: presente / rugas / creme
    t0, t1 = b(1), b(2)
    bg(cr, t, 'verde')
    progress_days(cr, t, TL, 0)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.07, dy=-20)
    age = .35 * ease(prog(t, wt('rugas') - .5, wt('rugas') + .5))
    char(cr, 300, 1450, 620, age=age, expr='smile', jacket=C['purple'], t=t)
    char(cr, 780, 1450, 620, age=0, expr='happy', jacket=hexc('#2F80ED'), t=t)
    label(cr, 'amigos', 300, 1510, 46, (.8, 1, .9), 'i'); label(cr, 'você', 780, 1510, 46, C['yellow'], 'b')
    if t > wt('presente'):
        a = back(prog(t, wt('presente'), wt('presente') + .3)); cr.save(); cr.translate(780, 640); cr.scale(a, a)
        rrect(cr, -90, -70, 180, 140, 16); fill(cr, C['red']); rrect(cr, -14, -70, 28, 140, 4); fill(cr, C['yellow']); rrect(cr, -90, -14, 180, 28, 4); fill(cr, C['yellow'])
        cr.restore()
    if t > wt('creme'):
        a = back(prog(t, wt('creme'), wt('creme') + .3)); cr.save(); cr.translate(330, 600); cr.scale(a, a); bubble(cr, 0, 0, 440, 110, 'qual seu creme?', size=46); cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Parece', 's', 72), ('um', 's', 72)], [('presente', 'i', 120)]], y=180, t1=wt('creme') - .2)
    post(cr, t)

def s4(cr, t):  # 20 anos: documento
    t0, t1 = b(2), wt('aeroporto') - .2
    bg(cr, t, 'gelo')
    progress_days(cr, t, TL, ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08)
    td = min(wt('documento'), t0 + .6)
    if t > td:
        a = back(prog(t, td, td + .35)); cr.save(); cr.translate(W / 2, 820); cr.scale(a, a); cr.rotate(-.04)
        rrect(cr, -440, -270, 880, 540, 36); fill(cr, hexc('#DDE8D5'))
        rrect(cr, -440, -270, 880, 90, 36); fill(cr, hexc('#2E7D4F'))
        label(cr, 'IDENTIDADE', 0, -225, 44, (1, 1, 1), 'b')
        rrect(cr, -400, -150, 280, 360, 20); fill(cr, hexc('#B9C8D6'))
        char(cr, -260, 230, 380, age=0, expr='smile', jacket=hexc('#2F80ED'))
        label(cr, 'NASC.: 1981', -80, -90, 46, hexc('#22262E'), 'b', align='l')
        label(cr, 'IDADE:', -80, 0, 46, hexc('#22262E'), 's', align='l')
        label(cr, '45', -80 + 170, 0, 96, C['red'], 'b', align='l')
        cr.restore()
    tr = wt('rosto')
    if t > tr:
        chip(cr, t, tr, 999, 'ROSTO: 25', W / 2, 1260, col=hexc('#2F80ED'), size=64)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Vinte', 'b', 100), ('anos', 's', 72), ('depois', 'i', 110)]], y=180)
    post(cr, t)

def s5(cr, t):  # aeroporto: policial olha 2x
    t0, t1 = wt('aeroporto') - .2, b(3)
    bg(cr, t, 'azul', grid=False)
    progress_days(cr, t, TL, 1)
    cr.save(); cam(cr, t, t0, t1, 1.05, 1.15, dy=-40)
    rrect(cr, 0, 1050, W, 600, 0); fill(cr, hexc('#13263F'))
    rrect(cr, 100, 980, 520, 140, 20); fill(cr, hexc('#5E6670'))
    look = math.sin(prog(t, wt('olha') - .2, t1) * math.pi * 4)
    char(cr, 330, 1000, 520, age=.3, expr='O' if look > 0 else 'disgust', jacket=hexc('#1E2A5A'), t=t)
    # quepe
    rrect(cr, 330 - 120, 1000 - 540, 240, 70, 20); fill(cr, hexc('#1E2A5A'))
    char(cr, 800, 1560, 600, age=0, expr='smile', jacket=hexc('#2F80ED'), t=t)
    # passaporte
    cr.save(); cr.translate(520 + 30 * look, 820); cr.rotate(-.1)
    rrect(cr, -80, -110, 160, 220, 16); fill(cr, hexc('#1F4E8C')); label(cr, 'PASS', 0, -40, 34, C['yellow'], 'b')
    cr.restore()
    for k in range(2):
        if t > wt('duas') + k * .3: label(cr, '?', 200 + k * 260, 360, 140, C['yellow'], 'b', prog(t, wt('duas') + k * .3, wt('duas') + k * .3 + .2))
    cr.restore()
    ktext(cr, t, t0 + .1, [[('No', 's', 72), ('aeroporto...', 'i', 110)]], y=180, t1=wt('duas'))
    post(cr, t)

def s6(cr, t):  # 50 anos: amigos de bengala, você joga bola
    t0, t1 = b(3), wt('mudar') - .2
    bg(cr, t, 'sepia')
    progress_days(cr, t, TL, 1 + ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.06)
    tp = wt('pais')
    if t < wt('amigos', after=t0) - .1:
        a = back(prog(t, tp, tp + .4)) if t > tp else 0
        if a > 0:
            cr.save(); cr.translate(W / 2, 900); cr.scale(a, a)
            for k in (-1, 1):
                rrect(cr, k * 210 - 150, -260, 300, 380, 24); fill(cr, hexc('#F3EBDD'))
                rrect(cr, k * 210 - 130, -240, 260, 280, 14); fill(cr, hexc('#7A6A5A'))
                char(cr, k * 210, 40, 260, age=.9, expr='smile', jacket=[C['purple'], C['green']][k > 0])
            label(cr, 'saudade', 0, 230, 70, ACC, 'i')
            cr.restore()
    else:
        for k in range(2):
            char(cr, 180 + k * 260, 1400, 520, age=.95, cane=True, expr='sad', jacket=[C['purple'], C['green']][k], t=t)
        bx = 800; by = 1400 - abs(math.sin(t * 5)) * 300
        char(cr, bx, 1400, 560, age=0, arm='up', expr='happy', jacket=hexc('#2F80ED'), t=t)
        circle(cr, bx + 170, by, 55, (1, 1, 1)); circle(cr, bx + 170, by, 20, C['dark'])
        if t > wt('futebol'): chip(cr, t, wt('futebol'), 999, 'FUTEBOL NO DOMINGO', W / 2, 520, col=C['green'], size=46)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Cinquenta', 'b', 100), ('anos', 'i', 110)]], y=180)
    post(cr, t)

def s7(cr, t):  # muda de cidade
    t0, t1 = wt('mudar') - .2, b(4)
    bg(cr, t, 'azul')
    progress_days(cr, t, TL, 2)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-20)
    cities = [(260, 620, 'Recife'), (800, 820, 'Lisboa'), (360, 1100, 'Curitiba'), (780, 1320, 'Tóquio')]
    p = prog(t, t0 + .2, min(t1, t0 + 3.0)) * (len(cities) - 1)
    cr.set_source_rgba(1, 1, 1, .5); cr.set_line_width(6); cr.set_dash([18, 14])
    for i in range(len(cities) - 1):
        if p > i:
            f = clamp(p - i); (x0, y0, _), (x1, y1, _) = cities[i], cities[i + 1]
            cr.move_to(x0, y0); cr.line_to(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f); cr.stroke()
    cr.set_dash([])
    for i, (x, y, nm) in enumerate(cities):
        if p >= i - .05:
            a = back(prog(p, i - .05, i + .25))
            cr.save(); cr.translate(x, y); cr.scale(a, a)
            cr.move_to(0, 0); cr.curve_to(-60, -70, -50, -130, 0, -130); cr.curve_to(50, -130, 60, -70, 0, 0); fill(cr, ACC)
            circle(cr, 0, -88, 18, (1, 1, 1)); label(cr, nm, 0, 50, 44, (1, 1, 1), 'b')
            cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Mudar', 'b', 100), ('de', 's', 72), ('cidade', 'i', 120)]], y=180)
    if t > wt('perguntas'): chip(cr, t, wt('perguntas'), 999, 'SEM PERGUNTAS', W / 2, 1480 - 0, col=C['red'], size=46)
    post(cr, t)

def s8(cr, t):  # 100 anos: solidão
    t0, t1 = b(4), b(5)
    bg(cr, t, 'noite', grid=False)
    stars(cr, a=.6)
    progress_days(cr, t, TL, 2 + ease(prog(t, t0, t0 + .8)))
    S = keys(t, [(t0, 70), (t1, 90)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.6)
    iso.quad(-14, -14, 28, 28, hexc('#2F4A3A'))
    n = int(1 + 11 * ease(prog(t, wt('enterrou') - .2, wt('enterrou') + 1.8)))
    for k in range(n):
        x, y = -6 + (k % 4) * 3.2, -4 + (k // 4) * 3.2
        iso.box(x, y, 0, .5, 1.4, 1.6, hexc('#8D96A3'), top=hexc('#B9BEC6'))
    person(iso, 4.5, 5, jacket=hexc('#2F80ED'))
    iso.draw(night=.35)
    ts = wt('solidão')
    if t > ts - .2:
        cr.set_source_rgba(0, 0, 0, .45 * prog(t, ts - .2, ts + .3)); cr.paint()
        title(cr, t, ts - .1, 999, 'SOLIDÃO', y=820, size=170, col=C['white'])
        label(cr, 'que nenhum humano viveu', W / 2, 1000, 56, ACC, 'i', prog(t, ts + .3, ts + .7))
    ktext(cr, t, t0 + .1, [[('Cem', 'b', 110), ('anos', 'i', 120)]], y=180, t1=ts - .2)
    post(cr, t, vignette=.6)

def jelly(cr, x, y, s, t, a=1.0, col=None):
    col = col or hexc('#FF8FB1')
    cr.save(); cr.translate(x, y); cr.scale(s, s * (1 + .08 * math.sin(t * 3)))
    rg = cairo.RadialGradient(0, -40, 10, 0, -20, 160); rg.add_color_stop_rgba(0, 1, 1, 1, .9 * a); rg.add_color_stop_rgba(1, *col, .85 * a)
    cr.move_to(-140, 0); cr.curve_to(-140, -170, 140, -170, 140, 0); cr.curve_to(80, 25, -80, 25, -140, 0); cr.set_source(rg); cr.fill()
    cr.set_source_rgba(*col, .8 * a); cr.set_line_width(8); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(6):
        x0 = -110 + k * 44
        cr.move_to(x0, 10)
        for j in range(1, 8): cr.line_to(x0 + 14 * math.sin(t * 3 + j * .9 + k), 10 + j * 32)
        cr.stroke()
    circle(cr, 0, -60, 36, hexc('#E8473C'), .8 * a)
    cr.restore()

def s9(cr, t):  # água-viva imortal
    t0, t1 = b(5), b(6)
    bg(cr, t, 'gelo')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-30)
    # ciclo: adulta -> pólipo -> jovem (seta de volta)
    tv = wt('voltar')
    if t < tv:
        jelly(cr, W / 2, 820 + 20 * math.sin(t), 2.0, t)
        label(cr, 'Turritopsis dohrnii', W / 2, 1220, 54, (.8, .95, 1), 'i')
        label(cr, '~5 mm', W / 2, 1320, 64, C['yellow'], 'b')
    else:
        p = ease(prog(t, tv, tv + 1.5))
        jelly(cr, W / 2 - 250, 820, 1.4 - .4 * p, t, a=1 - .5 * p)
        jelly(cr, W / 2 + 250, 820, .5 + .5 * p, t, a=p)
        cr.set_source_rgba(*C['yellow'], 1); cr.set_line_width(14); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.arc_negative(W / 2, 1000, 240, -.3, math.pi + .3); cr.stroke()
        label(cr, 'volta a ser jovem', W / 2, 1310, 62, (1, 1, 1), 'i')
    if t > wt('imortal'): stamp(cr, t, wt('imortal'), 'IMORTAL', W / 2, 560, col=ACC, size=100)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Na', 's', 72), ('natureza...', 'i', 120)]], y=170, t1=wt('imortal'))
    post(cr, t)

def s10(cr, t):  # 200 anos
    t0, t1 = b(6), b(7)
    bg(cr, t, 'noite')
    yr = int(2026 + 200 * ease(prog(t, wt('duzentos'), t1 - .3)))
    S = keys(t, [(t0, 52), (t1, 62)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.66)
    iso.quad(-30, -30, 60, 60, hexc('#3A4150'))
    r = random.Random(yr // 25)
    for gx in range(-3, 4):
        for gy in range(-3, 4):
            if gx == 0 and gy == 0: continue
            fl = r.randint(2, 4 + (yr - 2026) // 40)
            building(iso, gx * 4.5 - 1.5, gy * 4.5 - 1.5, 3, 3, fl, r.choice([hexc('#8FA3B8'), hexc('#6E829A'), hexc('#9AA7C7'), hexc('#7FD3FF')]), glass=yr > 2120)
    person(iso, 0, 0, jacket=hexc('#2F80ED'), s=1.6)
    iso.draw(night=.4)
    card(cr, W / 2 - 260, 330, 520, 170, r=30, fillc=hexc('#0F1236'))
    label(cr, str(yr), W / 2, 415, 120, C['yellow'], 'b')
    ktext(cr, t, t0 + .1, [[('Duzentos', 'b', 100), ('anos', 'i', 110)]], y=140)
    if t > wt('ninguém', after=t0): chip(cr, t, wt('ninguém', after=t0), 999, 'SEM NINGUÉM PRA LEMBRAR', W / 2, 1450, col=C['purple'], size=44)
    post(cr, t)

def s11(cr, t):  # CTA
    t0 = b(7)
    bg(cr, t, 'vinho')
    hourglass(cr, W / 2, 1300, 1.0, .5, t, frozen=True)
    ktext(cr, t, t0 + .05, [[('E', 's', 72), ('você?', 'i', 140)]], y=170)
    cta(cr, t, t0 + .3, 'Aceitaria não envelhecer?', 'SIM ou NÃO?')
    post(cr, t)

SCENES = [(0, .4, s0), (.4, wt('nunca'), s1), (wt('nunca'), b(1), s2), (b(1), b(2), s3), (b(2), wt('aeroporto') - .2, s4),
          (wt('aeroporto') - .2, b(3), s5), (b(3), wt('mudar') - .2, s6), (wt('mudar') - .2, b(4), s7), (b(4), b(5), s8),
          (b(5), b(6), s9), (b(6), b(7), s10), (b(7), 999, s11)]
render = make_render(SCENES, WORDS, DUR)
