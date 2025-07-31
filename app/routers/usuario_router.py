from fastapi import APIRouter, HTTPException, Depends, Response, status
from typing import List
from app.database.bd import get_connection 
from app.models.models import Usuario, UsuarioCreate, UsuarioUpdate

router = APIRouter()

@router.get("/", response_model=List[Usuario])
async def listar_usuarios():
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")
        
    cur = conn.cursor()
    cur.execute("SELECT id_usuario, nome, email, senha, tipo, matricula, curso FROM usuario")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [Usuario(id_usuario=r[0], nome=r[1], email=r[2], senha=r[3], tipo=r[4], matricula=r[5], curso=r[6]) for r in rows]

@router.get("/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: int):
    conn = get_connection(role='reader')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")

    cur = conn.cursor()
    cur.execute("SELECT id_usuario, nome, email, senha, tipo, matricula, curso FROM usuario WHERE id_usuario=%s", (usuario_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Usuario(id_usuario=row[0], nome=row[1], email=row[2], senha=row[3], tipo=row[4], matricula=row[5], curso=row[6])
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def criar_usuario(usuario: UsuarioCreate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuario (nome, email, senha, tipo, matricula, curso) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (usuario.nome, usuario.email, usuario.senha, usuario.tipo, usuario.matricula, usuario.curso)
        )
        new_row = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário: {e}")
    finally:
        cur.close()
        conn.close()
    
    return Usuario(id_usuario=new_row[0], nome=new_row[1], email=new_row[2], senha=new_row[3], tipo=new_row[4], matricula=new_row[5], curso=new_row[6])

@router.put("/{usuario_id}", response_model=Usuario)
async def atualizar_usuario(usuario_id: int, usuario: UsuarioUpdate):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")

    cur = conn.cursor()
    
    update_data = usuario.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
        
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(usuario_id)

    try:
        cur.execute(f"UPDATE usuario SET {set_clause} WHERE id_usuario = %s RETURNING *", tuple(values))
        updated_row = cur.fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar usuário: {e}")
    finally:
        cur.close()
        conn.close()

    return Usuario(id_usuario=updated_row[0], nome=updated_row[1], email=updated_row[2], senha=updated_row[3], tipo=updated_row[4], matricula=updated_row[5], curso=updated_row[6])

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(usuario_id: int):
    conn = get_connection(role='admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados para escrita.")
        
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM usuario WHERE id_usuario=%s", (usuario_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao deletar usuário: {e}")
    finally:
        cur.close()
        conn.close()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
