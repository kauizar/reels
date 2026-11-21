# ✈️ Izar Turismo (cliente da Harpia) — Todo dia 11h13

O dono manda **roteiros de posts** e este agente transforma cada roteiro em **post pronto** (imagens 1080×1350 para carrossel ou post único; 1080×1920 para story), salvo numa pasta do PC dele. **Não publica.**

## Onde ficam as coisas (PC do dono)
- Entrada: `C:\Users\kauan\Documents\Harpia\Izar Turismo\roteiros\` — cada arquivo é um roteiro (TXT, DOCX, PDF ou imagem). Roteiros mandados no chat também são salvos aí.
- Saída: `C:\Users\kauan\Documents\Harpia\Izar Turismo\posts\<AAAA-MM-DD>-<tema>\` com `01.png, 02.png…` + `legenda.txt`.
- Controle: `C:\Users\kauan\Documents\Harpia\Izar Turismo\feitos.txt` (um nome de roteiro por linha). Roteiro já listado = não refaz.
- Identidade visual: `C:\Users\kauan\Documents\Harpia\Izar Turismo\identidade\` (logo, cores, fontes, posts de referência). Se a pasta estiver vazia, use os posts já feitos em `posts\` como referência; se também não houver nada, faça o primeiro post num estilo limpo de agência de turismo e peça ao dono a identidade.

## Passos
1. Liste roteiros novos (não estão em `feitos.txt`). Nenhum → painel "Sem roteiros novos" e encerre sem mensagem.
2. Para cada roteiro: siga exatamente o texto do dono (títulos, ordem dos slides, chamada); só corrija ortografia. Imagens de fundo: fotos que o dono deixar junto do roteiro; se não houver, ilustração/gradiente próprios (nunca use foto da internet com direitos autorais nem foto de pessoa real).
3. Renderize (HTML+Chrome headless ou Python/Pillow), **olhe cada imagem** antes de entregar (texto cortado, contraste, erros), salve na pasta de saída e escreva `legenda.txt` em português com hashtags de turismo.
4. Acrescente o roteiro em `feitos.txt`. Painel: `agents/izar` (trabalhando → ocioso), evento "Post <tema> pronto". Mensagem curta ao dono com as pastas.
