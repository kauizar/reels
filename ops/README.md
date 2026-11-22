# Escritório Virtual — manual geral

Dois andares: **2º andar Harpia Global** (Carrosséis Harpia, Jasmine, Izar Turismo — playbooks `agentes/harpia-carrosseis.md`, `jasmine.md`, `izar-turismo.md`) e **1º andar Vídeos** (abaixo).

## 1º andar — Operação "O que aconteceria se..."

Mini-operação de vídeos com 6 agentes (sessões agendadas do Claude). Todos leem este repositório
(`kauizar/reels`) e gravam o progresso aqui e no **Escritório Virtual** (painel/artifact).

## Calendário fixo (horário de Brasília)

| Dia | O que sai |
|---|---|
| Seg–Sáb | 3 Shorts de ~1:05 — Instagram 12h00 · 16h00 · 19h00 / TikTok 13h00 · 17h00 · 20h00 (manual, pelo dono) / YouTube Shorts 14h00 · 18h00 · 21h00 |
| 1ª quarta-feira do mês | 1 vídeo longo (~42 min, horizontal) no YouTube às 20h30 |
| Domingo | Sem postagem. Relatórios, checkup, roteiros e produção da semana |

Orçamento de voz: **ElevenLabs Creator (121 mil créditos/mês)**. Shorts na voz normal (~1 crédito/caractere, ~78 mil/mês); o longo mensal no modelo **Flash** (~0,5 crédito/caractere, ~19 mil). Sobra ~20 mil para refações.

## Agentes e horários de trabalho

| Agente | Quando roda | Faz |
|---|---|---|
| 📊 Analista (Relatórios) | Dom 09h | Puxa métricas (Windsor: IG + YouTube), escreve relatório, define temas da semana |
| ✍️ Roteirista | Dom 10h | 18 roteiros de Shorts + 3 roteiros longos da semana, legendas, títulos, descrições |
| 🎙️ Narrador | Seg–Sáb 07h | Gera as narrações do dia (3 Shorts; + o longo quando o plano tiver um no dia) no ElevenLabs, pelo navegador do app Claude no PC do dono |
| 🎬 Produtor | Seg–Sáb 08h | Anima/renderiza os 3 Shorts do dia, sobe no repo, agenda no YouTube Studio, manda legendas TikTok |
| 🎞️ Documentarista | Quartas 09h23 (só trabalha na 1ª quarta do mês) | Produz o vídeo longo do dia e agenda no YouTube para 20h30 |
| 📤 Publicador | Seg–Sáb 12h, 16h, 19h | Publica o Reel da vez no Instagram (Windsor) e confere o Short do horário |

Fluxo de um Short: `roteiro → narrado → renderizado → agendado_yt → publicado_ig` (+ TikTok manual).

## Regras de ouro
1. **Nunca publicar** nada fora do plano da semana aprovado (`ops/semanas/<semana>/plano.json`).
2. Toda ação registra um evento no Escritório Virtual (collection `events`) e atualiza o item em `items`.
3. Falhou? Registra o erro no painel, avisa o dono e **não** tenta caminhos que contornem segurança de site.
4. TikTok bloqueia upload automático: o Produtor manda as legendas TikTok do dia pro dono, que agenda pelo app.
5. Narração e YouTube Studio dependem do PC do dono ligado com o app Claude aberto. Se estiver offline: avisar e seguir com o resto.
6. Conteúdo original, sem música com direitos autorais, variar o visual entre vídeos (política de conteúdo repetitivo do YouTube).

## Onde fica cada coisa
- `pipeline/` — motor de animação (lib), ferramentas (setup, align, render, still, assemble), exemplos de vídeos prontos
- `ops/agentes/*.md` — instruções de cada agente
- `ops/semanas/<AAAA-Www>/plano.json` — plano da semana (fila de itens)
- `ops/semanas/<AAAA-Www>/roteiros/<id>.txt` — roteiros
- `ops/semanas/<AAAA-Www>/narracoes/<id>.mp3` — narrações (Git)
- raiz do repo — vídeos finais `.mp4` (URL pública raw usada pelo Instagram)
- `ops/relatorios/<data>.md` — relatórios de domingo
