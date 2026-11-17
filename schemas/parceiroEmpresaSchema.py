from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class EmpresaSchema(BaseModel):
    user_id: Optional[int] = None
    local_id: Optional[int] = None

    data_registro: Optional[datetime] = None
    data_alteracao: Optional[datetime] = None
    RazaoSocial: Optional[str] = None
    NomeFantasia: Optional[str] = None
    CNAE: Optional[int] = None
    Tipo: Optional[int] = None
    CNPJCPF: Optional[int] = None
    Logradouro: Optional[str] = None
    Numero: Optional[str] = None
    Bairro: Optional[str] = None
    CEP: Optional[int] = None
    Cidade: Optional[str] = None
    Estado: Optional[str] = None
    Is_PessoaJuridico: Optional[bool] = None
    Is_PessoaFisico: Optional[bool] = None
    Telefone:Optional[int] = None
    Email: Optional[str] = None
    InscricaoEstadual: Optional[int] = None
    InscricaoMunicipal: Optional[int] = None
    ProdutosServicosFornecidos: Optional[str] = None
    InformacoesAdicionais: Optional[str] = None
    ativo: Optional[bool] = None
    
   
    class Config:
        from_attributes = True

class EmpresaCreate(EmpresaSchema):
    pass

class EmpresaResponse(EmpresaSchema):
    id: int



class SalvarDadosRecebimentoSchema(BaseModel):
    empresa_id: int
    chave_pix_padrao: Optional[str] = None
    qr_code_estatico_base64: Optional[str] = None
    pix_copia_e_cola_padrao: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = "Conta Corrente"
    titular: Optional[str] = None
    documento_titular: Optional[str] = None
    
class UnidadeSchema(BaseModel):
    slug: str
    nome_exibicao: str
    razosocial: str
    cnpj: str
    chave_pix: str
    banco: str
    agencia: str
    conta: str
    titular: str
    qr_code_base64: str = None
    logo_url: str = None