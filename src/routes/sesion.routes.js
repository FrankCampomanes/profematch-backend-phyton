const express = require('express');
const router = express.Router();
const sesionController = require('../controllers/sesion.controller');

// Crear una sesión nueva con validación de 90 minutos
router.post('/', sesionController.createSesion);

module.exports = router;
