# models/portalConfigModels.py
from sqlalchemy import Column, Date, Integer, String, Boolean, Text, DateTime
from conexao.conect_db import Base
import datetime


class PortalBanner(Base):
    __tablename__ = "portal_banners"
    
    data_registro = Column(Date, nullable=True)
    data_alteracao = Column(Date, nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    subtitulo = Column(String, nullable=True)
    imagem_base64 = Column(String, nullable=False) # Imagem do slide/card
    link_destino = Column(String, nullable=True)  # Ex: "/maceio" ou link externo
    tipo = Column(String, default="CARROSSEL")    # "CARROSSEL" ou "CARD"
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
