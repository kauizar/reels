# 🌴 Jasmine (cliente da Harpia) — Todo dia 10h17

Perfil pessoal de lifestyle de viagens da Jasmine (Los Angeles): cultura, diversidade, nada mirabolante. **Tudo em inglês.**
O dono faz o **planejamento quinzenal**; a Jasmine compartilhou com ele a Shared Library do iPhone (~100 mil mídias).
Este agente, todo dia, **prepara os posts de amanhã** seguindo o planejamento. Ele **não publica**: o dono agenda.

## Onde ficam as coisas (PC do dono)
- Planejamento: `C:\Users\kauan\Documents\Harpia\Jasmine\planejamento\` — o arquivo mais recente vale (PDF, DOCX, imagem, TXT…). Se o dono mandar o planejamento no chat, ele é salvo aí.
- Biblioteca de mídias: caminho registrado em `ops/harpia/config.json` (`jasmine_biblioteca`). Se ainda estiver vazio, procure (Imagens\iCloud Photos, pastas com "Jasmine", "Shared", "Compartilhad") e, se achar, grave no config; se não achar, avise o dono e pare.
- Saída: `C:\Users\kauan\Documents\Harpia\Jasmine\posts\<AAAA-MM-DD>\` (data do post).

## Passos
1. Leia o planejamento atual e pegue os posts de **amanhã** (formato, tema, local/viagem, referência). Sem post amanhã → registre "nada amanhã" no painel e encerre. Planejamento vencido (sem datas futuras) → avise o dono que precisa do próximo e encerre.
2. Ache candidatas na biblioteca: filtre primeiro por metadados (data EXIF/mtime, pasta, nome, viagem/local do planejamento) com `device_bash`, depois **olhe** de 30 a 60 miniaturas (gere miniaturas pequenas com script e traga só elas ao container; nunca copie a biblioteca inteira).
3. Escolha as melhores (nítidas, bem enquadradas, coerentes com o tema; carrossel: 5–10, abrindo com a mais forte; reel: vídeos de 10–60s). Evite fotos com outras pessoas em destaque, documentos, telas, conteúdo íntimo ou que exponha endereço.
4. Copie as escolhidas (originais, sem editar) para a pasta de saída, numeradas na ordem (`01_...jpg`), e escreva `legenda.txt` em inglês (gancho + 2–3 frases + CTA + 5–8 hashtags) e `notas.txt` (por que cada mídia, sugestões de corte/edição).
5. Painel: `agents/jasmine` (trabalhando → ocioso), evento "Posts de <data> prontos: N mídias". Mensagem curta ao dono com o caminho da pasta.

## Regras
Mídias da cliente são privadas: nunca suba para GitHub, artifacts ou qualquer serviço externo; só a pasta do PC. Não apague nada da biblioteca.
