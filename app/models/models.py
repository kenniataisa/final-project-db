from pydantic import BaseModel
from typing import Optional
from datetime import date

class Usuario(BaseModel):
    id_usuario: int
    nome: str
    email: str
    senha: str
    tipo: str
    matricula: Optional[str] = None
    curso: Optional[str] = None

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    tipo: str
    matricula: Optional[str] = None
    curso: Optional[str] = None

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    tipo: Optional[str] = None
    matricula: Optional[str] = None
    curso: Optional[str] = None

class Evento(BaseModel):
    id_evento: int
    titulo: str
    data_evento: date
    local: str
    vagas: int
    carga_horaria: int
    categoria: str
    id_organizador: int

class EventoCreate(BaseModel):
    titulo: str
    data_evento: date
    local: str
    vagas: int
    carga_horaria: int
    categoria: str
    id_organizador: int

class EventoUpdate(BaseModel):
    titulo: Optional[str] = None
    data_evento: Optional[date] = None
    local: Optional[str] = None
    vagas: Optional[int] = None
    carga_horaria: Optional[int] = None
    categoria: Optional[str] = None
    id_organizador: Optional[int] = None

class Inscricao(BaseModel):
    id_inscricao: int
    id_usuario: int
    id_evento: int
    data_inscricao: date
    presente: bool = False

class InscricaoCreate(BaseModel):
    id_usuario: int
    id_evento: int

class InscricaoUpdate(BaseModel):
    presente: Optional[bool] = None

class Certificado(BaseModel):
    id_certificado: int
    id_inscricao: int
    codigo_verificacao: str
    data_emissao: date

class CertificadoCreate(BaseModel):
    id_inscricao: int
    codigo_verificacao: str

class HorasComplementares(BaseModel):
    id_horas: int
    id_usuario: int
    id_evento: int
    horas_concedidas: float
    data_lancamento: date
    status: str

class HorasComplementaresCreate(BaseModel):
    id_usuario: int
    id_evento: int
    horas_concedidas: float
    status: str

class HorasComplementaresUpdate(BaseModel):
    horas_concedidas: Optional[float] = None
    status: Optional[str] = None