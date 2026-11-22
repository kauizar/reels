# 🌴 Jasmine (cliente da Harpia) — todo dia 10h17

Perfil pessoal de lifestyle de viagens da Jasmine (Los Angeles): cultura, diversidade, nada mirabolante. **Tudo para a cliente em inglês.**
A Jasmine **não** está conectada ao Claude: o agente só **prepara**; o dono pega na pasta no dia e publica.
O dono manda o **calendário a cada 15 dias**. Todo dia, às 10h17, o agente prepara o post **do próprio dia** e avisa o dono quando estiver pronto (é o combinado: "faz no dia e me diz quando estiver pronto"). Resumo do calendário vigente: `ops/harpia/jasmine-calendario-atual.md`.

## Pastas (PC do dono)
- Calendário: `C:\Users\kauan\Documents\JASMINE POSTS\_CALENDARIO (coloque aqui)\` — o arquivo mais recente vale. Se o dono mandar no chat, salve aí.
- Biblioteca de mídias: `C:\Users\kauan\iCloudPhotos\Photos` (~39 mil arquivos; mistura fotos do dono com a Shared Library da Jasmine). Listar tudo demora: filtre por data com `find -newermt`, limite o tempo de cada comando e trabalhe em lotes.
- Saída: `C:\Users\kauan\Documents\JASMINE POSTS\<AAAA-MM-DD> (<dia>) - <formato> - <tema>\`.

## Passos
1. Leia o calendário e pegue o post de **hoje** (formato, tema, viagem/local, referência). Sem post hoje → painel "nada hoje" e encerre sem mensagem. **Stories ficam por conta da própria Jasmine**: em dia de Stories o agente não prepara nada — só registra "Stories: com a Jasmine" no painel e encerra sem mensagem. O agente faz apenas **feed posts e carrosséis**. Calendário acabando (≤ 2 dias restantes) → avise o dono que precisa do próximo.
2. Ache candidatas: filtre por metadados (data EXIF/arquivo, período da viagem do calendário) e **olhe** 30–60 miniaturas (gere miniaturas pequenas no PC e traga só elas). Nunca copie a biblioteca inteira.
3. Escolha as melhores (nítidas, bem enquadradas, coerentes com o tema; carrossel 5–10 abrindo com a mais forte; reel: vídeos de 10–60 s). Evite fotos com outras pessoas em destaque, documentos, telas, conteúdo íntimo ou que exponha endereço — e **só fotos da Jasmine/da viagem dela**, não do dono.
4. Copie os originais para a pasta de saída, numerados (`01_...jpg`), com `caption.txt` em inglês (gancho + 2–3 frases + CTA + 5–8 hashtags) e `notas.txt` em português (por que cada mídia, sugestões de corte/edição).
5. Painel: `agents/jasmine` (trabalhando → ocioso), evento "Posts de <data> prontos". Mensagem ao dono: "✅ Jasmine — <formato> de hoje pronto: pasta <nome>" + qualquer pendência.

## Regras
Mídias da cliente são privadas: nunca vão para GitHub, artifacts ou qualquer serviço externo — só para a pasta do PC. Não apague nem altere nada na biblioteca.
