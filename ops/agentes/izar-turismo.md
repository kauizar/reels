# ✈️ Izar Turismo (cliente da Harpia) — todo dia 20h47

A Izar Turismo **não** está conectada ao Claude: o agente só **produz** e deixa na pasta; o dono pega no dia e publica.

## Ritmo semanal
Todo **domingo** o dono manda os roteiros de **2 viagens** (Y e X). Com eles, o agente faz:

| Dia | Peça |
|---|---|
| Segunda | **Post** da viagem Y (carrossel 1080×1350, 5–8 slides, ou post único se o roteiro pedir) |
| Terça | **Stories** da viagem Y (1080×1920, 3–5 telas) |
| Quarta | **Post** da viagem X |
| Quinta | **Stories** da viagem X |

Ordem: o 1º roteiro recebido (ou o que o dono marcar como Y) é o de segunda.

## Pastas (PC do dono)
- Entrada: `C:\Users\kauan\Documents\IZAR TURISMO POSTS\_ROTEIROS (coloque aqui)\` — TXT, DOCX, PDF ou imagens; fotos que vierem junto podem ser usadas nas artes. Se o dono mandar no chat, salve aí.
- Identidade: `...\IZAR TURISMO POSTS\_IDENTIDADE (logo e cores)\` (logo, cores, fontes, posts de referência). Vazia → use as peças já feitas como referência; se não houver nenhuma, faça um estilo limpo de agência de turismo e peça a identidade ao dono.
- Saída: uma pasta por dia em `...\IZAR TURISMO POSTS\`, ex.: `2026-11-23 (seg) - POST - Fernando de Noronha\` com `01.png, 02.png…` + `legenda.txt` (posts) ou só as telas numeradas + `textos.txt` (stories: enquetes/links/stickers sugeridos).
- Controle: `_ROTEIROS (coloque aqui)\feitos.txt` — `<arquivo do roteiro> -> <pastas geradas>`.

## Identidade da Izar (padrão atual — siga as referências em `_IDENTIDADE`)
- Referência principal: `referencia-carrossel-01..04.png` (carrossel "Treze Tílias", nov/2026). Copie esse sistema:
  - **Capa:** foto grande do destino no topo (2/3), card branco arredondado embaixo com selo pequeno em caps azul ("PRIMEIRA VIAGEM DE 2027"), título forte azul-marinho, subtítulo em azul, pílulas ("5 dias", "Pensão completa"), "Arraste →", logo Izar em quadrado branco no canto e pílula com a data no canto oposto.
  - **Miolo:** fundo branco/azul-clarinho, selo em caps ("O QUE ESTÁ INCLUSO", "EXPERIÊNCIAS"), título 2 linhas, cards brancos com ícone fino azul, título e 1 linha de descrição; numeração "02/04".
  - **Fechamento:** fundo azul-marinho, "GARANTA SUA VAGA", preço grande (se o roteiro tiver), card branco com detalhes, "Entre em contato e saiba mais!" + pílula WhatsApp **(13) 3448-7000** + logo.
- Cores: azul-marinho `#0B3D6B` (principal), azul `#0078CE`, azul-céu `#1FA8E8` (detalhes, linha pontilhada com aviãozinho), fundos `#F3F9FE` / `#EAF6FD`, branco.
- Tipografia: sans geométrica pesada nos títulos (Poppins/Plus Jakarta Sans 700–800), regular no corpo. Logo: `logo-izar-1.png` / `logo-izar-2-horizontal.png`.
- Stories (1080×1920): mesmo sistema, 3–5 telas: capa com foto + título, 1–2 telas de destaques/inclusos, tela final "Garanta sua vaga" com WhatsApp e sticker sugerido (enquete/link) em `textos.txt`.
- Fotos: use as que o dono mandar junto do roteiro. Sem foto → capa com ilustração/gradiente próprio no mesmo sistema (nunca foto da internet) e avise o dono que, com fotos do destino, fica melhor.

## Cada execução (todo dia 20h47)
1. Veja os roteiros que ainda não estão em `feitos.txt`. Para cada viagem nova, gere **todas** as peças da semana que ainda faltam e cujo dia é **amanhã ou depois** (domingo à noite → as 4 peças). Nada novo → atualize o painel e encerre sem mensagem.
2. Siga o roteiro do dono (títulos, ordem, chamadas); só corrija ortografia. Imagens: fotos que o dono mandou; sem fotos → fundos e ilustrações próprios. Nunca use foto da internet com direitos autorais nem pessoas reais. Preços, datas e condições: só os que estiverem no roteiro.
3. Renderize (HTML + Chrome headless ou Pillow), **olhe cada imagem** (texto cortado, contraste, erros), salve, escreva legenda em português com CTA para WhatsApp/direct e hashtags de turismo.
4. Atualize `feitos.txt`, o painel (`agents/izar`, evento por peça) e mande ao dono: "Semana da Izar pronta: seg Post Y, ter Stories Y, qua Post X, qui Stories X — pasta IZAR TURISMO POSTS".
