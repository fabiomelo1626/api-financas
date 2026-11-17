from sqlalchemy.orm import Session
from models.tabelasAuxiliaresModels import *

def seed_tabelas_auxiliares(db: Session):
    status = [
        (1, "CONCLUIDO"),
        (2, "RECUSADO"),
        (3, "AGUARDANDO_VALIDACAO"),
        (4, "Cancelado"),
    ]

    tipo = [
        (1, "PIX"),
        (2, "TRANSFERENCIA")
        
    ]

   
    
    db.bulk_save_objects([Status(id=c, descricao=d) for c, d in status])
    #db.bulk_save_objects([Tipo(id=c, descricao=d) for c, d in tipo])
    db.commit()
