from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from app.database.bd import get_connection 
from app.models.models import Inscricao, InscricaoCreate, InscricaoUpdate

router = APIRouter()

@router.get("/", response_model=List[Inscricao])
async def listar_inscricoes():
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
    
    cur = conn.cursor()
    cur.execute("SELECT id_inscricao, id_usuario, id_evento, data_inscricao, presente FROM inscricao")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [Inscricao(id_inscricao=r[0], id_usuario=r[1], id_evento=r[2], data_inscricao=r[3], presente=r[4]) for r in rows]

@router.get("/{inscricao_id}", response_model=Inscricao)
async def get_inscricao(inscricao_id: int):
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")

    cur = conn.cursor()
    cur.execute("SELECT id_inscricao, id_usuario, id_evento, data_inscricao, presente FROM inscricao WHERE id_inscricao=%s", (inscricao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Inscricao(id_inscricao=row[0], id_usuario=row[1], id_evento=row[2], data_inscricao=row[3], presente=row[4])
    raise HTTPException(status_code=404, detail="Inscrição não encontrada")

@router.post("/", response_model=Inscricao, status_code=status.HTTP_201_CREATED)
async def criar_inscricao(inscricao: InscricaoCreate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO inscricao (id_usuario, id_evento) VALUES (%s, %s) RETURNING *",
            (inscricao.id_usuario, inscricao.id_evento)
        )
        new_row = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="Usuário já inscrito neste evento.")
        raise HTTPException(status_code=400, detail=f"Erro ao criar inscrição: {e}")
    finally:
        cur.close()
        conn.close()
    
    return Inscricao(id_inscricao=new_row[0], id_usuario=new_row[1], id_evento=new_row[2], data_inscricao=new_row[3], presente=new_row[4])

@router.put("/{inscricao_id}", response_model=Inscricao)
async def atualizar_inscricao(inscricao_id: int, inscricao: InscricaoUpdate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    
    update_data = inscricao.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
        
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(inscricao_id)

    try:
        cur.execute(f"UPDATE inscricao SET {set_clause} WHERE id_inscricao = %s RETURNING *", tuple(values))
        updated_row = cur.fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar inscrição: {e}")
    finally:
        cur.close()
        conn.close()

    return Inscricao(id_inscricao=updated_row[0], id_usuario=updated_row[1], id_evento=updated_row[2], data_inscricao=updated_row[3], presente=updated_row[4])

@router.delete("/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_inscricao(inscricao_id: int):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM inscricao WHERE id_inscricao=%s", (inscricao_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao deletar inscrição: {e}")
    finally:
        cur.close()
        conn.close()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
