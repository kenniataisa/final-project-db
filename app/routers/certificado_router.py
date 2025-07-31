from fastapi import APIRouter, HTTPException
from typing import List
from app.database.bd import get_connection 
from app.models.models import Certificado, CertificadoCreate

router = APIRouter()

@router.get("/certificados", response_model=List[Certificado])
async def listar_certificados():
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
    
    cur = conn.cursor()
    cur.execute("SELECT id_certificado, id_inscricao, codigo_verificacao, data_emissao FROM certificado")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [Certificado(id_certificado=r[0], id_inscricao=r[1], codigo_verificacao=r[2], data_emissao=r[3]) for r in rows]

@router.get("/certificado/{certificado_id}", response_model=Certificado)
async def get_certificado(certificado_id: int):
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
        
    cur = conn.cursor()
    cur.execute("SELECT id_certificado, id_inscricao, codigo_verificacao, data_emissao FROM certificado WHERE id_certificado=%s", (certificado_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return Certificado(id_certificado=row[0], id_inscricao=row[1], codigo_verificacao=row[2], data_emissao=row[3])
    
    raise HTTPException(status_code=404, detail="Certificado não encontrado")

@router.post("/certificado")
async def criar_certificado(certificado: CertificadoCreate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO certificado (id_inscricao, codigo_verificacao) VALUES (%s, %s)",
            (certificado.id_inscricao, certificado.codigo_verificacao)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar certificado: {e}")
    finally:
        cur.close()
        conn.close()
        
    return {"msg": "Certificado criado com sucesso"}

@router.delete("/certificado/{certificado_id}")
async def deletar_certificado(certificado_id: int):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    
    cur.execute("SELECT id_certificado FROM certificado WHERE id_certificado=%s", (certificado_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Certificado não encontrado para deletar")
    
    try:
        cur.execute("DELETE FROM certificado WHERE id_certificado=%s", (certificado_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar certificado: {e}")
    finally:
        cur.close()
        conn.close()
        
    return {"msg": "Certificado removido com sucesso"}
