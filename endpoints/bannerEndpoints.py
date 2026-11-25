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



#NOVAS ROTAS 

import os
import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from conexao.conect_db import get_db
from models.bannerModels import PortalBanner
# importe sua dependência de autenticação (ex: get_current_user)

portal_router = APIRouter(prefix="/api")

UPLOAD_DIR = "uploads/portal"
os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".webp"}
EXTENSOES_VIDEO = {".mp4", ".webm"}
TAMANHO_MAX_VIDEO = 15 * 1024 * 1024  # 15 MB


# 1. ENDPOINT PÚBLICO (Consumido pela Home Page)
@portal_router.get("/portal/public/destaques")
def listar_destaques_publico(db: Session = Depends(get_db)):
    itens = (
        db.query(PortalBanner)
        .filter(PortalBanner.ativo == True)
        .order_by(PortalBanner.ordem.asc(), PortalBanner.id.desc())
        .all()
    )

    carrossel = [i for i in itens if (i.tipo or "").upper() == "CARROSSEL"]
    cards = [i for i in itens if (i.tipo or "").upper() == "CARD"]

    return {
        "carrossel": carrossel,
        "cards": cards,
    }


# 2. LISTAGEM ADMINISTRATIVA
@portal_router.get("/admin/destaques")
def listar_destaques_admin(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(PortalBanner)
        .order_by(PortalBanner.tipo.asc(), PortalBanner.ordem.asc(), PortalBanner.id.desc())
        .all()
    )


# 3. UPLOAD EM LOTE DE IMAGENS OU VÍDEOS CURTOS (Multipart/Form-Data)
@portal_router.post("/admin/portal/destaques/upload-lote")
async def upload_destaques_lote(
    arquivos: List[UploadFile] = File(...),
    titulos: List[str] = Form(...),
    subtitulos: List[str] = Form([]),
    links_destino: List[str] = Form([]),
    tipos: List[str] = Form(...),
    ordens: List[int] = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not arquivos:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    hoje = date.today()
    criados = []

    for idx, arquivo in enumerate(arquivos):
        ext = os.path.splitext(arquivo.filename or "")[1].lower()

        if ext in EXTENSOES_IMAGEM:
            tipo_imagem = "IMAGEM"
        elif ext in EXTENSOES_VIDEO:
            tipo_imagem = "VIDEO"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado ({arquivo.filename}). Use JPG, PNG, WEBP, MP4 ou WEBM.",
            )

        conteudo = await arquivo.read()

        if tipo_imagem == "VIDEO" and len(conteudo) > TAMANHO_MAX_VIDEO:
            raise HTTPException(
                status_code=400,
                detail=f"O vídeo '{arquivo.filename}' excede o limite de 15 MB.",
            )

        nome_unico = f"{uuid.uuid4().hex}{ext}"
        caminho_fisico = os.path.join(UPLOAD_DIR, nome_unico)

        with open(caminho_fisico, "wb") as f:
            f.write(conteudo)

        url_publica = f"/uploads/portal/{nome_unico}"

        titulo = titulos[idx].strip() if idx < len(titulos) and titulos[idx].strip() else "Destaque"
        subtitulo = subtitulos[idx].strip() if idx < len(subtitulos) and subtitulos[idx].strip() else None
        link = links_destino[idx].strip() if idx < len(links_destino) and links_destino[idx].strip() else None
        tipo = tipos[idx].upper() if idx < len(tipos) else "CARROSSEL"
        ordem = ordens[idx] if idx < len(ordens) else idx + 1

        novo = PortalBanner(
            data_registro=hoje,
            data_alteracao=hoje,
            titulo=titulo,
            subtitulo=subtitulo,
            imagem_base64=url_publica,
            tipo_imagem=tipo_imagem,
            link_destino=link,
            tipo=tipo,
            ordem=ordem,
            ativo=True,
        )
        db.add(novo)
        criados.append(novo)

    db.commit()
    return {"message": f"{len(criados)} mídia(s) cadastrada(s) com sucesso.", "total": len(criados)}


# 4. EXCLUSÃO (Remove registro no banco + arquivo físico se estiver em /uploads/)
@portal_router.delete("/admin/portal/destaques/{destaque_id}")
def deletar_destaque(
    destaque_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(PortalBanner).filter(PortalBanner.id == destaque_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Destaque não encontrado.")

    # Se for arquivo salvo em disco (/uploads/portal/...), apaga o arquivo físico
    if item.imagem_base64 and item.imagem_base64.startswith("/uploads/"):
        caminho_arquivo = item.imagem_base64.lstrip("/")
        if os.path.exists(caminho_arquivo):
            try:
                os.remove(caminho_arquivo)
            except OSError:
                pass

    db.delete(item)
    db.commit()
    return {"ok": True}