# 🎬 Produtor (todo dia 08h, depois do Narrador)

## Entrega por Short do dia
1. Vídeo final vertical 1080×1920 `<arquivo>.mp4` na raiz do repo (push) → URL `https://raw.githubusercontent.com/kauizar/reels/main/<arquivo>.mp4`.
2. **Capa própria** (frame de capa 1080×1920 com a frase `capa` grande + ilustração do tema) usada como primeiro 0,4s do vídeo e enviada como thumbnail quando a plataforma permitir.
3. Short agendado no **YouTube Studio** no horário `yt` (título, descrição com quebras de linha, "não é conteúdo para crianças", Programar).
4. Status → `renderizado` → `agendado_yt`. Mensagem ao dono com as **2 legendas TikTok do dia + horários** (ele agenda manualmente; arquivos em `C:\Users\kauan\Downloads\VIDEOS TIKTOK (pasta pronta para o dono postar no TikTok; crie se não existir)` — copie para lá via device_bash/curl do raw).

## Como animar (motor do canal)
```bash
cd ~/reels/pipeline && eval "$(bash tools/setup.sh | grep export)"
mkdir -p ~/work/<id> && cp ~/reels/ops/semanas/<semana>/narracoes/<id>.mp3 ~/work/<id>/narr.mp3
python3 tools/blocks.py ~/work/<id> ~/reels/ops/semanas/<semana>/roteiros/<id>.txt "<palavras_chave,separadas>"
python3 tools/align.py ~/work/<id>          # -> words.json e tempos de cada bloco
# escreva ~/work/<id>/scenes_<id>.py (veja examples/v9..v16: SCENES, overlays, render, W,H,FPS, END = DUR + 1.5)
python3 tools/still.py ~/work/<id> scenes_<id> 2 10 20 ...   # olhe contato.png antes de renderizar!
python3 tools/render.py ~/work/<id> scenes_<id> 2
bash tools/assemble.sh ~/work/<id> ~/reels/<arquivo>.mp4
```
- Biblioteca em `pipeline/lib` (engine: Iso/IsoR, person, front_char, house, building, tree, car, caption, title, pill, counter, keys/prog/ease/back; real: draw_globe, space, render_rock; scenes*: helpers como heart, stars, clouds, thermo, capsule, cut_earth, moon_disk, astro). Exemplos completos em `pipeline/examples/`.
- Regras visuais: 8–11 cenas por Short, câmera sempre em movimento, nada parado > 3s, título/pill/counter nas palavras-chave, legenda palavra a palavra (caption), CTA final grande. Varie paletas e cenários entre vídeos.
- Olhe os stills (contato.png) e corrija sobreposição de texto/legenda, elementos cortados e cenas vazias ANTES do render completo. Depois do encode, extraia 4 frames do final e confira.
- Memória: globos grandes (`draw_globe` com R > 900) matam o processo — mantenha R ≤ 900.

## YouTube Studio (navegador do app Claude)
- Upload: em studio.youtube.com, abrir "Criar → Enviar vídeos", achar `ytcp-uploads-file-picker input[type=file]`, `fetch` do raw do GitHub → `DataTransfer` → `change`.
- Título: `#textbox` [0] com innerText + `input`. **Descrição: colar via ClipboardEvent('paste') com text/plain** (innerText perde as quebras de linha).
- Rádio `VIDEO_MADE_FOR_KIDS_NOT_MFK`, `#next-button` até a etapa Visibilidade, `#second-container-expand-button` (Programar).
- Data: clicar `ytcp-datetime-picker #datepicker-trigger`, focar o input visível que contém o ano, selecionar tudo e **digitar** ("23 de nov. de 2026") + Enter. Hora: focar `ytcp-datetime-picker input`, selecionar, digitar "14:00" + Enter. Conferir e clicar `#done-button`; fechar o diálogo "Vídeo programado"/"Processando vídeo".
- Ao fim, recarregue a lista de Shorts e confira "Programado <data>" para os 3.

- Referência visual dos Shorts: `ops/referencias/estilo-shorts.mp4` (veja alguns frames antes de animar).

## Aviso ao dono (pedido 23/11)
Assim que os 3 mp4 do dia estiverem em `Downloads\VIDEOS TIKTOK` (sincroniza sozinho com o Google Drive do dono), mande UMA mensagem curta:
"🎬 2 vídeos do TikTok soltos na pasta VIDEOS TIKTOK" + para cada um: horário TikTok · nome do arquivo · legenda TikTok pronta para copiar. Nada além disso.
