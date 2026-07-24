# Decisões de arquitetura e segurança

Os comentários no código referenciam códigos `ADR-` e `SEC-`. Este índice
explica cada um, para que a referência seja resolvível a partir do repositório.

Os códigos vêm do registro de decisões usado durante o desenvolvimento. As
entradas abaixo descrevem o que foi decidido e por quê; o comentário no ponto
de uso descreve como.

## Arquitetura

| Código | Decisão |
| --- | --- |
| ADR-013 | Internacionalização pt-BR / en. O backend traduz mensagens de erro por `Accept-Language` e por um campo de formulário; o frontend usa `next-intl` com roteamento de locale `as-needed`, de modo que pt-BR fica na raiz e o inglês em `/en`. Os prompts do modelo têm teste de regressão próprio. |
| ADR-021 | As páginas estáticas (`/privacy`, `/terms`) existem só em pt-BR e ficam em um route group próprio, com layout raiz separado. O `app/layout.tsx` de topo é intencionalmente ausente: sem ele, cada route group declara seu próprio `<html>`/`<body>`, que é o padrão de múltiplos layouts raiz do App Router. |
| ADR-026 | Modo "rodar local": além do MiniMax na nuvem, a análise pode rodar em Ollama ou LM Studio na máquina do usuário. O seletor de modelo aparece só quando o backend confirma o suporte, e o endereço local é validado como loopback antes de qualquer requisição. |

## Segurança

Camadas de defesa contra prompt injection, já que CV e vaga são texto não
confiável que chega direto ao modelo.

| Código | Decisão |
| --- | --- |
| SEC-005 | Filtro de regex como primeira linha contra tentativas de injeção no texto de CV e vaga. Falso positivo é aceitável: nenhum CV legítimo contém "ignore previous instructions" ou pseudo-tags de sistema. |
| SEC-052 | Expansão do filtro após um payload real. As regras foram estreitadas para alvos de sequestro de instrução, evitando falso positivo em CVs de tecnologia — a regra de exfiltração de credenciais foi removida por disparar em linhas normais de contato. |
| SEC-064 | O texto é normalizado em NFKC e limpo de caracteres zero-width e de override RTL antes de a regex rodar. Sem isso, "ɪɢɴᴏʀᴇ ᴀʟʟ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ" (versaletes Unicode) ou zero-width joiners passariam batido. |
| SEC-069 | Dobra de confusables: homóglifos cirílicos e gregos são mapeados para o equivalente latino, fechando a variante do bypass acima. |
| SEC-065 | Caracteres invisíveis, de controle e sósias são desarmados na fronteira, antes de o texto chegar ao guard ou ao modelo. |
| SEC-053 | Pré-checagem com o próprio modelo como juiz, antes da análise principal, para classificar conteúdo suspeito que a regex não pega. |
| SEC-068 | O juiz foi endurecido contra ataques de menção-versus-uso — citar uma instrução ("um blog sobre prompt injection") não é o mesmo que emiti-la. |
| SEC-006 | A saída do modelo é higienizada com `bleach` antes de chegar ao React, removendo qualquer markup que ele tenha produzido. |
| SEC-063 | Limites rígidos de tamanho em cada campo de texto produzido pelo modelo, para que uma resposta descontrolada não infle o relatório. |

Validação de entrada e limites de recurso.

| Código | Decisão |
| --- | --- |
| SEC-036 | Limite de tamanho na descrição da vaga. |
| SEC-046 | Middleware ASGI que aborta uploads antes do parser do FastAPI. Roda antes de qualquer dispatcher, então um multipart acima do limite nunca é lido por inteiro: com `Content-Length` acima do cap, responde 413 sem tocar no body; sem `Content-Length`, conta os bytes durante o `receive()`. |
| SEC-055 | Checagem de `Content-Type` no nível da rota: o CV precisa ser `application/pdf` e a vaga, texto. |
| SEC-056 | Lista de assinaturas binárias conhecidas rejeitadas de saída no parser de texto. Não existe magic byte canônico para "texto", então o teste é invertido: recusa o que parece PDF, ZIP, executável e afins. |
| SEC-057 | Varredura de palavras-chave perigosas em nível de objeto do PDF (`/Encrypt`, JavaScript embutido e semelhantes) antes da extração. |
| SEC-066 | Decodificação estrita no parser de texto. O `errors="replace"` anterior trocava bytes inválidos por U+FFFD em silêncio, o que permitia contrabandear uma sequência inesperada pela lista de assinaturas ao declarar o encoding errado. |
| SEC-021 | Revisada: `RLIMIT_AS` valeria para o processo inteiro, não só para a thread de parsing, e derrubava o worker. A proteção ficou com o limite de 5 MB na entrada mais as checagens estruturais do próprio `pdfplumber`. |

Superfície e entrega.

| Código | Decisão |
| --- | --- |
| SEC-0022 | Os containers rodam com usuário não-root. |
| SEC-058 | Política de mensagem de erro em dois níveis: específica para causa benigna (formato errado, PDF protegido por senha, PDF digitalizado) e genérica para rejeição sensível à segurança, para não entregar ao atacante o motivo exato da recusa. |
| SEC-061 | Subresource Integrity em todas as tags de script emitidas pelo Next. Os hashes sha384 são calculados no build e injetados junto de `crossOrigin`, protegendo contra adulteração dos chunks em trânsito. |
