"""
API FastAPI para gerenciamento de filmes 
Implementa endpoints RESTful com documentação automática
"""

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from typing import List
import logging
from .models import Filme, FilmeCreate, ErrorResponse
from .services import FilmeService
from .security import check_rate_limit, sanitize_error_message

# Configurar logging
logger = logging.getLogger(__name__)

# CONFIGURAÇÃO SEGURA DA API
app = FastAPI(
    title="API de Filmes",
    description="API segura para gerenciamento de filmes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS RESTRITIVO E SEGURO
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       
    ],
    allow_credentials=False,         
    allow_methods=["GET", "POST"],   
    allow_headers=["Content-Type"],  
)

# TRUSTED HOST MIDDLEWARE
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "seu-dominio.com"]
)

# Instância do serviço
filme_service = FilmeService()

# HANDLER DE ERROS SEGURO
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar erros e não expor informações"""
    logger.error(f"Erro não tratado: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Erro interno do servidor"
        }
    )

@app.get("/", tags=["Health Check"])
def health_check():
    """Health check seguro sem exposição de informações"""
    return {
        "status": "online",
        "service": "API de Filmes",
        "version": "1.0.0"
    }

@app.get("/filmes", response_model=List[Filme], tags=["Filmes"])
def listar_filmes(request: Request, _: None = Depends(check_rate_limit)):
    """[GET] Lista filmes com rate limiting"""
    try:
        filmes = filme_service.listar_todos_filmes()
        
        # LOG SEGURO SEM DADOS SENSÍVEIS
        logger.info(f"Listagem de filmes - IP: {request.client.host}")
        
        return filmes
    except Exception as e:
        logger.error(f"Erro ao listar filmes: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=sanitize_error_message(e)
        )

@app.post("/filmes", response_model=Filme, status_code=status.HTTP_201_CREATED, tags=["Filmes"])
def criar_filme(filme: FilmeCreate, request: Request, _: None = Depends(check_rate_limit)):
    """[POST] Cria filme com validações de segurança"""
    try:
        # VALIDAÇÃO DE TAMANHO DO PAYLOAD
        if len(filme.json()) > 1024:  # Max 1KB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Payload muito grande"
            )
        
        novo_filme = filme_service.criar_filme(filme)
        
        # LOG SEGURO
        logger.info(f"Filme criado - ID: {novo_filme.id} - IP: {request.client.host}")
        
        return novo_filme
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar filme: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=sanitize_error_message(e)
        )

@app.get("/filmes/{filme_id}", response_model=Filme, tags=["Filmes"])
def obter_filme(filme_id: int, request: Request, _: None = Depends(check_rate_limit)):
    """[GET] Busca filme com validações de segurança"""
    # VALIDAÇÃO DE ID
    if not isinstance(filme_id, int) or filme_id <= 0 or filme_id > 999999:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )
    
    try:
        filme = filme_service.obter_filme_por_id(filme_id)
        
        if not filme:
            # LOG DE TENTATIVA DE ACESSO
            logger.warning(f"Tentativa de acesso a filme inexistente - ID: {filme_id} - IP: {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Filme não encontrado"
            )
        
        return filme
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar filme: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=sanitize_error_message(e)
        )