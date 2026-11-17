import os
import uuid
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from conexao.conect_db import get_db
from endpoints.userEndpoints import get_current_user
from models.entradasModels import Entrada
from models.parceiroEmpresaModels import ParceiroEmpresa, UnidadeRecebedora
from schemas.entradasSchemas import EntradasCreate, EntradasResponse, ValidacaoSchema
import logging
import traceback


entrada = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

# Schema auxiliar para a rota de validação de status

# ------------------------------------------------------------------
# 1. CRIAR ENTRADA (Com upload do comprovante e persistência no DB)
# ------------------------------------------------------------------
@entrada.post("/create-entrada/")
def create_entrada(
    payload: EntradasCreate,
    db: Session = Depends(get_db)
):
    try:
        nova_entrada = Entrada(
            id=str(uuid.uuid4()),
            empresa_id=payload.empresa_id,
            unidade_recebedora_id=payload.unidade_recebedora_id,
            valor=payload.valor,
            tipo_pagamento=payload.tipo_pagamento_id or 1,
            status=payload.status_id or 1,
            txid=payload.txid or f"TX-{uuid.uuid4().hex[:12].upper()}", # Garante preenchimento do txid
            descricao=payload.descricao or "Pagamento informado pelo cliente",
            data_registro=date.today(),
            comprovante_url=None
        )

        db.add(nova_entrada)
        db.commit()
        db.refresh(nova_entrada)

        return {
            "mensagem": "Pagamento registrado com sucesso!",
            "entrada_id": nova_entrada.id,
            "status": nova_entrada.status
        }

    except SQLAlchemyError as e:
        logger.exception("Erro de banco de dados ao criar aluno")
        raise HTTPException(
            status_code=500,
            detail="Erro de banco de dados ao criar aluno"
        )
    except Exception as e:
        logger.exception("Erro interno ao criar aluno")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

# ------------------------------------------------------------------
# 2. BUSCAR UMA ENTRADA ESPECÍFICA PELO ID
# ------------------------------------------------------------------
@entrada.get("/busca-entrada/{entrada_id}", response_model=EntradasResponse)
def search_entrada(
    entrada_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_entrada = db.query(Entrada).filter(Entrada.id == entrada_id).first()
    if not db_entrada:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return db_entrada


# ------------------------------------------------------------------
# 3. LISTAR TODAS AS ENTRADAS (Visão Gestor / Admin)
# ------------------------------------------------------------------
@entrada.get("/admin/entradas")
def listar_entradas_admin(db: Session = Depends(get_db)):
    resultados = db.query(
        Entrada,
        ParceiroEmpresa.RazaoSocial,
        ParceiroEmpresa.NomeFantasia,
        UnidadeRecebedora.nome_exibicao
    ).outerjoin(
        ParceiroEmpresa, Entrada.empresa_id == ParceiroEmpresa.id
    ).outerjoin(
        UnidadeRecebedora, Entrada.unidade_recebedora_id == UnidadeRecebedora.id
    ).order_by(Entrada.data_registro.desc()).all()

    entradas_formatadas = []
    for reg_entrada, razao_social, nome_fantasia, nome_unidade in resultados:
        entradas_formatadas.append({
            "id": str(reg_entrada.id),
            "empresa_id": reg_entrada.empresa_id,
            "empresa_nome": nome_fantasia or razao_social or f"Empresa #{reg_entrada.empresa_id}",
            "unidade_recebedora_id": reg_entrada.unidade_recebedora_id,
            "unidade_nome": nome_unidade or "Matriz",
            "valor": reg_entrada.valor or 0.0,
            "tipo_pagamento": reg_entrada.tipo_pagamento or 1,
            "status": reg_entrada.status or 1,
            "txid": reg_entrada.txid,
            "descricao": reg_entrada.descricao,
            "data_registro": reg_entrada.data_registro.isoformat() if reg_entrada.data_registro else None
        })

    return entradas_formatadas


# ------------------------------------------------------------------
# 4. MUDAR O STATUS PARA VALIDAÇÃO (Aprovar / Recusar)
# ------------------------------------------------------------------
@entrada.patch("/admin/entradas/{entrada_id}/validar")
def validar_entrada(
    entrada_id: str,
    payload: ValidacaoSchema,
    db: Session = Depends(get_db)
):
    registro = db.query(Entrada).filter(Entrada.id == entrada_id).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")

    # Atualiza o status conforme a escolha do operador
    registro.status = payload.status_id if payload.status_id else (2 if payload.aprovado else 3)
    registro.data_alteracao = date.today()

    try:
        db.commit()
        db.refresh(registro)
        return {
            "mensagem": "Entrada validada com sucesso!",
            "entrada_id": registro.id,
            "status": registro.status
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar entrada: {str(e)}")