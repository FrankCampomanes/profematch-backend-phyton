from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Text, JSON, DateTime, TIMESTAMP, func
from sqlalchemy.orm import relationship
from core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    rol = Column(Enum('admin', 'profesor', 'estudiante'), nullable=False)
    estado = Column(Enum('pendiente', 'aprobado', 'inactivo'), default='pendiente', nullable=False)
    score_confiabilidad = Column(Integer, default=100, nullable=False)
    plan = Column(String(50), default='Gratuito', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    perfil = relationship("ProfesorPerfil", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    sesiones_impartidas = relationship("Sesion", back_populates="profesor", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="estudiante", cascade="all, delete-orphan")
    resenas_dadas = relationship("Resena", foreign_keys="[Resena.estudiante_id]", back_populates="estudiante", cascade="all, delete-orphan")
    resenas_recibidas = relationship("Resena", foreign_keys="[Resena.profesor_id]", back_populates="profesor", cascade="all, delete-orphan")
    cursos = relationship("Curso", secondary="profesores_cursos", back_populates="profesores")
    advertencias_recibidas = relationship("Advertencia", foreign_keys="[Advertencia.profesor_id]", back_populates="profesor", cascade="all, delete-orphan")

class ProfesorPerfil(Base):
    __tablename__ = "profesores_perfiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    metodologia = Column(Text, nullable=True)
    reconocimientos = Column(JSON, nullable=True)
    horarios = Column(JSON, nullable=True)
    foto = Column(String(500), nullable=True)
    universidad = Column(String(255), nullable=True)
    perfil_completado = Column(Boolean, default=False, nullable=False)

    usuario = relationship("Usuario", back_populates="perfil")

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    categoria = Column(String(255), default='General')

    profesores = relationship("Usuario", secondary="profesores_cursos", back_populates="cursos")
    sesiones = relationship("Sesion", back_populates="curso", cascade="all, delete-orphan")

class ProfesorCurso(Base):
    __tablename__ = "profesores_cursos"

    profesor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), primary_key=True)

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime, nullable=False)
    tema = Column(String(255), default='General', nullable=False)
    precio = Column(Integer, default=10, nullable=False)
    cupos_maximos = Column(Integer, default=1, nullable=False)
    enlace_reunion = Column(String(500), nullable=True)
    estado = Column(Enum('Programada', 'En Curso', 'Finalizada', 'Cancelada'), default='Programada', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    profesor = relationship("Usuario", back_populates="sesiones_impartidas")
    curso = relationship("Curso", back_populates="sesiones")
    inscripciones = relationship("Inscripcion", back_populates="sesion", cascade="all, delete-orphan")
    resenas = relationship("Resena", back_populates="sesion", cascade="all, delete-orphan")

class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False)
    fecha_inscripcion = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    estado = Column(Enum('Confirmado', 'Cancelado'), default='Confirmado', nullable=False)

    estudiante = relationship("Usuario", back_populates="inscripciones")
    sesion = relationship("Sesion", back_populates="inscripciones")

class Resena(Base):
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    profesor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False)
    comentario = Column(Text, nullable=False)
    puntuaciones_json = Column(JSON, nullable=False)
    recomendaria = Column(Boolean, default=True, nullable=False)
    queja_formal = Column(Boolean, default=False, nullable=False)
    motivo_queja = Column(Text, nullable=True)
    respuesta_profesor = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    estudiante = relationship("Usuario", foreign_keys=[estudiante_id], back_populates="resenas_dadas")
    profesor = relationship("Usuario", foreign_keys=[profesor_id], back_populates="resenas_recibidas")
    sesion = relationship("Sesion", back_populates="resenas")

class Advertencia(Base):
    __tablename__ = "advertencias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    resena_id = Column(Integer, ForeignKey("resenas.id", ondelete="SET NULL"), nullable=True)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    profesor = relationship("Usuario", foreign_keys=[profesor_id], back_populates="advertencias_recibidas")
    admin = relationship("Usuario", foreign_keys=[admin_id])
