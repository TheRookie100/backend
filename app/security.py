"""
Módulo de segurança para a API
https://medium.com/geekculture/system-design-design-a-rate-limiter-81d200c9d392
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from typing import Dict
import logging

# Configurar logging seguro
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting simples para prevenir DoS"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Verifica se o IP pode fazer mais requests"""
        now = time.time()
        
        # Limpar requests antigos
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        # Verificar limite
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # Adicionar request atual
        self.requests[client_ip].append(now)
        return True

# Instância global do rate limiter
rate_limiter = RateLimiter(max_requests=50, window_seconds=60)

def check_rate_limit(request: Request):
    """Middleware para verificar rate limiting"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas solicitações. Tente novamente em alguns minutos."
        )

def sanitize_error_message(error: Exception) -> str:
    """Sanitiza mensagens de erro para não expor informações sensíveis"""
    # Mapear erros conhecidos para mensagens seguras
    error_map = {
        "FileNotFoundError": "Erro de configuração do sistema",
        "PermissionError": "Erro de acesso ao sistema",
        "JSONDecodeError": "Erro no formato dos dados",
    }
    
    error_type = type(error).__name__
    return error_map.get(error_type, "Erro interno do servidor")