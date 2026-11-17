from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from conexao.conect_db import get_db
from endpoints.userEndpoints import get_current_user
from models.parceiroEmpresaModels import ParceiroEmpresa, UnidadeRecebedora
from schemas.parceiroEmpresaSchema import *

empresa = APIRouter(prefix="/api")



@empresa.post("/create-empresa/", response_model=EmpresaResponse)
def create_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
):
   
    
    try:
        db_empresa = ParceiroEmpresa(**empresa.dict())
        db_empresa.data_registro = datetime.today()

        db.add(db_empresa)
        db.commit()
        db.refresh(db_empresa)
        return db_empresa

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")



@empresa.get("/api/busca-empresa/{empresa_cnpj}")
def buscar_empresa(empresa_cnpj: str, db: Session = Depends(get_db)):
    # Limpa caracteres e converte para int para bater com a coluna CNPJCPF (Integer/BigInteger)
    cnpj_limpo = int("".join(filter(str.isdigit, empresa_cnpj)))
    
    empresa = db.query(ParceiroEmpresa).filter(ParceiroEmpresa.CNPJCPF == cnpj_limpo).first()
    
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
    return empresa


@empresa.get("/busca-empresa/{empresa_cnpj}", response_model=EmpresaResponse)
def search_empresa(
    empresa_cnpj: int,
    db: Session = Depends(get_db),
):
    db_empresa = db.query(ParceiroEmpresa).filter(ParceiroEmpresa.CNPJCPF == empresa_cnpj).first()
    if not db_empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return db_empresa


@empresa.get("/empresas", response_model=List[EmpresaResponse])
def empresas_all(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(ParceiroEmpresa).all()



@empresa.get("/empresa-by-local-id/{local_id}", response_model=List[EmpresaResponse])
def search_empresa_local(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    empresas = db.query(ParceiroEmpresa).filter(ParceiroEmpresa.local_id == local_id).all()
   
    return empresas


@empresa.put("/editar-empresa/{empresa_id}", response_model=EmpresaResponse)
def update_pessoa(
    empresa_id: int,
    pessoa: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_empresa = db.query(ParceiroEmpresa).filter(ParceiroEmpresa.id == empresa_id).first()
    if not db_empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    try:
        for key, value in pessoa.dict(exclude_unset=True).items():
            setattr(db_empresa, key, value)

        db_empresa.data_alteracao = datetime.now()
        db.commit()
        db.refresh(db_empresa)
        return db_empresa

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")



@empresa.get("/unidades/public/listar-ativas")
def listar_unidades_ativas_publico(db: Session = Depends(get_db)):
    unidades = db.query(UnidadeRecebedora).filter(UnidadeRecebedora.ativo == True).all()
    return unidades

# 2. Buscar os dados de uma unidade pelo SLUG (ex: /maceio, /murici)
@empresa.get("/unidades/public/{slug}")
def obter_unidade_por_slug(slug: str, db: Session = Depends(get_db)):
    unid = db.query(UnidadeRecebedora).filter(UnidadeRecebedora.slug == slug.lower(), UnidadeRecebedora.ativo == True).first()
    if not unid:
        raise HTTPException(status_code=404, detail="Unidade recebedora não encontrada ou inativa.")
    return unid

# ------------------------------------------------------------------
# ROTAS ADMINISTRATIVAS (Painel do Gestor)
# ------------------------------------------------------------------

# 3. Listar todas as unidades no admin
@empresa.get("/admin/unidades")
def listar_unidades_admin(db: Session = Depends(get_db)):
    return db.query(UnidadeRecebedora).all()

# 4. Criar ou atualizar unidade recebedora
@empresa.post("/admin/unidades")
def salvar_unidade_admin(payload: UnidadeSchema, db: Session = Depends(get_db)):
    existente = db.query(UnidadeRecebedora).filter(UnidadeRecebedora.slug == payload.slug).first()
    
    if existente:
        for key, value in payload.dict().items():
            setattr(existente, key, value)
        db.commit()
        db.refresh(existente)
        return existente
    else:
        nova_unidade = UnidadeRecebedora(**payload.dict())
        db.add(nova_unidade)
        db.commit()
        db.refresh(nova_unidade)
        return nova_unidade