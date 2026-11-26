# 📤 Publicador (todo dia 12h e 19h)

## Passos
1. Início comum (`_comum.md`). Pegue o item de **hoje** cujo horário `ig` é o desta execução (12:00 → slot 1, 19:00 → slot 2).
2. Confira que o arquivo existe: `curl -sI https://raw.githubusercontent.com/kauizar/reels/main/<arquivo>.mp4` → 200.
   - Se não existir (Produtor atrasou): avise o dono, registre `erro`, e tente de novo em 30 min uma única vez (agende um lembrete para esta mesma sessão com send_later, se disponível).
3. Publique no Instagram: `mcp__Windsor_ai__execute_action` connector `instagram`, action `create_video_post`, account `17841407394822011`, params `{video_url, caption: legenda_ig, share_to_feed: true}`. (Esse item já foi aprovado no plano da semana.)
4. Status → `publicado_ig` (guarde o media id). Evento no painel.
5. Confira no YouTube (se o navegador estiver disponível) que o Short do slot continua "Programado"; se não, avise.
6. Mensagem curta ao dono: "✅ <tema> no Instagram (<hora>). Próximo: ...".
