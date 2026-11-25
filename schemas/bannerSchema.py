from datetime import datetime
from typing import Optional
from pydantic import BaseModel





class BannerSchema(BaseModel):
    titulo: str
    subtitulo: Optional[str] = None
    tipo_imagem : str
    imagem_base64: str
    link_destino: Optional[str] = None
    tipo: str = "CARROSSEL" # "CARROSSEL" ou "CARD"
    ordem: int = 0
    
    
    class Config:
        from_attributes = True
    
class BannerCreate(BannerSchema):
    pass
    
class BannerResponse(BannerSchema):
    id: int

