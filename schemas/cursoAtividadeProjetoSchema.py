from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class CursoAtividadeProjetoSchema(BaseModel):
    user_id: Optional[int] = None
    local_id: Optional[int] = None

    data_registro: Optional[datetime] = None
    data_alteracao: Optional[datetime] = None
    nome_curso_projeto : Optional[str] = None
    desricao : Optional[str] = None
        
    
   
    class Config:
        from_attributes = True

class CursoAtividadeProjetoCreate(CursoAtividadeProjetoSchema):
    pass

class CursoAtividadeProjetoResponse(CursoAtividadeProjetoSchema):
    id: int
