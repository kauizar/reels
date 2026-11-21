"""Frames de teste. uso: python3 still.py <pasta> <modulo> t1 t2 ...  -> f_<t>.png e contato.png"""
import sys, os, subprocess, importlib, cairo
D = os.path.abspath(sys.argv[1]); sys.path.insert(0, D); m = importlib.import_module(sys.argv[2])
fs = []
for a in sys.argv[3:]:
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, m.W, m.H); m.render(float(a), s); p = f'{D}/f_{a}.png'; s.write_to_png(p); fs.append(p)
subprocess.call(['montage'] + fs + ['-geometry', '200x356+3+3', '-tile', '8x', f'{D}/contato.png'])
print(f'{D}/contato.png')
