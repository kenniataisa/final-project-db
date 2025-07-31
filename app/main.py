from fastapi import FastAPI

from app.routers.usuario_router import router as usuario_router
from app.routers.evento_router import router as evento_router
from app.routers.inscricao_router import router as inscricao_router
from app.routers.certificado_router import router as certificado_router
from app.routers.horas_complementares_router import router as horas_complementares_router

app = FastAPI(
    title="API de Eventos Acadêmicos",
    description="API para gerenciar usuários, eventos, inscrições e certificados de um sistema acadêmico.",
    version="1.0"
)

app.include_router(usuario_router, prefix="/usuarios", tags=["Usuários"])
app.include_router(evento_router, prefix="/eventos", tags=["Eventos"])
app.include_router(inscricao_router, prefix="/inscricoes", tags=["Inscrições"])
app.include_router(certificado_router, prefix="/certificados", tags=["Certificados"])
app.include_router(horas_complementares_router, prefix="/horas_complementares", tags=["Horas Complementares"])