"""Renderiza cenas de um vídeo em paralelo.
uso: python3 render.py <pasta_video> <modulo_cenas> [jobs]   ex: python3 render.py work/v17 scenes17 2
O módulo precisa expor render(t, surf), SCENES=[(t0,t1,fn)], END, W, H, FPS."""
import sys, os, subprocess, importlib
D = os.path.abspath(sys.argv[1]); mod = sys.argv[2]; jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 2
sys.path.insert(0, D)
if len(sys.argv) > 4 and sys.argv[4] == '--scene':
    import cairo
    m = importlib.import_module(mod)
    for i in [int(x) for x in sys.argv[5:]]:
        a, b, _ = m.SCENES[i]; b = min(b, m.END); f0, f1 = round(a * m.FPS), round(b * m.FPS)
        out = f'{D}/sc_{i:02d}.mp4'; tmp = out.replace('.mp4', '.tmp.mp4')
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{m.W}x{m.H}', '-r', str(m.FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', str(m.FPS), tmp], stdin=subprocess.PIPE)
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, m.W, m.H)
        for f in range(f0, f1):
            m.render(f / m.FPS, s); s.flush(); p.stdin.write(bytes(s.get_data()))
        p.stdin.close()
        if p.wait() == 0: os.rename(tmp, out); print('done', i, flush=True)
    sys.exit()
m = importlib.import_module(mod); n = len(m.SCENES)
groups = [list(range(k, n, jobs)) for k in range(jobs)]
procs = [subprocess.Popen([sys.executable, __file__, D, mod, '1', '--scene'] + [str(i) for i in g]) for g in groups if g]
codes = [p.wait() for p in procs]
missing = [i for i in range(n) if not os.path.exists(f'{D}/sc_{i:02d}.mp4')]
if missing:  # retry sequentially (ex.: processo morto por memória)
    subprocess.call([sys.executable, __file__, D, mod, '1', '--scene'] + [str(i) for i in missing])
missing = [i for i in range(n) if not os.path.exists(f'{D}/sc_{i:02d}.mp4')]
print('FALTANDO', missing) if missing else print('todas as cenas ok')
