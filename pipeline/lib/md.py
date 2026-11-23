"""Estilo 'motion design' azul (referência estilo-shorts.mp4): fundo gradiente com brilho e grade,
tipografia cinética mista (Montserrat Black + Gelasio itálico), cards de vidro, celular, câmera em movimento."""
import math, random, json, os
import cairo
from engine import *

SANS, SERIF = "Montserrat", "Gelasio"

def load_words(d):
    return json.load(open(os.path.join(d, 'words.json')))

def make_wt(WORDS):
    def wt(word, n=1, after=0.0):
        k = 0
        for w in WORDS:
            if w['t0'] >= after and w['w'].strip('.,:;?!"').lower().startswith(word.lower()):
                k += 1
                if k == n: return w['t0']
        raise KeyError(word)
    return wt

PAL = {
    'azul':   ('#0A2A72', '#061540', '#3E7BFF'),
    'noite':  ('#141046', '#05061A', '#7A5CFF'),
    'verde':  ('#073B3A', '#03181C', '#2FD38A'),
    'sepia':  ('#3A2412', '#140A04', '#FFB14A'),
    'vinho':  ('#3E0B22', '#14030B', '#FF4F7B'),
    'gelo':   ('#123A5E', '#071726', '#7FD3FF'),
}

def bg(cr, t, pal='azul', grid=True, glow=(0.7, 0.25)):
    a, b, g_ = (hexc(x) for x in PAL[pal])
    g = cairo.LinearGradient(0, 0, W * .3, H); g.add_color_stop_rgb(0, *a); g.add_color_stop_rgb(1, *b)
    cr.set_source(g); cr.paint()
    gx = W * (glow[0] + .08 * math.sin(t * .4)); gy = H * (glow[1] + .05 * math.cos(t * .33))
    rg = cairo.RadialGradient(gx, gy, 0, gx, gy, 900); rg.add_color_stop_rgba(0, *g_, .28); rg.add_color_stop_rgba(1, *g_, 0)
    cr.set_source(rg); cr.paint()
    if grid:
        cr.set_source_rgba(1, 1, 1, .045); cr.set_line_width(2)
        off = (t * 18) % 90
        for x in range(-90, W + 90, 90): cr.move_to(x + off, 0); cr.line_to(x + off, H)
        for y in range(-90, H + 90, 90): cr.move_to(0, y + off); cr.line_to(W, y + off)
        cr.stroke()
    # partículas
    r = random.Random(7)
    for k in range(40):
        x = (r.uniform(0, W) + t * r.uniform(-12, 12)) % W; y = (r.uniform(0, H) - t * r.uniform(8, 30)) % H
        circle(cr, x, y, r.uniform(1.5, 4), (1, 1, 1), r.uniform(.08, .3))

def cam(cr, t, t0, t1, z0=1.0, z1=1.12, dx=0, dy=0, cx=W / 2, cy=H / 2):
    """push-in contínuo da câmera (chame antes de desenhar a cena, com cr.save/restore)."""
    p = clamp((t - t0) / max(.01, t1 - t0))
    z = z0 + (z1 - z0) * p
    cr.translate(cx + dx * p, cy + dy * p); cr.scale(z, z); cr.translate(-cx, -cy)

def font(cr, kind, size):
    if kind == 'i': cr.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    elif kind == 's': cr.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    elif kind == 'L': cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    else: cr.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(size)

def reset_font(cr):
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

ACC = hexc('#FF8A3D')

def ktext(cr, t, t0, lines, x=90, y=300, t1=None, stagger=.09, align='left', accent=None):
    """lines: lista de linhas; cada linha = lista de (texto, estilo, tamanho). estilo: b (branco forte), i (itálico destaque),
    s (pequeno), y (forte amarelo), o (forte laranja). Palavras entram uma a uma (sobe + fade)."""
    if t < t0: return
    if t1 is not None and t >= t1: return
    fade = 1.0 if t1 is None else clamp((t1 - t) / .25)
    acc = accent or ACC
    k = 0; yy = y
    for line in lines:
        hmax = max(s for _, _, s in line)
        yy += hmax * .78
        # largura para centralizar
        tw = 0
        for txt, st, sz in line:
            font(cr, 'i' if st == 'i' else ('s' if st == 's' else 'b'), sz); tw += cr.text_extents(txt + ' ').x_advance
        xx = x if align == 'left' else (W - tw) / 2
        for txt, st, sz in line:
            p = eout((t - t0 - k * stagger) / .35); k += 1
            font(cr, 'i' if st == 'i' else ('s' if st == 's' else 'b'), sz)
            adv = cr.text_extents(txt + ' ').x_advance
            if p > 0:
                col = {'i': acc, 'y': C['yellow'], 'o': acc, 's': (.78, .84, 1.0)}.get(st, (1, 1, 1))
                cr.save(); cr.translate(xx, yy + (1 - p) * 40)
                cr.move_to(4, 6); cr.text_path(txt); cr.set_source_rgba(0, 0, 0, .35 * p * fade); cr.fill()
                cr.move_to(0, 0); cr.text_path(txt); cr.set_source_rgba(*col, p * fade); cr.fill()
                cr.restore()
            xx += adv
        yy += hmax * .32
    reset_font(cr)

def card(cr, x, y, w, h, a=1.0, r=34, fillc=None, border=None):
    rrect(cr, x + 10, y + 18, w, h, r); fill(cr, (0, 0, 0), .35 * a)
    rrect(cr, x, y, w, h, r)
    g = cairo.LinearGradient(x, y, x, y + h)
    fc = fillc or hexc('#1B2C5E')
    g.add_color_stop_rgba(0, *shade(fc, 1.25), .92 * a); g.add_color_stop_rgba(1, *fc, .92 * a)
    cr.set_source(g); cr.fill_preserve()
    cr.set_source_rgba(*(border or (.6, .75, 1)), .5 * a); cr.set_line_width(3); cr.stroke()

def phone(cr, x, y, s, content, t, a=1.0):
    """celular centrado em (x,y), altura 900*s; content(cr, w, h, m) desenha a tela em coordenadas de escala 1 (440x900)."""
    w, h = 440, 900
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.translate(-w / 2, -h / 2)
    rrect(cr, 14, 24, w, h, 60); fill(cr, (0, 0, 0), .4 * a)
    rrect(cr, 0, 0, w, h, 60); fill(cr, hexc('#0E0F14'), a)
    m = 18
    cr.save(); rrect(cr, m, m, w - 2 * m, h - 2 * m, 46); cr.clip()
    content(cr, w - 2 * m, h - 2 * m, m)
    cr.restore()
    rrect(cr, w / 2 - 60, m + 14, 120, 30, 15); fill(cr, hexc('#0E0F14'), a)
    cr.restore()

def label(cr, txt, x, y, size, col=None, kind='b', alpha=1.0, align='c'):
    font(cr, kind, size)
    e = cr.text_extents(txt)
    xx = x - e.x_advance / 2 if align == 'c' else x
    cr.move_to(xx, y + size * .35); cr.text_path(txt); cr.set_source_rgba(*(col or (1, 1, 1)), alpha); cr.fill()
    reset_font(cr)
    return e.x_advance

def chip(cr, t, t0, t1, txt, x, y, col=None, size=40):
    if not (t0 <= t < t1): return
    a = min(1, (t1 - t) / .15); sc = back((t - t0) / .28)
    col = col or ACC
    font(cr, 'b', size); tw = cr.text_extents(txt).x_advance
    cr.save(); cr.translate(x, y); cr.scale(sc, sc)
    w, h = tw + size * 1.2, size * 1.6
    rrect(cr, -w / 2, -h / 2, w, h, 12); fill(cr, col, a)
    cr.move_to(-tw / 2, size * .36); cr.text_path(txt); fill(cr, (1, 1, 1), a)
    cr.restore(); reset_font(cr)

def stamp(cr, t, t0, txt, x, y, col=None, size=80, rot=-.12):
    if t < t0: return
    sc = 1 + 1.2 * (1 - eout((t - t0) / .25))
    a = clamp((t - t0) / .12)
    col = col or C['red']
    font(cr, 'b', size); tw = cr.text_extents(txt).x_advance
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(sc, sc)
    rrect(cr, -tw / 2 - 30, -size * .8, tw + 60, size * 1.5, 16)
    cr.set_source_rgba(*col, a); cr.set_line_width(10); cr.stroke()
    cr.move_to(-tw / 2, size * .36); cr.text_path(txt); fill(cr, col, a)
    cr.restore(); reset_font(cr)

def cta(cr, t, t0, l1, l2, col=None):
    """CTA final grande."""
    if t < t0: return
    p = back((t - t0) / .35)
    cr.save(); cr.translate(W / 2, 760); cr.scale(p, p); cr.translate(-W / 2, -760)
    card(cr, 90, 560, W - 180, 420, r=48, fillc=hexc('#10204A'))
    font(cr, 'b', fit_s(cr, l1, 92, 820)); e = cr.text_extents(l1)
    cr.move_to(W / 2 - e.x_advance / 2, 720); cr.text_path(l1); fill(cr, (1, 1, 1))
    font(cr, 'i', fit_s(cr, l2, 110, 820, 'i')); e = cr.text_extents(l2)
    cr.move_to(W / 2 - e.x_advance / 2, 880); cr.text_path(l2); fill(cr, col or ACC)
    cr.restore(); reset_font(cr)

def fit_s(cr, txt, size, maxw, kind='b'):
    font(cr, kind, size); w = cr.text_extents(txt).x_advance
    return size if w <= maxw else size * maxw / w

def flash_cut(cr, t, t0, d=.18):
    if t0 <= t < t0 + d:
        cr.set_source_rgba(1, 1, 1, .55 * (1 - (t - t0) / d)); cr.paint()

def wipe_in(cr, t, t0, d=.35):
    """cortina diagonal saindo (transição de entrada da cena)."""
    if t0 <= t < t0 + d:
        p = eout((t - t0) / d)
        cr.save(); cr.move_to(W * p * 1.6 - 400, 0); cr.line_to(W * 2, 0); cr.line_to(W * 2, H); cr.line_to(W * p * 1.6 - 900, H); cr.close_path()
        fill(cr, hexc('#0A1A44')); cr.restore()

def progress_days(cr, t, labels, idx, y=110, col=None):
    """barra de linha do tempo no topo (Primeiro minuto/hora/dia/...)."""
    n = len(labels); x0, x1 = 110, W - 110
    cr.set_source_rgba(1, 1, 1, .25); cr.set_line_width(6); cr.move_to(x0, y); cr.line_to(x1, y); cr.stroke()
    px = x0 + (x1 - x0) * idx / (n - 1)
    cr.set_source_rgba(*(col or ACC), 1); cr.move_to(x0, y); cr.line_to(px, y); cr.stroke()
    for i, l in enumerate(labels):
        x = x0 + (x1 - x0) * i / (n - 1)
        on = i <= idx + 1e-6
        circle(cr, x, y, 16 if on else 11, col or ACC if on else (1, 1, 1), 1 if on else .5)
        label(cr, l, x, y + 48, 28, (1, 1, 1), 's', .95 if abs(i - idx) < .5 else .55)
