# Job Match — execução local

Compare um CV em PDF com uma descrição de vaga e receba score de 0 a 100, análise em seis dimensões, gaps priorizados e plano de ação.

Esta edição foi preparada exclusivamente para execução local. Ela não captura e-mail, não mantém banco de dados, não armazena CVs ou relatórios e não contém configuração de deploy.

## Requisitos

- Docker com Docker Compose v2
- Uma das opções de modelo:
  - chave própria da API MiniMax; ou
  - Ollama rodando na máquina host; ou
  - servidor local do LM Studio rodando na máquina host

## Início rápido

```bash
cp .env.example .env
docker compose up --build
```

Abra `http://localhost:3000`.

A API local e sua documentação OpenAPI ficam em `http://localhost:8001/docs`.

Para encerrar:

```bash
docker compose down
```

## MiniMax

Preencha sua própria chave no `.env`:

```dotenv
MINIMAX_API_KEY=sua-chave-aqui
```

Suba novamente a stack e mantenha **MiniMax (nuvem)** selecionado na interface. Ao usar MiniMax, o texto extraído do CV e da vaga é enviado à API externa.

## Ollama

Instale o Ollama na máquina host, baixe um modelo compatível e inicie o servidor. Exemplo:

```bash
ollama pull <modelo>
ollama serve
```

Na interface:

1. Selecione **Rodar local**.
2. Escolha **Ollama**.
3. Mantenha `http://localhost:11434`.
4. Clique em **Testar conexão** e selecione o modelo encontrado.

O backend valida que o endereço recebido é loopback e, dentro do Docker, encaminha a conexão para `host.docker.internal`.

## LM Studio

No LM Studio, carregue um modelo e ative o servidor OpenAI-compatible. Na interface do Job Match:

1. Selecione **Rodar local**.
2. Escolha **LM Studio**.
3. Mantenha `http://localhost:1234`, salvo se você mudou a porta no LM Studio.
4. Clique em **Testar conexão** e selecione o modelo encontrado.

O servidor do LM Studio deve aceitar conexões vindas do Docker. A opção correspondente normalmente aparece nas configurações do servidor local.

## Privacidade

- CV e vaga são processados em memória durante cada análise.
- Não existe banco de dados, captura de lead, analytics ou sincronização externa nesta edição.
- O PDF é gerado diretamente no navegador.
- Ollama e LM Studio processam na máquina local.
- MiniMax é um provedor externo; consulte os termos do serviço antes de enviar dados pessoais ou confidenciais.

## Desenvolvimento sem Docker

Backend:

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8001
```

Frontend, em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

Ao executar o backend fora do Docker, o valor padrão de `LOCAL_LLM_HOST=localhost` acessa Ollama e LM Studio diretamente.

## Testes

```bash
cd backend
uv run pytest

cd ../frontend
npm run typecheck
npm run build
```

## Licença

MIT. Consulte [LICENSE](LICENSE).

Leonardo Bissoli — Tech Hub
