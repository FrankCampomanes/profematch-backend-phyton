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
        const isPasswordValid = await bcrypt.compare(password, usuario.password_hash);
        if (!isPasswordValid) {
            return res.status(401).json({ error: 'Credenciales inválidas' });
        }

        // 4. Generar JWT (Token)
        const token = jwt.sign(
            { id: usuario.id, email: usuario.email, rol: usuario.rol },
            JWT_SECRET,
            { expiresIn: '24h' }
        );

        // 5. Devolver datos al frontend (SIN el password_hash)
        res.json({
            token,
            user: {
                id: usuario.id,
                nombre: usuario.nombre,
                email: usuario.email,
                rol: usuario.rol,
                estado: usuario.estado
            }
        });

    } catch (error) {
        console.error('Error en el login:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = {
    login
};
