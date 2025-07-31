from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from app.database.bd import get_connection 
from app.models.models import Evento, EventoCreate, EventoUpdate

router = APIRouter()

@router.get("/", response_model=List[Evento])
async def listar_eventos():
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
    
    cur = conn.cursor()
    cur.execute("SELECT id_evento, titulo, data_evento, local, vagas, carga_horaria, categoria, id_organizador FROM evento")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [Evento(id_evento=r[0], titulo=r[1], data_evento=r[2], local=r[3], vagas=r[4], carga_horaria=r[5], categoria=r[6], id_organizador=r[7]) for r in rows]

@router.get("/{evento_id}", response_model=Evento)
async def get_evento(evento_id: int):
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
        
    cur = conn.cursor()
    cur.execute("SELECT id_evento, titulo, data_evento, local, vagas, carga_horaria, categoria, id_organizador FROM evento WHERE id_evento=%s", (evento_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return Evento(id_evento=row[0], titulo=row[1], data_evento=row[2], local=row[3], vagas=row[4], carga_horaria=row[5], categoria=row[6], id_organizador=row[7])
    
    raise HTTPException(status_code=404, detail="Evento não encontrado")

@router.post("/", response_model=Evento, status_code=status.HTTP_201_CREATED)
async def criar_evento(evento: EventoCreate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO evento (titulo, data_evento, local, vagas, carga_horaria, categoria, id_organizador) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (evento.titulo, evento.data_evento, evento.local, evento.vagas, evento.carga_horaria, evento.categoria, evento.id_organizador)
        )
        new_row = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar evento: {e}")
    finally:
        cur.close()
        conn.close()

    return Evento(id_evento=new_row[0], titulo=new_row[1], data_evento=new_row[2], local=new_row[3], vagas=new_row[4], carga_horaria=new_row[5], categoria=new_row[6], id_organizador=new_row[7])

@router.put("/{evento_id}", response_model=Evento)
async def atualizar_evento(evento_id: int, evento: EventoUpdate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    
    update_data = evento.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
        
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(evento_id)

    try:
        cur.execute(f"UPDATE evento SET {set_clause} WHERE id_evento = %s RETURNING *", tuple(values))
        updated_row = cur.fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar evento: {e}")
    finally:
        cur.close()
        conn.close()

    return Evento(id_evento=updated_row[0], titulo=updated_row[1], data_evento=updated_row[2], local=updated_row[3], vagas=updated_row[4], carga_horaria=updated_row[5], categoria=updated_row[6], id_organizador=updated_row[7])

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_evento(evento_id: int):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM evento WHERE id_evento=%s", (evento_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao deletar evento: {e}")
    finally:
        cur.close()
        conn.close()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
