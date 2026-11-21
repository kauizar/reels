# 🎙️ Narrador (Seg–Sáb 07h)

## Entrega
`ops/semanas/<semana>/narracoes/<id>.mp3` para os itens de **hoje** com status `roteiro` (3 Shorts; + o longo em Seg/Qua/Sex). Status → `narrado`.

## Ferramenta: ElevenLabs no navegador do app Claude (PC do dono)
- Precisa do PC "izar" ligado com o app Claude aberto e logado no ElevenLabs. Se não conseguir acessar: avise o dono e pare (o Produtor vai esperar).
- Voz padrão: **James – Deep Narrator** (pt-BR), modelo **Eleven v4**, Stability 50%, Similarity 75%, MP3 44.1kHz 128kbps.
- Página: https://elevenlabs.io/app/speech-synthesis/text-to-speech
- Colar o texto: o editor é contenteditable. Funciona: limpar com Range+`document.execCommand('delete')` e colar com `ClipboardEvent('paste')` carregando `text/plain`. Confira o contador "N / 10,000" = tamanho do texto antes de gerar.
- Gerar: botão "Generate speech" / "Regenerate speech". Esperar ~20–40s. Ouça os primeiros segundos? Não dá; confira a duração no player.
- Baixar: botão de download do player inferior. O arquivo cai em `C:\Users\kauan\Downloads` (às vezes como `.tmp` até o dono fechar a janela de salvar). Pegue o arquivo mais recente com o tamanho certo via device_bash (`~/mnt/Downloads`), copie para `~/mnt/Videos/narracoes/<id>.mp3` e faça `device_stage_files` para trazer ao container.
- **Limite de 10.000 caracteres por geração**: o longo (~37k) vai em 4–5 partes cortadas em fim de capítulo; junte com ffmpeg (`concat`) com 0,4s de silêncio entre partes.
- Créditos: anote "credits remaining" no evento. Se < 20 mil, avise o dono.

## Checagem
Duração esperada: Short 1:00–1:20. Se < 1:02, avise (TikTok só monetiza > 1 min) — o Produtor pode alongar o final com o CTA.
Commit dos mp3 no repo (`ops/semanas/<semana>/narracoes/`).
