from pydantic import BaseModel, EmailStr
from typing import Optional

class UserAdminResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    score_confiabilidad: int
    plan: str
    
    class Config:
        from_attributes = True

class UserCreateAdmin(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    score_confiabilidad: Optional[int] = 100
    plan: Optional[str] = 'Gratuito'

class UserUpdateAdmin(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    score_confiabilidad: int
    plan: str
