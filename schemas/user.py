from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class CursoBase(BaseModel):
    id: int
    nombre: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72, description="Contraseña demasiado larga (máx 72)")

class UserRegister(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(..., max_length=72, description="Contraseña demasiado larga (máx 72)")
    rol: str
    universidad: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    estado: str
    universidad: Optional[str] = None
    perfil_completado: Optional[bool] = None
    cursos: Optional[List[CursoBase]] = None
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    token: str
    user: UserResponse
