from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from app.database.bd import get_connection 
from app.models.models import HorasComplementares, HorasComplementaresCreate, HorasComplementaresUpdate

router = APIRouter()

@router.get("/", response_model=List[HorasComplementares])
async def listar_horas():
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
    
    cur = conn.cursor()
    cur.execute("SELECT id_horas, id_usuario, id_evento, horas_concedidas, data_lancamento, status FROM horas_complementares")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [HorasComplementares(id_horas=r[0], id_usuario=r[1], id_evento=r[2], horas_concedidas=r[3], data_lancamento=r[4], status=r[5]) for r in rows]

@router.get("/{horas_id}", response_model=HorasComplementares)
async def get_horas(horas_id: int):
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")

    cur = conn.cursor()
    cur.execute("SELECT id_horas, id_usuario, id_evento, horas_concedidas, data_lancamento, status FROM horas_complementares WHERE id_horas=%s", (horas_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return HorasComplementares(id_horas=row[0], id_usuario=row[1], id_evento=row[2], horas_concedidas=row[3], data_lancamento=row[4], status=row[5])
    raise HTTPException(status_code=404, detail="Registro de horas não encontrado")

@router.post("/", response_model=HorasComplementares, status_code=status.HTTP_201_CREATED)
async def criar_horas(horas: HorasComplementaresCreate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO horas_complementares (id_usuario, id_evento, horas_concedidas, status) VALUES (%s, %s, %s, %s) RETURNING *",
            (horas.id_usuario, horas.id_evento, horas.horas_concedidas, horas.status)
        )
        new_row = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar registro de horas: {e}")
    finally:
        cur.close()
        conn.close()
    
    return HorasComplementares(id_horas=new_row[0], id_usuario=new_row[1], id_evento=new_row[2], horas_concedidas=new_row[3], data_lancamento=new_row[4], status=new_row[5])

@router.put("/{horas_id}", response_model=HorasComplementares)
async def atualizar_horas(horas_id: int, horas: HorasComplementaresUpdate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    
    update_data = horas.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
        
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(horas_id)

    try:
        cur.execute(f"UPDATE horas_complementares SET {set_clause} WHERE id_horas = %s RETURNING *", tuple(values))
        updated_row = cur.fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail="Registro de horas não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar registro de horas: {e}")
    finally:
        cur.close()
        conn.close()

    return HorasComplementares(id_horas=updated_row[0], id_usuario=updated_row[1], id_evento=updated_row[2], horas_concedidas=updated_row[3], data_lancamento=updated_row[4], status=updated_row[5])


@router.delete("/{horas_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_horas(horas_id: int):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM horas_complementares WHERE id_horas=%s", (horas_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de horas não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao deletar registro de horas: {e}")
    finally:
        cur.close()
        conn.close()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
