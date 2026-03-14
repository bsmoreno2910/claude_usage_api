# Claude Usage API

API em FastAPI para executar `claude /usage` com profiles separados.

## Endpoints

### `GET /health`
Verifica se o binário `claude` está disponível.

### `POST /usage`
Executa `claude /usage` com o token e profile informados.

#### Header opcional
`x-api-key: SUA_CHAVE_DA_API`

#### Body
```json
{
  "token": "SEU_SETUP_TOKEN",
  "profile": "conta_1"
}
```

## Subir localmente
```bash
docker compose up -d --build
```

## Teste
```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/usage \
  -H "Content-Type: application/json" \
  -H "x-api-key: troque-essa-chave" \
  -d '{
    "token": "SEU_SETUP_TOKEN",
    "profile": "conta_1"
  }'
```
