const express = require('express');
const router = express.Router();
const usuarioController = require('../controllers/usuario.controller');

// GET endpoints
router.get('/', usuarioController.getActivos);
router.get('/papelera', usuarioController.getPapelera);
router.get('/pendientes', usuarioController.getPendientes);

// POST & PUT endpoints para CRUD manual
router.post('/', usuarioController.createUser);
router.put('/:id', usuarioController.updateUser);

// PUT endpoints para cambios de estado
router.put('/bloquear/:id', usuarioController.bloquearUser);
router.put('/restaurar/:id', usuarioController.restaurarUser);
router.put('/aprobar/:id', usuarioController.aprobarUser);

module.exports = router;
