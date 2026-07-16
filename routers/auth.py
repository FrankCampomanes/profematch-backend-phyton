from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token
from models.all_models import Usuario, ProfesorPerfil, Curso, ProfesorCurso
from schemas.user import UserLogin, UserRegister, LoginResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
    if usuario.estado == 'pendiente':
        raise HTTPException(status_code=403, detail="Cuenta pendiente de aprobación")
    if usuario.estado == 'inactivo':
        raise HTTPException(status_code=403, detail="Cuenta inactiva o suspendida")
        
    if len(login_data.password) > 72:
        raise HTTPException(status_code=400, detail="Contraseña demasiado larga (máx 72 caracteres)")
    if not usuario.password_hash or not verify_password(login_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
    universidad = None
    perfil_completado = None
    cursos_lista = []
    
    if usuario.rol == 'profesor' and getattr(usuario, 'perfil', None):
        universidad = usuario.perfil.universidad
        perfil_completado = usuario.perfil.perfil_completado
        cursos_lista = [{"id": c.id, "nombre": c.nombre} for c in getattr(usuario, 'cursos', [])]
    else:
        universidad = None
        perfil_completado = None
        cursos_lista = []
    token_data = {"id": usuario.id, "email": usuario.email, "rol": usuario.rol}
    token = create_access_token(subject=str(usuario.id), extra_data=token_data)
    
    user_resp = UserResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        rol=usuario.rol,
        estado=usuario.estado,
        universidad=universidad,
        perfil_completado=perfil_completado,
        cursos=cursos_lista if usuario.rol == 'profesor' else None
    )
    
    return LoginResponse(token=token, user=user_resp)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if user_data.rol not in ['estudiante', 'profesor']:
        raise HTTPException(status_code=400, detail="Rol inválido")
        
    existing = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
    hashed_password = get_password_hash(user_data.password)
    
    nuevo_usuario = Usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        password_hash=hashed_password,
        rol=user_data.rol,
        estado='pendiente'
    )
    db.add(nuevo_usuario)
    db.flush() 
    
    if user_data.rol == 'profesor':
        nuevo_perfil = ProfesorPerfil(
            usuario_id=nuevo_usuario.id,
            universidad=user_data.universidad,
            perfil_completado=False,
            reconocimientos=[],
            horarios={}
        )
        db.add(nuevo_perfil)
        
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {
        "message": "Usuario registrado exitosamente. Esperando aprobación del administrador.",
        "user": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol,
            "estado": nuevo_usuario.estado
        }
    }
