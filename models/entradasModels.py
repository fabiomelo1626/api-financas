from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from conexao.conect_db import Base


class Entrada(Base):
    __tablename__ = "entrada"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="entrada")
    local_id = Column(Integer, ForeignKey("localAcesso.id"), nullable=True)
    local = relationship("LocalAcesso", back_populates="entrada")
    
    data_registro = Column(Date, nullable=True)
    data_alteracao = Column(Date, nullable=True)
        
    empresa_id = Column(Integer, ForeignKey("parceiro_empresa.id"), nullable=True)
    unidade_recebedora_id = Column(Integer, ForeignKey("unidades_recebedoras.id")) # Recebedor
    valor = Column(Float, nullable=True)
    tipo_pagamento = Column(Integer, ForeignKey("tipo.id"), nullable=True)
    status = Column(Integer, ForeignKey("status.id"), nullable=True)
    txid = Column(String, nullable=False) 
    qr_code_payload = Column(String)
    comprovante_url = Column(String)
    descricao = Column((String), nullable=True)
    