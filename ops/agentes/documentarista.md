# 🎞️ Documentarista — vídeo longo (Seg, Qua, Sex 09h30)

## Entrega
Vídeo horizontal **1920×1080, ~42 min**, com capítulos, agendado no YouTube às **20h30** do mesmo dia, com thumbnail própria.

**Frequência: 1 por mês (1ª quarta-feira).** A tarefa roda toda quarta: se o plano da semana não tiver item `longo` com a data de hoje, marque `agents/documentarista` como ocioso (tarefa: "Próximo longo: 1ª quarta do mês") e encerre sem mensagem.

## Formato (documentário "do zero")
Pipeline próprio em `pipeline/longo/` (criado no piloto). Cenas reaproveitáveis e baratas de renderizar:
mapa animado (países/fronteiras/setas de avanço), linha do tempo, cartão de capítulo, texto cinético com palavras-chave,
personagens/ilustrações low-poly do motor do canal, gráficos (números, comparações), citações parafraseadas.
- 24 fps, troca de cena a cada 6–12 s, cartão de capítulo a cada 4–6 min.
- Render em paralelo por capítulo (`tools/render.py` com jobs = núcleos). Encode final crf 22, áudio aac 160k.
- Thumbnail 1280×720: título curto (≤ 4 palavras) + imagem forte + contraste alto.
- Descrição: resumo com palavras-chave + capítulos `00:00 Título` (tempos reais) + CTA.

## Primeira execução (piloto)
Se `pipeline/longo/` ainda não existir: construa o formato (cenas de mapa, linha do tempo, cartão de capítulo, texto cinético) reaproveitando `pipeline/lib`, renderize os 3 primeiros minutos, mande ao dono para aprovar e só então produza o vídeo inteiro. Nesse dia publique no horário que der (avise o dono) — melhor atrasar do que publicar algo feio.

## Passos
1. Narração (feita pelo Narrador, em partes) → `narr.mp3` juntado.
2. Alinhamento por capítulo (`tools/align.py` funciona por parágrafos; rode por capítulo para não estourar).
3. Stills por capítulo → render → assemble → conferir 8 frames espalhados.
4. Upload no YouTube Studio (mesmo método do Produtor, mas **sem** #shorts; adicionar thumbnail), Programar 20:30.
5. Status `agendado_yt`, painel, aviso ao dono com o link.
Se o tempo de render ameaçar o horário, publique às 21h30 e avise.
