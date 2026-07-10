const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../config/db');

// Esta clave debería estar en un archivo .env en producción
const JWT_SECRET = process.env.JWT_SECRET || 'profematch_super_secreto_123';

const login = async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Faltan credenciales (email y password)' });
        }

        // 1. Buscar usuario por email
        const [rows] = await pool.query('SELECT * FROM usuarios WHERE email = ?', [email]);
        if (rows.length === 0) {
            return res.status(401).json({ error: 'Credenciales inválidas' });
        }

        const usuario = rows[0];

        // 2. Verificar estado de la cuenta
        if (usuario.estado === 'pendiente') {
            return res.status(403).json({ error: 'Cuenta pendiente de aprobación' });
        }
        if (usuario.estado === 'inactivo') {
            return res.status(403).json({ error: 'Cuenta inactiva o suspendida' });
        }

        // 3. Verificar contraseña
        if (!usuario.password_hash) {
            return res.status(401).json({ error: 'Credenciales inválidas' });
        }
        const isPasswordValid = await bcrypt.compare(password, usuario.password_hash);
        if (!isPasswordValid) {
            return res.status(401).json({ error: 'Credenciales inválidas' });
        }

        // 4. Si es profesor, traemos su perfil completado y sus cursos
        let perfilProfesor = {};
        let cursosProfesor = [];
        if (usuario.rol === 'profesor') {
            const [perfilRows] = await pool.query('SELECT universidad, perfil_completado FROM profesores_perfiles WHERE usuario_id = ?', [usuario.id]);
            if (perfilRows.length > 0) {
                perfilProfesor = {
                    universidad: perfilRows[0].universidad,
                    perfil_completado: perfilRows[0].perfil_completado === 1
                };
            }
            const [cursosRows] = await pool.query(
                `SELECT c.id, c.nombre FROM profesores_cursos pc 
                 JOIN cursos c ON pc.curso_id = c.id 
                 WHERE pc.profesor_id = ?`, 
                [usuario.id]
            );
            cursosProfesor = cursosRows.map(c => ({ id: c.id, nombre: c.nombre }));
        }

        // 5. Generar JWT (Token)
        const token = jwt.sign(
            { id: usuario.id, email: usuario.email, rol: usuario.rol },
            JWT_SECRET,
            { expiresIn: '24h' }
        );

        // 6. Devolver datos al frontend
        res.json({
            token,
            user: {
                id: usuario.id,
                nombre: usuario.nombre,
                email: usuario.email,
                rol: usuario.rol,
                estado: usuario.estado,
                ...(usuario.rol === 'profesor' ? {
                    universidad: perfilProfesor.universidad,
                    perfil_completado: perfilProfesor.perfil_completado,
                    cursos: cursosProfesor
                } : {})
            }
        });

    } catch (error) {
        console.error('Error en el login:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

const register = async (req, res) => {
    try {
        const { nombre, email, password, rol, universidad } = req.body;

        if (!nombre || !email || !password || !rol) {
            return res.status(400).json({ error: 'Todos los campos básicos son obligatorios' });
        }

        if (rol !== 'estudiante' && rol !== 'profesor') {
            return res.status(400).json({ error: 'Rol inválido' });
        }

        // 1. Verificar si el email ya existe
        const [existing] = await pool.query('SELECT id FROM usuarios WHERE email = ?', [email]);
        if (existing.length > 0) {
            return res.status(400).json({ error: 'El correo ya está registrado' });
        }

        // 2. Hashear password
        const password_hash = await bcrypt.hash(password, 10);

        // 3. Crear el usuario (estado pendiente por defecto según reglas de negocio)
        const [result] = await pool.query(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES (?, ?, ?, ?, 'pendiente')",
            [nombre, email, password_hash, rol]
        );
        const nuevoUsuarioId = result.insertId;

        // 4. Si es profesor, crear su perfil vacío con la universidad y perfil_completado = false
        if (rol === 'profesor') {
            await pool.query(
                "INSERT INTO profesores_perfiles (usuario_id, universidad, perfil_completado, reconocimientos, horarios) VALUES (?, ?, false, '[]', '{}')",
                [nuevoUsuarioId, universidad || null]
            );
        }

        res.status(201).json({
            message: 'Usuario registrado exitosamente. Esperando aprobación del administrador.',
            user: {
                id: nuevoUsuarioId,
                nombre,
                email,
                rol,
                estado: 'pendiente'
            }
        });
    } catch (error) {
        console.error('Error en el registro:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = {
    login,
    register
};
