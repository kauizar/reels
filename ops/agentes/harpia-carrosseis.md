# 🦅 Carrosséis Harpia (2×/dia · 14h23 e 20h23 de Brasília = 12h23 e 18h23 Nova York)

Agente que busca temas em alta nos EUA e publica carrosséis no Instagram **@harpia.global**.
O playbook completo fica no repositório `kauizar/harpia-content` → `CLAUDE.md` (temas, checagem, slides, legenda, publicação via Windsor, LOG.md). Domingo de manhã (seg 09h37) sai o relatório semanal.

## Painel (Escritório Virtual)
Além do playbook, registre no painel (slug em `kauizar/reels` → `ops/escritorio.json`, ferramentas db_get/db_write):
- `agents/harpia` → `trabalhando` no início (tarefa: "Pesquisando tema"), `ocioso` no fim (tarefa: "Último: <tema>").
- evento `events/<AAAA-MM-DDTHH-MM-SSZ>-harpia` → `{ts, agente:"harpia", texto:"Carrossel publicado: <tema>", tipo:"ok"}` (ou `erro`).
