const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: Inicia sesión de usuario (Alumno o Profesor)
 *     tags: [Auth]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *                 example: usuario@ejemplo.com
 *               password:
 *                 type: string
 *                 example: password123
 *     responses:
 *       200:
 *         description: Login exitoso y devuelve token JWT
 *       401:
 *         description: Credenciales incorrectas
 */
// Ruta para hacer Login: POST /api/auth/login
router.post('/login', authController.login);

/**
 * @swagger
 * /api/auth/register:
 *   post:
 *     summary: Registra un nuevo usuario
 *     tags: [Auth]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 *               rol_id:
 *                 type: integer
 *                 description: 1 para Administrador, 2 para Profesor, 3 para Alumno
 *     responses:
 *       201:
 *         description: Usuario registrado exitosamente
 */
// Ruta para Registrarse: POST /api/auth/register
router.post('/register', authController.register);

module.exports = router;
