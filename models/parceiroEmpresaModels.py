from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from conexao.conect_db import Base


class ParceiroEmpresa(Base):
    __tablename__ = "parceiro_empresa"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="parceiro_empresa")
    local_id = Column(Integer, ForeignKey("localAcesso.id"), nullable=True)
    local = relationship("LocalAcesso", back_populates="parceiro_empresa")
    
    data_registro = Column(Date, nullable=True)
    data_alteracao = Column(Date, nullable=True)
        
    RazaoSocial = Column(String(255))
    NomeFantasia = Column(String(255))
    CNAE = Column(Integer, nullable=True)
    Tipo = Column(Integer)
    CNPJCPF = Column(BigInteger, nullable=False) 
    Logradouro = Column(String(255))
    Numero = Column(String(10))
    Bairro = Column(String(255))
    CEP = Column(Integer)
    Cidade = Column(String(255))
    Estado = Column(String(2))
    Is_PessoaJuridico = Column(Boolean)
    Is_PessoaFisico = Column(Boolean)
    Telefone = Column(BigInteger, nullable=True)
    Email = Column(String(255), nullable=True)
    InscricaoEstadual = Column(BigInteger, nullable=True)
    InscricaoMunicipal = Column(BigInteger, nullable=True) 
    ProdutosServicosFornecidos = Column(String(1024), nullable=True)
    InformacoesAdicionais = Column(String(1024), nullable=True)
    ativo = Column(Boolean)
    
    
    
    
class UnidadeRecebedora(Base):
    __tablename__ = "unidades_recebedoras"

    id = Column(Integer, primary_key=True, index=True)
    nome_filial = Column(String, unique=True, index=True, nullable=True) # Ex: "maceio", "murici", "filial-centro"
    nome_exibicao = Column(String, nullable=False)
    razosocial = Column(String, nullable=False)
    cnpj = Column(String, nullable=False)
    logo_url = Column(String, nullable=True) # Logo da Filial
    
    # Dados de Recebimento Pix / TED
    chave_pix = Column(String, nullable=True)
    qr_code_base64 = Column(String, nullable=True)
    pix_copia_cola = Column(String, nullable=True)
    banco = Column(String, nullable=True)
    agencia = Column(String, nullable=True)
    conta = Column(String, nullable=True)
    tipo_conta = Column(String, default="Conta Corrente")
    titular = Column(String, nullable=True)
    
    ativo = Column(Boolean, default=True)
