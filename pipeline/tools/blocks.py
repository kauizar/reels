"""Gera text.py (BLOCKS) a partir do roteiro.
uso: python3 blocks.py <pasta_video> roteiro.txt "palavra1,palavra2,..."
Parágrafos separados por linha em branco viram blocos; palavras-chave (exatamente como no texto, com pontuação) ficam destacadas na legenda."""
import sys, json
d, src, keys = sys.argv[1], sys.argv[2], set(k.strip() for k in sys.argv[3].split(',') if k.strip())
s = open(src, encoding='utf-8').read().strip()
blocks = [' '.join(('**' + w if w in keys else w) for w in p.split()) for p in s.split('\n\n') if p.strip()]
open(f'{d}/text.py', 'w', encoding='utf-8').write('BLOCKS = ' + json.dumps(blocks, ensure_ascii=False) + '\n')
print(len(blocks), 'blocos')
