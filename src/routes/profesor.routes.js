const express = require('express');
const router = express.Router();
const profesorController = require('../controllers/profesor.controller');

/**
 * @swagger
 * /api/professors:
 *   get:
 *     summary: Obtiene la lista de todos los profesores
 *     description: Retorna profesores que están aprobados y tienen perfil completado.
 *     tags: [Profesores]
 *     responses:
 *       200:
 *         description: Lista de profesores obtenida exitosamente
 */
// Obtener la lista de todos los profesores aprobados y con perfil completado
router.get('/', profesorController.getProfesores);

/**
 * @swagger
 * /api/professors/{id}/profile:
 *   put:
 *     summary: Actualiza el perfil de un profesor
 *     tags: [Profesores]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del profesor
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               tarifa_hora:
 *                 type: number
 *               biografia:
 *                 type: string
 *     responses:
 *       200:
 *         description: Perfil actualizado correctamente
 */
// Actualizar perfil del profesor
router.put('/:id/profile', profesorController.updateProfile);

module.exports = router;
