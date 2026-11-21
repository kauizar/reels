# 📊 Analista — Relatórios e checkup (Domingo 09h)

## Objetivo
Medir a semana que passou e dizer ao Roteirista o que fazer mais/menos.

## Passos
1. `ops/agentes/_comum.md` (início de sessão). Marque `agents/analista` como trabalhando.
2. Métricas via Windsor.ai (`get_fields` antes de `get_data`):
   - YouTube (`youtube`): por vídeo dos últimos 7 e 28 dias — views, likes, comments, shares, average_view_percentage, estimated_minutes_watched, subscribers_gained.
   - Instagram (`instagram`): por mídia — reach/plays, likes, comments, saves, shares (descubra os campos com get_fields).
   - TikTok: se o conector `tiktok_organic` estiver conectado, idem; se não, anote "sem dados".
3. Calcule: top 5 e piores 5 vídeos (por views e por retenção), média por formato (curto ~1:10 vs longo), melhor horário, temas que mais seguraram retenção, progresso de monetização:
   - YouTube: inscritos (meta 1.000), horas de exibição 12m (meta 4.000; atenção: a partir de 01/02/2027 a meta sobe para 8.000h / 20M views de Shorts para novos canais), views de Shorts 90d.
   - TikTok Creator Rewards: 10k seguidores + 100k views/30d.
4. Checkup: (a) todos os itens da semana passada chegaram a `publicado_ig`/`agendado_yt`? liste falhas; (b) agendamentos da próxima semana existem? (c) créditos ElevenLabs (se o navegador estiver disponível, leia "credits remaining" em elevenlabs.io/app/speech-synthesis/text-to-speech); (d) espaço do repo.
5. Escreva `ops/relatorios/<data>.md` (resumo em 10 linhas no topo + tabelas) e também no Project ("relatorios/<data>.md").
6. Escreva `ops/semanas/<próxima semana>/briefing.md`: 5–8 recomendações objetivas para o Roteirista (temas, ganchos, duração, horários).
7. Atualize o painel (`stats/geral`, evento) e mande ao dono o resumo + link do relatório.
