const bcrypt = require('bcrypt');
const pool = require('../config/db');

// Obtener Usuarios Activos (Aprobados)
const getActivos = async (req, res) => {
    try {
        const [rows] = await pool.query(
            "SELECT id, nombre, email, rol, score_confiabilidad, plan FROM usuarios WHERE estado = 'aprobado'"
        );
        res.json(rows);
    } catch (error) {
        console.error('Error al obtener usuarios activos:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Obtener Usuarios en Papelera (Bloqueados/Inactivos)
const getPapelera = async (req, res) => {
    try {
        const [rows] = await pool.query(
            "SELECT id, nombre, email, rol, score_confiabilidad, plan FROM usuarios WHERE estado = 'inactivo'"
        );
        res.json(rows);
    } catch (error) {
        console.error('Error al obtener papelera:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Obtener Solicitudes Pendientes
const getPendientes = async (req, res) => {
    try {
        const [rows] = await pool.query(
            "SELECT id, nombre, email, rol, score_confiabilidad, plan FROM usuarios WHERE estado = 'pendiente'"
        );
        res.json(rows);
    } catch (error) {
        console.error('Error al obtener solicitudes pendientes:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Crear Usuario Manual (Admin)
const createUser = async (req, res) => {
    try {
        const { nombre, email, rol, score_confiabilidad, plan } = req.body;

        if (!nombre || !email || !rol) {
            return res.status(400).json({ error: 'Nombre, email y rol son obligatorios' });
        }

        const [existing] = await pool.query('SELECT id FROM usuarios WHERE email = ?', [email]);
        if (existing.length > 0) {
            return res.status(400).json({ error: 'El correo ya está registrado' });
        }

        // Asignamos una contraseña por defecto
        const password_hash = await bcrypt.hash('temp123', 10);
        
        // Estado por defecto aprobado ya que lo crea un Admin
        const [result] = await pool.query(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, estado, score_confiabilidad, plan) VALUES (?, ?, ?, ?, 'aprobado', ?, ?)",
            [nombre, email, password_hash, rol, score_confiabilidad || 100, plan || 'Gratuito']
        );
        
        const nuevoId = result.insertId;

        if (rol === 'profesor') {
            await pool.query(
                "INSERT INTO profesores_perfiles (usuario_id, perfil_completado, reconocimientos, horarios) VALUES (?, false, '[]', '{}')",
                [nuevoId]
            );
        }

        res.status(201).json({ message: 'Usuario creado exitosamente con contraseña temporal temp123' });
    } catch (error) {
        console.error('Error al crear usuario:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Actualizar Usuario Manual (Admin)
const updateUser = async (req, res) => {
    try {
        const { id } = req.params;
        const { nombre, email, rol, score_confiabilidad, plan } = req.body;

        await pool.query(
            "UPDATE usuarios SET nombre = ?, email = ?, rol = ?, score_confiabilidad = ?, plan = ? WHERE id = ?",
            [nombre, email, rol, score_confiabilidad, plan, id]
        );

        res.json({ message: 'Usuario actualizado exitosamente' });
    } catch (error) {
        console.error('Error al actualizar usuario:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Inhabilitar Usuario (Mover a Papelera)
const bloquearUser = async (req, res) => {
    try {
        const { id } = req.params;
        await pool.query("UPDATE usuarios SET estado = 'inactivo' WHERE id = ?", [id]);
        res.json({ message: 'Usuario inhabilitado exitosamente' });
    } catch (error) {
        console.error('Error al inhabilitar usuario:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Restaurar Usuario (Desde Papelera)
const restaurarUser = async (req, res) => {
    try {
        const { id } = req.params;
        await pool.query("UPDATE usuarios SET estado = 'aprobado' WHERE id = ?", [id]);
        res.json({ message: 'Usuario restaurado exitosamente' });
    } catch (error) {
        console.error('Error al restaurar usuario:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Aprobar Solicitud Pendiente
const aprobarUser = async (req, res) => {
    try {
        const { id } = req.params;
        await pool.query("UPDATE usuarios SET estado = 'aprobado' WHERE id = ?", [id]);
        res.json({ message: 'Solicitud aprobada exitosamente' });
    } catch (error) {
        console.error('Error al aprobar solicitud:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = {
    getActivos,
    getPapelera,
    getPendientes,
    createUser,
    updateUser,
    bloquearUser,
    restaurarUser,
    aprobarUser
};
