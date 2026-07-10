const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');

// Ruta para hacer Login: POST /api/auth/login
router.post('/login', authController.login);

// Ruta para Registrarse: POST /api/auth/register
router.post('/register', authController.register);

module.exports = router;
