# Claude Usage API

API em FastAPI para executar comandos do Claude CLI com profiles separados.

## Endpoints

### `GET /health`
Verifica se o binário `claude` está disponível.

### `GET /debug/claude-version`
Retorna a versão do CLI.

### `GET /debug/claude-help`
Retorna a ajuda do CLI para descobrir os comandos disponíveis.

### `POST /usage`
Tenta executar o comando de usage com token e profile informados.

## Header opcional
Se `API_KEY` estiver configurada no ambiente, envie:

```http
x-api-key: SUA_CHAVE_DA_API
