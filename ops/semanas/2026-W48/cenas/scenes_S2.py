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
WAT = hexc('#4AA8F0'); WAT2 = hexc('#7FD3FF')
TL = ['horas', 'dia 1', 'dia 2', 'dia 3']

def drop(cr, x, y, s, col=None, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(0, -120); cr.curve_to(40, -60, 90, -10, 90, 40); cr.curve_to(90, 100, 45, 130, 0, 130); cr.curve_to(-45, 130, -90, 100, -90, 40); cr.curve_to(-90, -10, -40, -60, 0, -120)
    cr.close_path(); fill(cr, col or WAT, a)
    cr.save(); cr.scale(.6, 1); cr.arc(-60, 30, 22, 0, 7); cr.restore(); fill(cr, (1, 1, 1), .5 * a)
    cr.restore()

def glass(cr, x, y, s, level, t=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-120, -200); cr.line_to(120, -200); cr.line_to(95, 200); cr.line_to(-95, 200); cr.close_path()
    cr.set_source_rgba(1, 1, 1, .15); cr.fill_preserve(); cr.set_source_rgba(1, 1, 1, .8); cr.set_line_width(8); cr.stroke()
    if level > 0.01:
        top = 200 - 390 * level
        wv = 6 * math.sin(t * 4)
        xt = 95 + 25 * (200 - top) / 400
        cr.move_to(-xt, top + wv); cr.curve_to(-30, top - wv, 30, top + wv, xt, top - wv); cr.line_to(95, 196); cr.line_to(-95, 196); cr.close_path(); fill(cr, WAT, .9)
    cr.restore()

def s0(cr, t):
    def art(cr):
        drop(cr, W / 2, 1120, 3.2, WAT)
        cr.set_source_rgba(*C['red'], 1); cr.set_line_width(40); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(W / 2 - 330, 820); cr.line_to(W / 2 + 330, 1440); cr.stroke()
    cover(cr, t, 'gelo', '3 DIAS', 'SEM ÁGUA', art)

def s1(cr, t):  # último gole segunda 8h
    t0, t1 = .4, wt('próximo')
    bg(cr, t, 'gelo')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-30)
    lv = .8 * (1 - ease(prog(t, wt('gole') - .2, wt('água') + .4)))
    glass(cr, W / 2 + 160, 1050, 1.3, lv, t)
    front_char(cr, 300, 1560, 640, expr='smile', arm='down', jacket=hexc('#2F80ED'), t=t)
    card(cr, W / 2 - 300, 330, 600, 220, fillc=hexc('#0F2236'))
    label(cr, 'SEGUNDA', W / 2, 390, 46, (.8, .9, 1), 's')
    label(cr, '08:00', W / 2, 480, 110 * back(prog(t, wt('oito') - .1, wt('oito') + .2)) if t > wt('oito') - .1 else 1, C['yellow'], 'b')
    cr.restore()
    ktext(cr, t, .5, [[('Último', 'b', 96), ('gole', 'i', 120)]], y=140)
    post(cr, t)

def s2(cr, t):  # próximo só na quinta
    t0, t1 = wt('próximo'), b(1)
    bg(cr, t, 'azul')
    days = ['SEG', 'TER', 'QUA', 'QUI']
    sweep = ease(prog(t, t0 + .2, t1 - .3)) * 3
    for k, d in enumerate(days):
        x = 165 + k * 250; y = 850
        a = back(prog(t, t0 + k * .1, t0 + k * .1 + .3))
        cr.save(); cr.translate(x, y); cr.scale(a, a)
        on = k == 3
        card(cr, -110, -160, 220, 320, fillc=hexc('#12304D') if not on else hexc('#1F6B4A'), border=(1, 1, 1) if on else None)
        label(cr, d, 0, -90, 54, (1, 1, 1), 'b')
        if k < 3 and sweep > k + .5:
            cr.set_source_rgba(*C['red'], 1); cr.set_line_width(14); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(-60, 0); cr.line_to(60, 110); cr.move_to(60, 0); cr.line_to(-60, 110); cr.stroke()
        if on: drop(cr, 0, 60, .55, WAT2)
        cr.restore()
    # sol atravessando
    sx = 165 + sweep * 250
    circle(cr, sx, 560, 50, C['sun'], .95)
    if t > t0 + .3: counter(cr, t, t0 + .3, 999, '72 HORAS', None, y=1260)
    ktext(cr, t, t0 + .1, [[('Próximo', 's', 72), ('gole:', 's', 72)], [('só', 'b', 100), ('quinta', 'i', 130)]], y=140)
    post(cr, t)

def body(cr, x, y, s, level, col=WAT):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    def shape():
        cr.new_path(); cr.arc(0, -330, 90, 0, 7)
        rrect(cr, -150, -230, 300, 360, 70)
        rrect(cr, -140, 120, 120, 320, 50); rrect(cr, 20, 120, 120, 320, 50)
        rrect(cr, -230, -210, 80, 300, 40); rrect(cr, 150, -210, 80, 300, 40)
    shape(); cr.set_source_rgba(1, 1, 1, .12); cr.fill()
    cr.save(); shape(); cr.clip()
    top = 440 - 860 * level
    cr.rectangle(-300, top, 600, 1000); fill(cr, col, .85)
    cr.restore()
    shape(); cr.set_source_rgba(1, 1, 1, .7); cr.set_line_width(6); cr.stroke()
    cr.restore()

def s3(cr, t):  # perde 2,5 L por dia
    t0, t1 = b(1), b(2)
    bg(cr, t, 'gelo')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.07, dy=-20)
    lv = .9 - .25 * ease(prog(t, wt('perde'), t1))
    body(cr, 330, 1000, 1.0, lv)
    tl = wt('dois')
    if t > tl:
        a = back(prog(t, tl, tl + .3)); cr.save(); cr.translate(780, 560); cr.scale(a, a)
        card(cr, -230, -130, 460, 260, fillc=hexc('#0F2236'))
        label(cr, '-2,5 L', 0, -20, 110, C['yellow'], 'b'); label(cr, 'por dia', 0, 75, 50, (.8, .9, 1), 'i'); cr.restore()
    for k, (nm, w) in enumerate((('XIXI', 'xixi'), ('SUOR', 'suor'), ('RESPIRAÇÃO', 'respiração'))):
        tk = wt(w)
        if t > tk:
            chip(cr, t, tk, 999, nm, 780, 850 + k * 170, col=[hexc('#E0B020'), hexc('#2F80ED'), hexc('#7A5CFF')][k], size=50)
    # gotas saindo
    for k in range(6):
        ph = (t * .9 + k / 6) % 1
        drop(cr, 330 + math.cos(k * 1.7) * (180 + ph * 200), 900 + math.sin(k * 1.7) * 200 + ph * 200, .25, WAT2, 1 - ph)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Todo', 's', 72), ('dia', 'i', 120)]], y=140)
    post(cr, t)

def s4(cr, t):  # primeiras horas: sede, 2%
    t0, t1 = b(2), b(3)
    bg(cr, t, 'sepia')
    progress_days(cr, t, TL, 0)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08, dy=-30)
    front_char(cr, 330, 1500, 600, expr='sad' if t < wt('quando') else 'O', jacket=hexc('#2F80ED'), t=t)
    if t > wt('sede'):
        chip(cr, t, wt('sede'), 999, 'SEDE', 760, 480, col=C['orange'], size=60)
    if t > wt('boca'):
        chip(cr, t, wt('boca'), 999, 'BOCA SECA', 760, 640, col=C['red'], size=52)
    tp = wt('dois', after=t0)
    if t > tp:
        a = back(prog(t, tp, tp + .3)); cr.save(); cr.translate(760, 930); cr.scale(a, a)
        card(cr, -230, -150, 460, 300, fillc=hexc('#3A2412'), border=(1, .8, .5))
        label(cr, '-2%', 0, -30, 130, C['yellow'], 'b'); label(cr, 'da sua água', 0, 85, 44, (1, .9, .8), 'i'); cr.restore()
    if t > wt('devagar'):
        a = back(prog(t, wt('devagar'), wt('devagar') + .3)); cr.save(); cr.translate(760, 1260); cr.scale(a, a)
        brain(cr, -120, 0, .55, hexc('#FF8FB1'))
        label(cr, 'lento', 110, 0, 96, ACC, 'i'); cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeiras', 's', 72), ('horas', 'i', 120)]], y=180)
    post(cr, t)

def s5(cr, t):  # dia 1: xixi escuro, rins
    t0, t1 = b(3), wt('cabeça') - .2
    bg(cr, t, 'verde')
    progress_days(cr, t, TL, ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.06)
    cols = [hexc('#FFF6C9'), hexc('#FBE38A'), hexc('#F3C94A'), hexc('#D99A1E'), hexc('#A8650F')]
    pos = ease(prog(t, wt('xixi', after=t0), wt('escuro') + .4)) * 4
    for k, c in enumerate(cols):
        rrect(cr, 140 + k * 165, 420, 140, 200, 24); fill(cr, c)
    px = 210 + pos * 165
    cr.move_to(px, 650); cr.line_to(px - 30, 700); cr.line_to(px + 30, 700); cr.close_path(); fill(cr, (1, 1, 1))
    label(cr, 'cor do xixi', W / 2, 760, 44, (.8, 1, .9), 'i')
    tr = wt('rins')
    if t > tr:
        a = back(prog(t, tr, tr + .35)); cr.save(); cr.translate(W / 2, 1110); cr.scale(a, a)
        card(cr, -420, -200, 840, 400, fillc=hexc('#073B3A'), border=(.6, 1, .8))
        for sg in (-1, 1):
            cr.save(); cr.translate(-230 + sg * 70, 0); cr.scale(sg, 1)
            cr.move_to(0, -110); cr.curve_to(80, -120, 90, 0, 60, 30); cr.curve_to(30, 10, 30, 60, 60, 80); cr.curve_to(70, 130, -20, 130, -20, 60); cr.curve_to(-40, -20, -40, -100, 0, -110)
            fill(cr, hexc('#C4505A')); cr.restore()
        label(cr, 'RINS', 120, -90, 60, (1, 1, 1), 'b')
        label(cr, 'modo', 120, -5, 46, (.8, 1, .9), 's'); label(cr, 'ECONOMIA', 120, 75, 72, C['yellow'], 'b')
        # bateria
        cr.restore()
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Primeiro', 's', 72), ('dia', 'i', 120)]], y=180, t1=wt('xixi', after=t0))
    post(cr, t)

def s6(cr, t):  # cabeça dói
    t0, t1 = wt('cabeça') - .2, b(4)
    bg(cr, t, 'vinho')
    progress_days(cr, t, TL, 1)
    sh = 6 * math.sin(t * 40) if t > t0 + .4 else 0
    cr.save(); cr.translate(sh, 0); cam(cr, t, t0, t1, 1.1, 1.2, dy=-60)
    front_char(cr, W / 2, 1650, 900, expr='sad', arm='nose', jacket=hexc('#2F80ED'), t=t)
    for k in range(3):
        ph = (t * 3 + k / 3) % 1
        x = W / 2 + (k - 1) * 260; y = 700 - 40 * ph
        cr.set_source_rgba(*C['yellow'], 1 - ph * .5); cr.set_line_width(14)
        cr.move_to(x - 20, y - 60); cr.line_to(x + 20, y - 10); cr.line_to(x - 15, y + 5); cr.line_to(x + 25, y + 60); cr.stroke()
    cr.restore()
    title(cr, t, t0 + .3, 999, 'DOR DE CABEÇA', y=300, size=110, col=C['white'])
    post(cr, t)

def s7(cr, t):  # dia 2: sangue grosso + coração
    t0, t1 = b(4), wt('pele') - .2
    bg(cr, t, 'vinho', grid=False)
    progress_days(cr, t, TL, 1 + ease(prog(t, t0, t0 + .8)))
    thick = ease(prog(t, wt('sangue'), wt('grosso') + .5))
    # vaso
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.06)
    rrect(cr, -40, 420, W + 80, 300, 150); fill(cr, hexc('#5A0F22'))
    rrect(cr, -40, 450, W + 80, 240, 120); fill(cr, mix(hexc('#C4243F'), hexc('#6E0A1C'), thick))
    r = random.Random(4)
    spd = 260 * (1 - .7 * thick)
    for k in range(int(14 + 16 * thick)):
        x = (r.uniform(0, W + 200) + t * spd) % (W + 200) - 100; y = r.uniform(490, 650)
        cr.save(); cr.translate(x, y); cr.scale(1, .55); cr.arc(0, 0, 38, 0, 7); cr.restore(); fill(cr, hexc('#FF5A6E'))
    if t > wt('grosso'): chip(cr, t, wt('grosso'), 999, 'MAIS GROSSO', W / 2, 790, col=C['red'], size=50)
    tc = wt('coração')
    if t > tc:
        bt = 1 + .12 * max(0, math.sin(t * 14))
        cr.save(); cr.translate(W / 2 - 200, 1140); cr.scale(bt * 1.6, bt * 1.6)
        cr.move_to(0, 60); cr.curve_to(-140, -40, -70, -140, 0, -60); cr.curve_to(70, -140, 140, -40, 0, 60); fill(cr, hexc('#FF4F7B')); cr.restore()
        bpm = int(72 + 50 * ease(prog(t, tc, tc + 2)))
        label(cr, str(bpm), W / 2 + 220, 1100, 150, (1, 1, 1), 'b'); label(cr, 'bpm', W / 2 + 220, 1210, 56, ACC, 'i')
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Segundo', 's', 72), ('dia', 'i', 120)]], y=180)
    post(cr, t)

def s8(cr, t):  # pele: beliscão
    t0, t1 = wt('pele') - .2, b(5)
    bg(cr, t, 'sepia')
    progress_days(cr, t, TL, 2)
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.1, dy=-40)
    pinch = ease(prog(t, wt('belisca') - .1, wt('belisca') + .4))
    rel = ease(prog(t, wt('belisca') + .6, t1 + 2))
    h = 260 * pinch * (1 - .6 * rel)
    # mão (dorso)
    rrect(cr, 160, 820, 760, 420, 160); fill(cr, C['skin'])
    for k in range(4): rrect(cr, 200 + k * 175, 640, 130, 260, 60); fill(cr, C['skin'])
    rrect(cr, 760, 980, 300, 120, 60); fill(cr, C['skin'])
    # prega de pele
    cr.move_to(420, 1000); cr.curve_to(470, 1000 - h, 610, 1000 - h, 660, 1000); fill(cr, shade(C['skin'], .9))
    if pinch > .1:
        for sg in (-1, 1):
            cr.save(); cr.translate(540 + sg * 80, 980 - h); rrect(cr, -40, -120, 80, 160, 40); fill(cr, shade(C['skin'], 1.05)); cr.restore()
    cr.restore()
    if t > wt('demora'): chip(cr, t, wt('demora'), 999, 'DEMORA PRA VOLTAR', W / 2, 1380, col=C['red'], size=48)
    ktext(cr, t, t0 + .1, [[('A', 's', 72), ('pele', 'i', 130)], [('perde', 's', 72), ('elasticidade', 'b', 80)]], y=180)
    post(cr, t)

def s9(cr, t):  # dia 3: cérebro 3/4 água
    t0, t1 = b(5), b(6)
    bg(cr, t, 'noite')
    progress_days(cr, t, TL, 2 + ease(prog(t, t0, t0 + .8)))
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.08, dy=-20)
    spin = t * 2.0
    cx, cy = W / 2, 880
    if t < wt('cérebro') - .2:
        front_char(cr, cx, 1450, 640, expr='shock', jacket=hexc('#2F80ED'), t=t)
        for k in range(5):
            a = spin + k * 1.256
            circle(cr, cx + math.cos(a) * 200, 700 + math.sin(a) * 50, 18, C['yellow'])
        for k, (nm, w) in enumerate((('TONTURA', 'tontura'), ('CONFUSÃO', 'confusão'), ('ALUCINAÇÃO', 'alucinação'))):
            if t > wt(w): chip(cr, t, wt(w), 999, nm, cx, 500 + k * 130, col=[C['orange'], C['purple'], C['red']][k], size=44)
    else:
        tb = wt('cérebro')
        lvl = .75 * ease(prog(t, wt('quase'), wt('água', after=tb) + .3)) * (1 - .25 * ease(prog(t, wt('sofre') - .1, wt('sofre') + .8)))
        cr.save(); cr.translate(cx, cy); cr.scale(1.6, 1.6)
        brain(cr, 0, 0, 1, hexc('#FF8FB1'))
        cr.restore()
        cr.save(); cr.rectangle(0, cy + 290 - 580 * lvl, W, 2000); cr.clip(); cr.translate(cx, cy); cr.scale(1.6, 1.6); brain(cr, 0, 0, 1, WAT); cr.restore()
        if t > wt('quase'): label(cr, '¾ água', cx, 1310, 100, WAT2, 'i')
        if t > wt('calor'): chip(cr, t, wt('calor'), 999, 'CALOR = MAIS RÁPIDO', cx, 450, col=C['red'], size=46)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('Terceiro', 's', 72), ('dia', 'i', 120)]], y=180, t1=wt('cérebro') - .2)
    post(cr, t)

def s10(cr, t):  # regra dos 3
    t0, t1 = b(6), b(7)
    bg(cr, t, 'azul')
    cr.save(); cam(cr, t, t0, t1, 1.0, 1.05)
    rows = [('3 MINUTOS', 'sem ar', 'minutos', hexc('#7FD3FF')), ('3 DIAS', 'sem água', 'dias', WAT), ('3 SEMANAS', 'sem comida', 'semanas', C['orange'])]
    for k, (a1, a2, w, col) in enumerate(rows):
        tk = min(wt(w, after=t0), t0 + .5 + k * .35)
        if t < tk: continue
        a = back(prog(t, tk, tk + .3)); y = 560 + k * 290
        cr.save(); cr.translate(W / 2, y); cr.scale(a, a)
        card(cr, -430, -120, 860, 240, fillc=hexc('#10204A'), border=(1, 1, 1) if k == 1 else None)
        circle(cr, -320, 0, 80, col); label(cr, '3', -320, 0, 110, (1, 1, 1), 'b')
        label(cr, a1, 70, -40, 70, (1, 1, 1), 'b'); label(cr, a2, 70, 45, 56, col, 'i')
        cr.restore()
    if t > wt('bolso'): chip(cr, t, wt('bolso'), 999, 'REGRA DE BOLSO', W / 2, 1420, col=C['purple'], size=46)
    cr.restore()
    ktext(cr, t, t0 + .1, [[('A', 's', 72), ('regra', 'b', 100), ('dos', 's', 72), ('três', 'i', 130)]], y=170)
    post(cr, t)

def s11(cr, t):  # CTA café
    t0 = b(7)
    bg(cr, t, 'sepia')
    cr.save(); cr.translate(W / 2, 1340); s = back(prog(t, t0, t0 + .4))
    cr.scale(s, s)
    rrect(cr, -170, -160, 340, 320, 40); fill(cr, (1, 1, 1))
    cr.set_source_rgb(1, 1, 1); cr.set_line_width(34); cr.arc(190, 0, 80, -1.3, 1.3); cr.stroke()
    rrect(cr, -150, -150, 300, 50, 20); fill(cr, hexc('#6B3A1E'))
    for k in range(3):
        ph = (t * .7 + k / 3) % 1
        cr.set_source_rgba(1, 1, 1, .7 * (1 - ph)); cr.set_line_width(12)
        x = -80 + k * 80; cr.move_to(x, -190 - ph * 120); cr.curve_to(x + 30, -230 - ph * 120, x - 30, -270 - ph * 120, x, -310 - ph * 120); cr.stroke()
    cr.restore()
    cta(cr, t, t0 + .3, 'Manda pro amigo', 'que vive no café')
    post(cr, t)

SCENES = [(0, .4, s0), (.4, wt('próximo'), s1), (wt('próximo'), b(1), s2), (b(1), b(2), s3), (b(2), b(3), s4),
          (b(3), wt('cabeça') - .2, s5), (wt('cabeça') - .2, b(4), s6), (b(4), wt('pele') - .2, s7), (wt('pele') - .2, b(5), s8),
          (b(5), b(6), s9), (b(6), b(7), s10), (b(7), 999, s11)]
render = make_render(SCENES, WORDS, DUR)
