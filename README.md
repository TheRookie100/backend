# API de Filmes 

> **CRUD de filmes desenvolvido com FastAPI, Docker e orientação a objetos**

## Execução Rápida

### Docker (Recomendado)
```bash
git clone https://github.com/TheRookie100/backend
cd backend
docker-compose up --build -d
```

### Python Local
```bash
git clone https://github.com/TheRookie100/backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/filmes` | Lista todos os filmes |
| `POST` | `/filmes` | Cadastra novo filme |
| `GET` | `/filmes/{id}` | Retorna filme por ID |

## Teste Rápido

```powershell
# Criar filme
$filme = @{
    titulo = "Matrix"
    genero = "Acao" 
    ano = 1999
    diretor = "Wachowski Sisters"
    duracao = 136
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/filmes" -Method Post -Body $filme -Headers @{'Content-Type'='application/json'}

# Listar filmes
Invoke-RestMethod -Uri "http://localhost:8000/filmes" -Method Get
```

## Documentação

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Arquitetura

```
backend/
├── app/
│   ├── main.py      # API FastAPI
│   ├── models.py    # Validação Pydantic
│   ├── services.py  # Lógica de negócio
│   └── security.py  # Rate limiting
├── data/            # Persistência JSON
├── Dockerfile       # Container
└── docker-compose.yml
```

## Tecnologias

- **FastAPI** - Framework web
- **Pydantic** - Validação de dados
- **Docker** - Containerização
- **JSON** - Persistência simples

---

**Desenvolvido por TheRookie100 - Branch: feature/guilherme**