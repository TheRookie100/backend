"""
Modelos de dados para a API de Filmes
Usando Pydantic para validação automática e documentação
Modelos seguros com validações reforçadas
https://medium.com/@habbema/pydantic-23fe91b5749b

"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class FilmeBase(BaseModel):
    """Modelo base com validações de segurança"""
    titulo: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Título do filme",
        example="O Poderoso Chefão"
    )
    genero: str = Field(
        ..., 
        min_length=1, 
        max_length=30,   
        description="Gênero do filme",
        example="Drama"
    )
    ano: int = Field(
        ..., 
        ge=1900, 
        le=2030, 
        description="Ano de lançamento",
        example=1972
    )
    diretor: str = Field(
        ..., 
        min_length=1, 
        max_length=80,   
        description="Diretor do filme",
        example="Francis Ford Coppola"
    )
    duracao: int = Field(
        ..., 
        ge=1, 
        le=1000,        
        description="Duração em minutos",
        example=175
    )
    
    @validator('titulo', 'diretor')
    def validar_campos_texto(cls, v):
        """Validação de segurança para campos de texto"""
        # PREVENIR XSS E INJECTION
        if re.search(r'[<>"\']|script|javascript|onload', v, re.IGNORECASE):
            raise ValueError('Caracteres perigosos detectados')
        return v.strip()
    
    @validator('genero')
    def validar_genero(cls, v):
        """Validação específica para gênero"""
        generos_validos = [
            'Acao', 'Aventura', 'Comedia', 'Drama', 'Terror', 
            'Thriller', 'Romance', 'Ficcao Cientifica', 'Animacao',
            'Documentario', 'Crime', 'Musical'
        ]
        if v not in generos_validos:
            raise ValueError(f'Gênero deve ser um dos: {", ".join(generos_validos)}')
        return v

class FilmeCreate(FilmeBase):
    """Modelo para criação com validações extras"""
    pass

class Filme(FilmeBase):
    """Modelo completo seguro"""
    id: int = Field(description="ID único do filme")
    criado_em: datetime = Field(description="Data de criação")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Modelo de resposta de erro padronizado e seguro"""
    error: str = Field(description="Tipo do erro")
    message: str = Field(description="Mensagem do erro")
    timestamp: datetime = Field(default_factory=datetime.now)