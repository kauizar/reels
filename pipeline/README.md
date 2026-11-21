# Pipeline de animação — "O que aconteceria se..."

```bash
bash pipeline/tools/setup.sh            # pycairo, numpy, fontes, ffmpeg
export PYTHONPATH=$PWD/pipeline/lib
D=~/work/meu-video; mkdir -p $D && cp narr.mp3 $D/
python3 pipeline/tools/blocks.py $D roteiro.txt "palavra1,palavra2"   # text.py
python3 pipeline/tools/align.py  $D                                    # words.json
# escreva $D/scenes_x.py (modelo: pipeline/examples/v14/scenes14.py)
python3 pipeline/tools/still.py  $D scenes_x 2 10 20 40               # contato.png
python3 pipeline/tools/render.py $D scenes_x 2                         # sc_*.mp4
bash    pipeline/tools/assemble.sh $D saida.mp4                        # vídeo final
```
- `lib/` motor (engine, real) + módulos de cenas antigos com helpers reaproveitáveis.
- `examples/v9..v16` vídeos prontos (sono, gravidade, oceanos, buraco negro, insetos, oxigênio, espaço, lua).
- Saída: 1080×1920, 30 fps, H.264 crf 24, AAC, faststart.
