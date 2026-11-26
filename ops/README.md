# Escritório Virtual — manual geral

Dois andares: **2º andar Harpia Global** (Carrosséis Harpia; Jasmine entrega em Documentos\JASMINE POSTS — playbooks `agentes/harpia-carrosseis.md`, `jasmine.md`) e **1º andar Vídeos** (abaixo).

## 1º andar — Operação "O que aconteceria se..."

Mini-operação de vídeos com 6 agentes (sessões agendadas do Claude). Todos leem este repositório
(`kauizar/reels`) e gravam o progresso aqui e no **Escritório Virtual** (painel/artifact).

## Calendário fixo (horário de Brasília)

| Dia | O que sai |
|---|---|
| Todo dia (dom a dom) | 2 Shorts de ~1:05 — Instagram Reels 12h00 · 19h00 / YouTube Shorts 14h00 · 18h00 / TikTok: o dono posta manualmente os arquivos da pasta `C:\Users\kauan\Downloads\VIDEOS TIKTOK` |
| 1ª quarta-feira do mês | 1 vídeo longo (~42 min, horizontal) no YouTube às 20h30 |
| Domingo | Também tem os 2 Shorts. Além disso: relatórios, checkup e roteiros da semana seguinte |

Orçamento de voz: **ElevenLabs Creator (~120 mil créditos/mês)**. Shorts na voz normal (~1 crédito/caractere; 2/dia × ~31 dias ≈ 58 mil/mês); o longo mensal no modelo **Flash** (~0,5 crédito/caractere, ~19 mil). Sobra ~20 mil para refações.

## Agentes e horários de trabalho

| Agente | Quando roda | Faz |
|---|---|---|
| 📊 Analista (Relatórios) | Dom 09h | Puxa métricas (Windsor: IG + YouTube), escreve relatório, define temas da semana |
| ✍️ Roteirista | Dom 10h | 14 roteiros de Shorts (seg–dom × 2) + o longo do mês quando houver, legendas, títulos, descrições |
| 🎙️ Narrador | Todo dia 07h | Gera as narrações do dia (2 Shorts; + o longo quando o plano tiver um no dia) no ElevenLabs, pelo navegador do app Claude no PC do dono |
| 🎬 Produtor | Todo dia 08h | Anima/renderiza os 2 Shorts do dia, sobe no repo, agenda no YouTube Studio, copia os mp4 para Downloads\VIDEOS TIKTOK e manda as legendas TikTok |
| 🎞️ Documentarista | Quartas 09h23 (só trabalha na 1ª quarta do mês) | Produz o vídeo longo do dia e agenda no YouTube para 20h30 |
| 📤 Publicador | Todo dia 12h e 19h | Publica o Reel da vez no Instagram (Windsor) e confere o Short do horário |

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
