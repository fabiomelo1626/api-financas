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
from models.bannerModels import PortalBanner
from models.entradasModels import Entrada
from models.parceiroEmpresaModels import ParceiroEmpresa, UnidadeRecebedora
from schemas.bannerSchema import BannerSchema
from schemas.entradasSchemas import EntradasCreate, EntradasResponse, ValidacaoSchema
import logging
import traceback


portal = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)



@portal.get("/portal/public/destaques")
def listar_destaques_publico(db: Session = Depends(get_db)):
    itens = db.query(PortalBanner).filter(PortalBanner.ativo == True).order_by(PortalBanner.ordem.asc()).all()
    return {
        "carrossel": [i for i in itens if i.tipo == "CARROSSEL"],
        "cards": [i for i in itens if i.tipo == "CARD"]
    }


# 2. Rotas Administrativas (Dashboard)
@portal.get("/admin/destaques")
def listar_destaques_admin(db: Session = Depends(get_db)):
    return db.query(PortalBanner).order_by(PortalBanner.ordem.asc()).all()


@portal.post("/admin/portal/destaques")
def criar_destaque_admin(payload: BannerSchema, db: Session = Depends(get_db)):
    novo = PortalBanner(**payload.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@portal.delete("/admin/portal/destaques/{item_id}")
def deletar_destaque_admin(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PortalBanner).filter(PortalBanner.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return {"mensagem": "Removido com sucesso"}
