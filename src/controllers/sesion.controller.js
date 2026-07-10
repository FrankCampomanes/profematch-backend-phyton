const pool = require('../config/db');

// Crear una nueva sesión
const createSesion = async (req, res) => {
    try {
        const { profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, cupos_maximos } = req.body;

        if (!profesor_id || !curso_id || !fecha_hora_inicio || !fecha_hora_fin) {
            return res.status(400).json({ error: 'Faltan datos requeridos (profesor_id, curso_id, fechas)' });
        }

        const inicio = new Date(fecha_hora_inicio);
        const fin = new Date(fecha_hora_fin);

        // Validar que las fechas sean válidas
        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
            return res.status(400).json({ error: 'Formato de fecha inválido' });
        }

        // --- DOBLE VALIDACIÓN: Regla de los 90 minutos ---
        const diferenciaMs = fin - inicio;
        const diferenciaMinutos = Math.floor(diferenciaMs / 60000);

        if (diferenciaMinutos < 90) {
            return res.status(400).json({ 
                error: 'Regla de negocio no cumplida: La sesión debe tener una duración mínima de 90 minutos (1.5 horas).' 
            });
        }
        // ------------------------------------------------

        // Si pasa la validación, insertamos en BD
        const [result] = await pool.query(
            `INSERT INTO sesiones (profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, cupos_maximos, estado) 
             VALUES (?, ?, ?, ?, ?, 'Programada')`,
            [profesor_id, curso_id, inicio, fin, cupos_maximos || 1]
        );

        res.status(201).json({ 
            message: 'Sesión creada exitosamente',
            sesion_id: result.insertId
        });

    } catch (error) {
        console.error('Error al crear la sesión:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = {
    createSesion
};
