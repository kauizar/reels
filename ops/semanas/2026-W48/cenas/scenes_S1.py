import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cairo
from engine import *
from real import post, IsoR
from md import *
from h25 import *

D = os.path.dirname(os.path.abspath(__file__))
T = Timing(D); WORDS = T.W; DUR = T.DUR; END = DUR + 1.5
b, wt = T.b, T.wt
PINK = hexc('#FF8FB1'); CY = hexc('#7FE8FF')
TL = ['1 hora', '1 dia', '1 semana', '1 mês']

def heads_row(cr, t, y, n, s, seed=1, think=None):
    r = random.Random(seed)
    for k in range(n):
        x = W * (k + .5) / n
        front_char(cr, x, y, s, expr=r.choice(['smile', 'O', 'shock']), jacket=r.choice([C['jacket'], hexc('#2F80ED'), C['green'], C['orange'], C['purple']]), t=t + k)
        if think: think(cr, k, x, y - s * 1.05)

def s0(cr, t):
    def art(cr):
        brain(cr, W / 2, 1150, 1.6, PINK, glow=1)
        for k, (x, y, w) in enumerate(((250, 820, 260), (840, 880, 240), (300, 1420, 220), (820, 1450, 250))):
            bubble(cr, x, y, w, 100, ['chato', 'mentira', 'fome', 'crush'][k], size=46)
    cover(cr, t, 'vinho', 'LERAM SUA', 'MENTE', art)

def s1(cr, t):  # padaria
    t0, t1 = .4, wt('Hoje')
    bg(cr, t, 'sepia')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-30)
    rrect(cr, 60, 1080, W - 120, 120, 20); fill(cr, hexc('#8A5A35'))
    rrect(cr, 60, 1060, W - 120, 40, 14); fill(cr, hexc('#C98B55'))
    for k in range(4):
        circle(cr, 200 + k * 120, 1040, 42, hexc('#E8B56A')); circle(cr, 200 + k * 120, 1030, 30, hexc('#F3CF8E'))
    front_char(cr, 770, 1080, 520, expr='smile' if t < wt('sabe') else 'disgust', jacket=hexc('#FFFFFF'), t=t)
    front_char(cr, 280, 1560, 640, expr='smile' if t < wt('sabe') else 'shock', jacket=hexc('#2F80ED'), t=t)
    if t > wt('pensou'):
        a = back(prog(t, wt('pensou'), wt('pensou') + .3))
        cr.save(); cr.translate(330, 560); cr.scale(a, a); bubble(cr, 0, 0, 420, 120, '"que demora..."', size=48); cr.restore()
    if t > wt('sabe'):
        stamp(cr, t, wt('sabe'), 'ELE OUVIU', 760, 420, col=C['red'], size=70)
    cr.restore()
    ktext(cr, t, .5, [[('Na', 's', 70), ('padaria', 'i', 120)]], y=150, t1=wt('pensou') - .05)
    post(cr, t)

def s2(cr, t):  # todo mundo lê todo mundo
    t0, t1 = wt('Hoje'), b(1)
    bg(cr, t, 'noite')
    S = keys(t, [(t0, 92), (t1, 108)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.62)
    iso.quad(-30, -30, 60, 60, hexc('#3B3F6B'))
    r = random.Random(3); pts = []
    for k in range(14):
        x, y = r.uniform(-4.5, 4.5), r.uniform(-4.5, 4.5); pts.append((x, y))
        person(iso, x, y, jacket=r.choice([C['jacket'], hexc('#2F80ED'), C['green'], C['orange'], C['pink']]), phase=t * 2 + k)
    iso.draw()
    words = ['bobo', 'chato', 'lindo', 'fome', 'mentira', 'saudade', 'medo', 'tédio', 'uau', 'credo', 'sono', 'raiva', 'vergonha', 'dinheiro']
    for k, (x, y) in enumerate(pts):
        tk = t0 + .2 + k * .08
        if t > tk:
            p = iso.P(x, y, 3.2); a = back(prog(t, tk, tk + .3))
            cr.save(); cr.translate(clamp(p[0], 130, W - 130), p[1] - 40); cr.scale(a * .8, a * .8); bubble(cr, 0, 0, 230, 80, words[k], size=40); cr.restore()
    ktext(cr, t, t0 + .1, [[('Todo', 'b', 96), ('mundo', 'b', 96)], [('lê', 's', 70), ('todo', 's', 70), ('mundo', 'i', 120)]], y=150)
    post(cr, t)

def s3(cr, t):  # Queen's 6 mil
    t0, t1 = b(1), wt('Agora')
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-40)
    a = back(prog(t, t0 + .3, t0 + .7))
    cr.save(); cr.translate(W / 2, 640); cr.scale(a, a)
    card(cr, -420, -170, 840, 340, fillc=hexc('#10204A'))
    label(cr, 'ESTUDO', 0, -95, 40, (.7, .8, 1), 's')
    label(cr, "Queen's University", 0, -20, 62, (1, 1, 1), 'b')
    label(cr, 'Canadá', 0, 70, 56, ACC, 'i')
    cr.restore()
    tc = wt('seis')
    if t > tc:
        n = int(6000 * ease(prog(t, tc, tc + 1.4)))
        s = f'{n:,}'.replace(',', '.')
        label(cr, s, W / 2, 1050, fit_s(cr, '6.000', 230, 900) * back(prog(t, tc, tc + .3)), C['yellow'], 'b')
        if t > wt('pensamentos'): label(cr, 'pensamentos por dia', W / 2, 1220, 62, (1, 1, 1), 'i', prog(t, wt('pensamentos'), wt('pensamentos') + .3))
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Mais', 's', 72), ('de', 's', 72)], [('seis', 'b', 110), ('mil', 'i', 130)]], y=140, t1=t1)
    post(cr, t)

def s4(cr, t):  # em voz alta
    t0, t1 = wt('Agora'), b(2)
    bg(cr, t, 'vinho')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.15)
    brain(cr, W / 2, 900, 1.3 + .05 * math.sin(t * 8), PINK, glow=1, t=t)
    r = random.Random(5)
    txts = ['ai que sono', 'boleto', 'ex', 'pizza', 'que roupa é essa', 'mentira!', 'chato', 'quero ir embora', 'kkk', 'grrr', 'socorro']
    for k, tx in enumerate(txts):
        tk = t0 + .2 + k * .12
        if t < tk: continue
        ang = k * 2.4; d = 280 + 220 * eout(prog(t, tk, tk + .8)) + 30 * (k % 3)
        x, y = W / 2 + math.cos(ang) * d * 1.0, 900 + math.sin(ang) * d * 1.2
        bubble(cr, x, y, 60 + 24 * len(tx), 84, tx, size=38, a=.95)
    cr.restore()
    # ondas de som
    for k in range(3):
        ph = (t * .8 + k / 3) % 1
        cr.set_source_rgba(1, 1, 1, .35 * (1 - ph)); cr.set_line_width(6); cr.arc(W / 2, 900, 200 + ph * 600, 0, 7); cr.stroke()
    ktext(cr, t, t0 + .1, [[('Em', 's', 72), ('voz', 'b', 110), ('alta.', 'i', 130)]], y=150)
    post(cr, t)

def s5(cr, t):  # primeira hora: caos na reunião
    t0, t1 = b(2), b(3)
    bg(cr, t, 'azul')
    progress_days(cr, t, TL, 0)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08, dy=-20)
    rrect(cr, 120, 1150, W - 240, 70, 20); fill(cr, hexc('#8A5A35'))
    for k in range(4):
        x = 200 + k * 230
        front_char(cr, x, 1150, 380, expr='shock' if t > wt('ouviu') else 'smile', jacket=[hexc('#2F80ED'), C['jacket'], C['green'], C['purple']][k], t=t + k)
    card(cr, 300, 440, 480, 150, fillc=hexc('#FFFFFF'), border=(1, 1, 1))
    label(cr, 'REUNIÃO', 540, 480, 36, hexc('#1B2C5E'), 's'); label(cr, 'Q4 metas', 540, 540, 54, hexc('#1B2C5E'), 'b')
    if t > wt('corte'):
        a = back(prog(t, wt('corte'), wt('corte') + .3)); cr.save(); cr.translate(300, 620); cr.scale(a, a); bubble(cr, 0, 0, 440, 110, 'que corte é esse?', size=44); cr.restore()
    if t > wt('vontade'):
        a = back(prog(t, wt('vontade'), wt('vontade') + .3)); cr.save(); cr.translate(760, 760); cr.scale(a, a); bubble(cr, 0, 0, 440, 110, 'quero ir embora', size=44, tail=-1); cr.restore()
    if t > wt('ouviu'):
        stamp(cr, t, wt('ouviu'), 'TODO MUNDO OUVIU', W / 2, 1350, size=62, col=C['red'])
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeira', 's', 72), ('hora', 'i', 130)], [('CAOS', 'b', 120)]], y=180, t1=wt('corte') + .8)
    post(cr, t)

def s6(cr, t):  # primeiro dia: chefe e crush
    t0, t1 = b(3), wt('família') - .6
    bg(cr, t, 'gelo')
    progress_days(cr, t, TL, ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.06)
    tc = wt('chefe')
    if t > tc:
        a = back(prog(t, tc, tc + .35)); cr.save(); cr.translate(W / 2, 560); cr.scale(a, a)
        card(cr, -430, -190, 860, 380, fillc=hexc('#12304D'))
        front_char(cr, -250, 170, 300, expr='disgust', jacket=C['dark'], t=t)
        label(cr, 'CHEFE', 100, -110, 56, (1, 1, 1), 'b')
        label(cr, 'sabe que você', 100, -20, 44, (.8, .85, 1), 's')
        label(cr, 'enrolou', 100, 60, 84, ACC, 'i')
        cr.restore()
    tk = wt('crush')
    if t > tk:
        a = back(prog(t, tk, tk + .35)); cr.save(); cr.translate(W / 2, 1100); cr.scale(a, a)
        card(cr, -430, -170, 860, 340, fillc=hexc('#3E0B22'), border=(1, .6, .75))
        hb = 1 + .1 * abs(math.sin(t * 6))
        cr.save(); cr.translate(-260, 0); cr.scale(hb, hb)
        cr.move_to(0, 60); cr.curve_to(-140, -40, -70, -140, 0, -60); cr.curve_to(70, -140, 140, -40, 0, 60); fill(cr, hexc('#FF4F7B')); cr.restore()
        label(cr, 'CRUSH', 110, -60, 64, (1, 1, 1), 'b'); label(cr, 'já sabe', 110, 40, 80, hexc('#FF8FB1'), 'i')
        cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeiro', 's', 72), ('dia', 'i', 130)]], y=180, t1=tc + .1)
    post(cr, t)

def s7(cr, t):  # família
    t0, t1 = wt('família') - .6, b(4)
    bg(cr, t, 'sepia')
    S = keys(t, [(t0, 88), (t1, 100)])
    iso = IsoR(cr, 0, 0, 0, S, oy=.62)
    iso.quad(-12, -12, 24, 24, hexc('#8A6A4A'))
    iso.box(-3, -1.5, 0, 6, 3, .9, hexc('#C98B55'))
    seats = [(-4, 0), (4, 0), (0, -3), (-2, 2.8), (2, 2.8)]
    for k, (x, y) in enumerate(seats): person(iso, x, y, jacket=[C['jacket'], C['green'], C['purple'], C['orange'], hexc('#2F80ED')][k], phase=t + k)
    iso.draw()
    progress_days(cr, t, TL, 1)
    txts = ['folgado', 'meu orgulho', 'ainda solteiro?', 'devia estudar', '']
    for k, (x, y) in enumerate(seats[:4]):
        tk = wt('família') + .2 + k * .3
        if t > tk:
            p = iso.P(x, y, 3.5); a = back(prog(t, tk, tk + .3))
            cr.save(); cr.translate(clamp(p[0], 200, W - 200), p[1] - 30); cr.scale(a * .85, a * .85); bubble(cr, 0, 0, 380, 96, txts[k], size=44); cr.restore()
    ktext(cr, t, t0 + .1, [[('O', 's', 72), ('que', 's', 72), ('a', 's', 72), ('família', 'i', 120)], [('pensa', 'b', 100), ('de', 's', 72), ('verdade', 'b', 100)]], y=180)
    post(cr, t)

def cards_x(cr, t, items, y0=560, dy=270, col=None):
    for k, (txt, tk) in enumerate(items):
        if t < tk: continue
        a = back(prog(t, tk, tk + .3)); cr.save(); cr.translate(W / 2, y0 + k * dy); cr.scale(a, a)
        card(cr, -400, -100, 800, 200, fillc=hexc('#1A1450'), border=(.7, .6, 1))
        label(cr, txt, 40, 0, fit_s(cr, txt, 70, 560), (1, 1, 1), 'b')
        cr.set_source_rgba(*C['red'], 1); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(-330, -50); cr.line_to(-230, 50); cr.move_to(-230, -50); cr.line_to(-330, 50); cr.stroke()
        cr.restore()

def s8(cr, t):  # primeira semana: mentira morre
    t0, t1 = b(4), wt('Políticos') - .1
    bg(cr, t, 'noite')
    progress_days(cr, t, TL, 1 + ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.07)
    tm = t0 + .3
    if t > tm:
        # túmulo da mentira
        a = back(prog(t, tm, tm + .35)); cr.save(); cr.translate(W / 2, 760); cr.scale(a, a)
        cr.move_to(-170, 160); cr.line_to(-170, -60); cr.curve_to(-170, -220, 170, -220, 170, -60); cr.line_to(170, 160); cr.close_path(); fill(cr, hexc('#8D96A3'))
        label(cr, 'R.I.P.', 0, -60, 64, hexc('#2B3566'), 'b'); label(cr, 'MENTIRA', 0, 40, 50, hexc('#2B3566'), 'b')
        rrect(cr, -260, 150, 520, 40, 10); fill(cr, hexc('#3CC46A'))
        cr.restore()
    cards_x(cr, t, [('Blefe no truco', wt('blefar')), ('"Amei o presente!"', wt('presente'))], y0=1120, dy=230)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeira', 's', 72), ('semana', 'i', 120)]], y=180)
    post(cr, t)

def s9(cr, t):  # políticos, vendedores, golpistas
    t0, t1 = wt('Políticos') - .1, b(5)
    bg(cr, t, 'vinho')
    progress_days(cr, t, TL, 2)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08, dy=-20)
    for k, (nm, w) in enumerate((('POLÍTICOS', 'Políticos'), ('VENDEDORES', 'vendedores'), ('GOLPISTAS', 'golpistas'))):
        tk = wt(w, after=t0 - .5)
        if t < tk: continue
        a = back(prog(t, tk, tk + .3)); y = 450 + k * 300
        cr.save(); cr.translate(W / 2, y); cr.scale(a, a)
        card(cr, -420, -120, 840, 240, fillc=hexc('#2A1030'), border=(1, .6, .75))
        front_char(cr, -300, 110, 210, expr='sad', jacket=[C['dark'], hexc('#2F80ED'), C['purple']][k], t=t)
        label(cr, nm, 80, 0, fit_s(cr, nm, 80, 560), (1, 1, 1), 'b')
        cr.restore()
    te = wt('emprego')
    if t > te: stamp(cr, t, te, 'DESEMPREGADOS', W / 2, 1330, size=70, col=C['red'])
    cr.restore()
    post(cr, t)

def s10(cr, t):  # primeiro mês: silêncio
    t0, t1 = b(5), b(6)
    bg(cr, t, 'verde')
    progress_days(cr, t, TL, 2 + ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-40)
    if t < wt('silêncio') - .3:
        # meditação
        y = 1100 + 12 * math.sin(t * 2)
        front_char(cr, W / 2, y, 560, expr='smile', arm='up', jacket=hexc('#2FD38A'), t=0)
        for k in range(3):
            ph = (t * .5 + k / 3) % 1
            cr.set_source_rgba(.6, 1, .8, .5 * (1 - ph)); cr.set_line_width(5); cr.arc(W / 2, y - 420, 120 + ph * 360, 0, 7); cr.stroke()
        if t > wt('Meditação'): chip(cr, t, wt('Meditação'), 999, 'MEDITAÇÃO = MODA', W / 2, 1200, size=48)
    else:
        ts = wt('silêncio')
        a = back(prog(t, ts - .3, ts))
        cr.save(); cr.translate(W / 2, 800); cr.scale(a, a)
        card(cr, -400, -330, 800, 660, fillc=hexc('#073B3A'), border=(.6, 1, .8))
        label(cr, 'ZONA DE', 0, -220, 60, (.8, 1, .9), 's'); label(cr, 'SILÊNCIO', 0, -130, 110, (1, 1, 1), 'b')
        # cadeado/mente
        brain(cr, 0, 70, .55, hexc('#9AF0C8'))
        cr.set_source_rgba(1, 1, 1, .9); cr.set_line_width(14); cr.arc(0, 70, 150, 0, 7); cr.stroke()
        if t > wt('ninguém', after=ts) - .2:
            rrect(cr, -230, 220, 460, 90, 45); fill(cr, C['yellow'])
            label(cr, 'R$ 999 / hora', 0, 265, 52, hexc('#073B3A'), 'b')
        cr.restore()
        chip(cr, t, wt('luxo'), 999, 'NOVO LUXO', W / 2, 330, size=52)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeiro', 's', 72), ('mês', 'i', 130)]], y=180, t1=wt('luxo') - .1)
    post(cr, t)

def s11(cr, t):  # honesto x gentil
    t0, t1 = b(6), b(7)
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, t0, t1, .95, 1.02)
    tilt = .25 * ease(prog(t, t0 + .4, t0 + 1.4)) - .4 * ease(prog(t, wt('gentil') - .2, wt('gentil') + .6))
    cx, cy = W / 2, 820
    rrect(cr, cx - 15, cy, 30, 520, 10); fill(cr, hexc('#C9D1DA'))
    rrect(cr, cx - 160, cy + 500, 320, 40, 14); fill(cr, hexc('#C9D1DA'))
    cr.save(); cr.translate(cx, cy); cr.rotate(tilt)
    rrect(cr, -340, -12, 680, 24, 10); fill(cr, hexc('#E8ECF2'))
    for sgn, txt, col, tw in ((-1, 'HONESTO', hexc('#3CC46A'), wt('honesto')), (1, 'GENTIL?', hexc('#FF4F7B'), wt('gentil'))):
        x = sgn * 300
        cr.save(); cr.translate(x, 0); cr.rotate(-tilt)
        cr.set_source_rgba(1, 1, 1, .7); cr.set_line_width(4); cr.move_to(0, 0); cr.line_to(-120, 200); cr.move_to(0, 0); cr.line_to(120, 200); cr.stroke()
        rrect(cr, -150, 200, 300, 40, 18); fill(cr, hexc('#E8ECF2'))
        if t > tw:
            a = back(prog(t, tw, tw + .3)); cr.save(); cr.translate(0, 140); cr.scale(a, a)
            rrect(cr, -150, -50, 300, 100, 22); fill(cr, col); label(cr, txt, 0, 0, fit_s(cr, txt, 54, 260), (1, 1, 1), 'b'); cr.restore()
        cr.restore()
    cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('No', 's', 72), ('fim...', 'i', 130)]], y=200)
    post(cr, t)

def s12(cr, t):  # CTA
    t0 = b(7)
    bg(cr, t, 'vinho')
    ktext(cr, t, t0 + .05, [[('E', 's', 72), ('você?', 'i', 140)]], y=170)
    cta(cr, t, t0 + .3, 'Ia querer esse mundo?', 'SIM ou NÃO?')
    if t > wt('manda', after=t0):
        tm = wt('manda', after=t0); a = back(prog(t, tm, tm + .35))
        cr.save(); cr.translate(W / 2, 1220); cr.scale(a, a)
        card(cr, -420, -110, 840, 220, fillc=hexc('#10204A'))
        cr.move_to(-330, 40); cr.line_to(-230, -50); cr.line_to(-250, 20); cr.close_path(); fill(cr, ACC)
        label(cr, 'Manda pra quem', 60, -35, 52, (1, 1, 1), 'b'); label(cr, 'ia te dar vergonha', 60, 40, 50, ACC, 'i')
        cr.restore()
    post(cr, t)

SCENES = [(0, .4, s0), (.4, wt('Hoje'), s1), (wt('Hoje'), b(1), s2), (b(1), wt('Agora'), s3), (wt('Agora'), b(2), s4),
          (b(2), b(3), s5), (b(3), wt('família') - .6, s6), (wt('família') - .6, b(4), s7), (b(4), wt('Políticos') - .1, s8),
          (wt('Políticos') - .1, b(5), s9), (b(5), b(6), s10), (b(6), b(7), s11), (b(7), 999, s12)]
render = make_render(SCENES, WORDS, DUR)
