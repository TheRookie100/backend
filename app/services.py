"""
Camada de serviços para gerenciamento de filmes
Implementa CRUD com orientação a objetos e persistência JSON
"""
import json
import os
from typing import List, Optional
from datetime import datetime
from .models import Filme, FilmeCreate

class FilmeService:
    """Serviço para gerenciamento de filmes com persistência em JSON"""
    
    def __init__(self, data_file: str = "data/filmes.json"):
        self.data_file = data_file
        self._ensure_data_dir()
        self._filmes: List[dict] = self._load_filmes()
        self._next_id = self._get_next_id()
    
    def _ensure_data_dir(self) -> None:
        """Garante que o diretório de dados existe"""
        data_dir = os.path.dirname(self.data_file)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    
    def _load_filmes(self) -> List[dict]:
        """Carrega filmes do arquivo JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_filmes(self) -> None:
        """Salva filmes no arquivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self._filmes, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar filmes: {e}")
    
    def _get_next_id(self) -> int:
        """Obtém o próximo ID disponível"""
        if not self._filmes:
            return 1
        return max(filme['id'] for filme in self._filmes) + 1
    
    def listar_todos_filmes(self) -> List[Filme]:
        """Lista todos os filmes cadastrados"""
        return [Filme(**filme) for filme in self._filmes]
    
    def obter_filme_por_id(self, filme_id: int) -> Optional[Filme]:
        """Obtém um filme específico pelo ID"""
        for filme_data in self._filmes:
            if filme_data['id'] == filme_id:
                return Filme(**filme_data)
        return None
    
    def criar_filme(self, filme_create: FilmeCreate) -> Filme:
        """Cria um novo filme"""
        filme_data = {
            'id': self._next_id,
            'criado_em': datetime.now().isoformat(),
            **filme_create.dict()
        }
        
        self._filmes.append(filme_data)
        self._save_filmes()
        self._next_id += 1
        
        return Filme(**filme_data)