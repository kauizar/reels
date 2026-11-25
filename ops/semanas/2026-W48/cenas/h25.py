"""helpers compartilhados dos Shorts de 25/11 (tempos derivados de words.json)."""
import math, random, subprocess, os
import cairo
from engine import *
from real import post
from md import *

class Timing:
    def __init__(self, D):
        self.W = load_words(D); self.wt_ = make_wt(self.W)
        try:
            self.DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(D, 'narr.mp3')]).decode())
        except Exception:
            self.DUR = self.W[-1]['t1'] + .3
    def b(self, i):  # início do bloco i
        return next(w['t0'] for w in self.W if w['block'] == i)
    def be(self, i):  # fim do bloco i
        return [w['t1'] for w in self.W if w['block'] == i][-1]
    def wt(self, word, n=1, after=0.0, d=0.0):
        try: return self.wt_(word, n, after) + d
        except KeyError: return after + 1.0

def cover(cr, t, pal, l1, l2, draw=None):
    """capa 1080x1920: frase grande + ilustração."""
    bg(cr, 0, pal)
    if draw: draw(cr)
    font(cr, 'b', 10)
    rrect(cr, 60, 180, W - 120, 470, 50); fill(cr, (0, 0, 0), .35)
    label(cr, l1, W / 2, 330, fit_s(cr, l1, 150, 900), (1, 1, 1), 'b')
    label(cr, l2, W / 2, 510, fit_s(cr, l2, 170, 920, 'i'), ACC, 'i')
    post(cr, 0, vignette=.5)

def make_render(SCENES, WORDS, DUR, cut=.15):
    def render(t, surf):
        cr = ctx_for(surf)
        for a, b, fn in SCENES:
            if a <= t < b:
                cr.save(); fn(cr, t); cr.restore(); break
        for a, b, fn in SCENES[1:]:
            flash_cut(cr, t, a, cut)
        if .4 <= t < DUR + .3:
            cr.save(); cr.translate(0, 230); caption(cr, t, WORDS); cr.restore()
    return render

def brain(cr, x, y, s, col=None, glow=0.0, t=0.0):
    col = col or hexc('#FF8FB1')
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if glow:
        rg = cairo.RadialGradient(0, 0, 50, 0, 0, 320); rg.add_color_stop_rgba(0, *col, .5 * glow); rg.add_color_stop_rgba(1, *col, 0); cr.set_source(rg); cr.paint()
    for (bx, by, r) in [(-90, -40, 95), (0, -80, 100), (90, -40, 95), (-60, 40, 90), (60, 40, 90), (0, 10, 100)]:
        circle(cr, bx, by, r, col)
    cr.set_source_rgba(*shade(col, .7), 1); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(0, -170); cr.curve_to(-20, -100, 20, -40, 0, 120); cr.stroke()
    for k in range(6):
        a = k * 1.1 + .4
        cr.move_to(math.cos(a) * 60, math.sin(a) * 50 - 10); cr.curve_to(math.cos(a) * 100, math.sin(a) * 80, math.cos(a + .5) * 120, math.sin(a + .4) * 90, math.cos(a + .7) * 150, math.sin(a + .6) * 100)
        cr.stroke()
    cr.restore()

def bubble(cr, x, y, w, h, txt, a=1.0, size=44, col=None, tail=1):
    """balão de pensamento."""
    col = col or (1, 1, 1)
    rrect(cr, x - w / 2, y - h / 2, w, h, h / 2); fill(cr, col, a)
    for k, r in enumerate((18, 11)):
        circle(cr, x + tail * (w * .25 + k * 22), y + h / 2 + 22 + k * 30, r, col, a)
    font(cr, 'b', fit_s(cr, txt, size, w - 50)); e = cr.text_extents(txt)
    cr.move_to(x - e.x_advance / 2, y + e.height / 2 - 4); cr.text_path(txt); fill(cr, hexc('#1B2C5E'), a); reset_font(cr)
