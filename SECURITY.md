# Política de segurança

## Versões suportadas

Apenas o código da branch `main` recebe correções. Não há releases versionados;
atualize para o commit mais recente antes de reportar.

## Como reportar uma vulnerabilidade

**Não abra issue pública** para falhas de segurança. Use um dos canais privados:

1. **GitHub Private Vulnerability Reporting** (preferencial):
   <https://github.com/leonardobissoli/jobmatch/security/advisories/new>
2. **LinkedIn**, por mensagem direta: <https://www.linkedin.com/in/leonardobissoli>

Inclua, sempre que possível: versão/commit afetado, passos para reproduzir,
impacto esperado e, se tiver, sugestão de correção. Relatos em português ou
inglês são bem-vindos.

Prazo-alvo: confirmação de recebimento em até 7 dias e posição sobre a correção
em até 30 dias. Após a correção, o reporte pode ser divulgado publicamente com
crédito ao autor, salvo pedido em contrário.

## Escopo

Dentro do escopo:

- Backend FastAPI (`backend/`): parsing de PDF/TXT, guarda contra prompt
  injection, limites de entrada, validação de endereço de LLM local (SSRF),
  sanitização da saída do modelo.
- Frontend Next.js (`frontend/`): rotas `app/api/*`, CSP e demais cabeçalhos
  de segurança, geração de PDF no navegador.
- `docker-compose.yml` e Dockerfiles.

Fora do escopo:

- Vulnerabilidades nos provedores de modelo (MiniMax, Ollama, LM Studio) ou nos
  modelos em si.
- Problemas que exijam acesso físico ou root na máquina onde a stack roda.
- Relatos gerados automaticamente por scanner sem prova de exploração.

## Controles existentes

As decisões de segurança do projeto são rastreadas por códigos `SEC-*` nos
comentários do código e documentadas em [docs/DECISIONS.md](docs/DECISIONS.md).

---

# Security Policy (English)

Only the `main` branch receives fixes. **Do not open a public issue** for
security problems — use [GitHub Private Vulnerability
Reporting](https://github.com/leonardobissoli/jobmatch/security/advisories/new)
or a direct message on [LinkedIn](https://www.linkedin.com/in/leonardobissoli).
Include the affected commit, reproduction steps and expected impact. Target
response: acknowledgement within 7 days, fix decision within 30 days.
Reports in English or Portuguese are welcome.
