"""words.json falso (só para testar stills antes da narração). uso: fake_words.py <pasta> [dur]"""
import sys, os, re, json
D = sys.argv[1]; sys.path.insert(0, D); from text import BLOCKS
words = []
for bi, b in enumerate(BLOCKS):
    for tok in b.split():
        c = tok.replace('**', ''); syl = max(1, len(re.findall(r'[aeiouyáéíóúâêôãõà]+', c.lower())))
        words.append(dict(w=c, key=tok.startswith('**'), block=bi, syl=syl, p=3 if re.search(r'[.?!:]$', c) else 0))
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 66
pause = sum(.35 for w in words if w['p']) + .5 * len(BLOCKS)
rate = sum(w['syl'] for w in words) / (dur - pause); t = .1
for w in words:
    d = w['syl'] / rate; w['t0'], w['t1'] = round(t, 3), round(t + d, 3); t += d + (.35 if w['p'] else 0)
    if w is words[-1] or words[words.index(w) + 1]['block'] != w['block']: t += .5
json.dump(words, open(f'{D}/words.json', 'w'), ensure_ascii=False)
print('fake dur', t)
