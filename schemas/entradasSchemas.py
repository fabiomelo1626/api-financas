from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class EntradasSchema(BaseModel):
    empresa_id: int               # ID do Pagador
    unidade_recebedora_id: int    # ID da Filial Recebedora
    valor: float
    tipo_pagamento_id: Optional[int] = 1  # ID referente ao tipo (ex: 1 = PIX, 2 = TED)
    status_id: Optional[int] = 1          # ID referente ao status (ex: 1 = PENDENTE / AGUARDANDO_VALIDACAO)
    descricao: Optional[str] = None
    txid: Optional[str] = None
   
    class Config:
        from_attributes = True

class EntradasCreate(EntradasSchema):
    pass

class EntradasResponse(EntradasSchema):
    id: str


class ValidacaoSchema(BaseModel):
    status_id: Optional[int] = 2  # 2 = CONCLUIDO, 3 = RECUSADO
    aprovado: bool