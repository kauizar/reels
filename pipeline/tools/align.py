import re, json
"""Alinha palavras do roteiro com a narração (sem transcrição): usa pausas (silencedetect) + sílabas.
uso: python3 align.py <pasta_video>   (precisa de narr.mp3 e text.py na pasta) -> words.json + mostra blocos"""
import sys, os, subprocess
D = os.path.abspath(sys.argv[1]); os.chdir(D); sys.path.insert(0, D)
from text import BLOCKS
DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'narr.mp3']).decode())
out = subprocess.run(['ffmpeg', '-hide_banner', '-i', 'narr.mp3', '-af', 'silencedetect=noise=-35dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
import re as _re
st = [float(x) for x in _re.findall(r'silence_start: ([0-9.]+)', out)]; en = [float(x) for x in _re.findall(r'silence_end: ([0-9.]+)', out)]
sil = list(zip(st, en))
# speech chunks
chunks = []; t = 0.0
for s, e in sil:
    if s - t > 0.05: chunks.append((t, s))
    t = e
if DUR - t > 0.05: chunks.append((t, DUR))

words = []  # (text, key, block, punct_strength, syl)
for bi, b in enumerate(BLOCKS):
    for tok in b.split():
        key = tok.startswith('**')
        clean = tok.replace('**', '')
        p = 0
        if re.search(r'(\.\.\.|[.?!:])$', clean): p = 3
        elif clean.endswith(','): p = 2
        syl = max(1, len(re.findall(r'[aeiouyáéíóúâêôãõà]+', clean.lower())))
        words.append(dict(w=clean, key=key, block=bi, p=p, syl=syl))
    words[-1]['p'] = 4

N, K = len(words), len(chunks)
cum = [0]
for w in words: cum.append(cum[-1] + w['syl'])
speech = sum(e - s for s, e in chunks)
rate = cum[-1] / speech
INF = 1e18
# dp[k][i] = min cost assigning first i words to first k chunks
dp = [[INF] * (N + 1) for _ in range(K + 1)]
bk = [[-1] * (N + 1) for _ in range(K + 1)]
dp[0][0] = 0
pen = {0: 6.0, 1: 3, 2: 1.0, 3: 0.0, 4: 0.0}
for k in range(1, K + 1):
    s, e = chunks[k - 1]; exp = rate * (e - s)
    for i in range(1, N + 1):
        best, arg = INF, -1
        bend = 0.0 if k == K else pen[words[i - 1]['p']]
        for j in range(max(0, i - 40), i):
            if dp[k - 1][j] >= INF: continue
            sy = cum[i] - cum[j]
            c = dp[k - 1][j] + (sy - exp) ** 2 / (exp + 2) + bend
            if c < best: best, arg = c, j
        dp[k][i], bk[k][i] = best, arg
# backtrack
i = N; groups = []
for k in range(K, 0, -1):
    j = bk[k][i]; groups.append((j, i, chunks[k - 1])); i = j
groups.reverse()
for j, i, (s, e) in groups:
    tot = cum[i] - cum[j]; t = s
    for w in words[j:i]:
        d = (e - s) * w['syl'] / tot
        w['t0'], w['t1'] = round(t, 3), round(t + d, 3); t += d
json.dump(words, open('words.json', 'w'), ensure_ascii=False, indent=0)
for bi in range(len(BLOCKS)):
    ws = [w for w in words if w['block'] == bi]
    print(bi + 1, ws[0]['t0'], ws[-1]['t1'], ' '.join(w['w'] for w in ws)[:60])
print('DUR', DUR)
