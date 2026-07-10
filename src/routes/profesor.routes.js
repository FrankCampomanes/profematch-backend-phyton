const express = require('express');
const router = express.Router();
const profesorController = require('../controllers/profesor.controller');

// Obtener la lista de todos los profesores aprobados y con perfil completado
router.get('/', profesorController.getProfesores);

// Actualizar perfil del profesor
router.put('/:id/profile', profesorController.updateProfile);

module.exports = router;
