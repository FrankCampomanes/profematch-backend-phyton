from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.all_models import Usuario, ProfesorPerfil
from schemas.admin import UserAdminResponse, UserCreateAdmin, UserUpdateAdmin
from core.security import get_password_hash
from typing import List

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios (Admin)"])

@router.get("/", response_model=List[UserAdminResponse])
def get_activos(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.estado == 'aprobado').all()
    return usuarios

@router.get("/papelera", response_model=List[UserAdminResponse])
def get_papelera(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.estado == 'inactivo').all()
    return usuarios

@router.get("/pendientes", response_model=List[UserAdminResponse])
def get_pendientes(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.estado == 'pendiente').all()
    return usuarios

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateAdmin, db: Session = Depends(get_db)):
    existing = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
    password_hash = get_password_hash('temp123')
    
    nuevo = Usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        password_hash=password_hash,
        rol=user_data.rol,
        estado='aprobado',
        score_confiabilidad=user_data.score_confiabilidad,
        plan=user_data.plan
    )
    db.add(nuevo)
    db.flush()
    
    if user_data.rol == 'profesor':
        nuevo_perfil = ProfesorPerfil(
            usuario_id=nuevo.id,
            perfil_completado=False,
            reconocimientos=[],
            horarios={}
        )
        db.add(nuevo_perfil)
        
    db.commit()
    return {"message": "Usuario creado exitosamente con contraseña temporal temp123"}

@router.put("/{id}")
def update_user(id: int, user_data: UserUpdateAdmin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user.nombre = user_data.nombre
    user.email = user_data.email
    user.rol = user_data.rol
    user.score_confiabilidad = user_data.score_confiabilidad
    user.plan = user_data.plan
    db.commit()
    
    return {"message": "Usuario actualizado exitosamente"}

@router.put("/bloquear/{id}")
def bloquear_user(id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.estado = 'inactivo'
    db.commit()
    return {"message": "Usuario inhabilitado exitosamente"}

@router.put("/restaurar/{id}")
def restaurar_user(id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.estado = 'aprobado'
    db.commit()
    return {"message": "Usuario restaurado exitosamente"}

@router.put("/aprobar/{id}")
def aprobar_user(id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.estado = 'aprobado'
    db.commit()
    return {"message": "Solicitud aprobada exitosamente"}
