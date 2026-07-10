const pool = require('../config/db');

// Obtener todos los profesores (para listar en tarjetas)
const getProfesores = async (req, res) => {
    try {
        const query = `
            SELECT 
                u.id, 
                u.nombre, 
                u.email,
                p.descripcion, 
                p.metodologia, 
                p.foto, 
                p.reconocimientos, 
                p.horarios,
                p.universidad,
                p.perfil_completado,
                GROUP_CONCAT(DISTINCT c.nombre) as cursos_impartidos,
                COUNT(DISTINCT i.estudiante_id) as estudiantes_atendidos
            FROM usuarios u
            JOIN profesores_perfiles p ON u.id = p.usuario_id
            LEFT JOIN profesores_cursos pc ON u.id = pc.profesor_id
            LEFT JOIN cursos c ON pc.curso_id = c.id
            LEFT JOIN sesiones s ON u.id = s.profesor_id AND s.estado = 'Finalizada'
            LEFT JOIN inscripciones i ON s.id = i.sesion_id AND i.estado = 'Confirmado'
            WHERE u.rol = 'profesor' AND u.estado = 'aprobado' AND p.perfil_completado = true
            GROUP BY u.id
        `;

        const [rows] = await pool.query(query);

        const profesores = [];

        for (const row of rows) {
            // Obtener reseñas reales para cada profesor
            const [resenasRows] = await pool.query(
                `SELECT r.comentario, r.puntuaciones_json, r.created_at, u.nombre as estudiante_nombre 
                 FROM resenas r 
                 JOIN usuarios u ON r.estudiante_id = u.id 
                 WHERE r.profesor_id = ?`,
                [row.id]
            );

            let puntuaciones = [];
            const listaResenas = resenasRows.map(r => {
                let p_json = {};
                try { p_json = JSON.parse(r.puntuaciones_json); } catch (e) { }
                puntuaciones.push(p_json);
                return {
                    estudiante: r.estudiante_nombre,
                    comentario: r.comentario,
                    fecha: r.created_at,
                    puntuaciones: p_json
                };
            });

            // Calculamos el promedio del gráfico de araña
            const criterios = { Claridad: 0, Dominio: 0, Puntualidad: 0, Profesionalismo: 0, Exigencia: 0, Disponibilidad: 0 };

            if (puntuaciones.length > 0) {
                puntuaciones.forEach(p => {
                    criterios.Claridad += p.Claridad || 0;
                    criterios.Dominio += p.Dominio || 0;
                    criterios.Puntualidad += p.Puntualidad || 0;
                    criterios.Profesionalismo += p.Profesionalismo || 0;
                    criterios.Exigencia += p.Exigencia || 0;
                    criterios.Disponibilidad += p.Disponibilidad || 0;
                });

                Object.keys(criterios).forEach(key => {
                    criterios[key] = parseFloat((criterios[key] / puntuaciones.length).toFixed(1));
                });
            }

            // Calculamos el "rating" global (Tasa de Aprobación base)
            let ratingGlobal = 0;
            let tasaAprobacion = "N/A";
            if (puntuaciones.length > 0) {
                const totalSuma = Object.values(criterios).reduce((a, b) => a + b, 0);
                ratingGlobal = parseFloat((totalSuma / 6).toFixed(1));
                // Convertir rating 1-5 a porcentaje (ej. 4.5 -> 90%)
                tasaAprobacion = `${Math.round((ratingGlobal / 5) * 100)}%`;
            }

            profesores.push({
                id: row.id,
                nombre: row.nombre,
                email: row.email,
                descripcion: row.descripcion,
                metodologia: row.metodologia,
                universidad: row.universidad,
                foto: row.foto,
                perfil_completado: row.perfil_completado === 1,
                reconocimientos: JSON.parse(row.reconocimientos || '[]'),
                horarios: JSON.parse(row.horarios || '{}'),
                cursos: row.cursos_impartidos ? row.cursos_impartidos.split(',') : [],
                rating: ratingGlobal,
                criteriosEvaluacion: criterios,
                resenas: listaResenas, // <-- Añadido para el frontend
                metricas: {
                    estudiantesAtendidos: row.estudiantes_atendidos || 0,
                    tasaAprobacion: tasaAprobacion, // <-- Añadido
                    tiempoRespuesta: "N/A"
                }
            });
        }

        res.json(profesores);
    } catch (error) {
        console.error('Error al obtener profesores:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Actualizar el perfil del profesor
const updateProfile = async (req, res) => {
    try {
        const { id } = req.params;
        const { descripcion, metodologia, reconocimientos, horarios, cursos } = req.body;

        await pool.query(
            `UPDATE profesores_perfiles 
             SET descripcion = ?, metodologia = ?, reconocimientos = ?, horarios = ?, perfil_completado = true
             WHERE usuario_id = ?`,
            [
                descripcion,
                metodologia,
                JSON.stringify(reconocimientos || []),
                JSON.stringify(horarios || {}),
                id
            ]
        );

        await pool.query('DELETE FROM profesores_cursos WHERE profesor_id = ?', [id]);

        if (cursos && cursos.length > 0) {
            for (const nombreCurso of cursos) {
                const [cursoRows] = await pool.query('SELECT id FROM cursos WHERE nombre = ?', [nombreCurso]);
                if (cursoRows.length > 0) {
                    await pool.query('INSERT INTO profesores_cursos (profesor_id, curso_id) VALUES (?, ?)', [id, cursoRows[0].id]);
                }
            }
        }

        res.json({ message: 'Perfil actualizado exitosamente' });
    } catch (error) {
        console.error('Error al actualizar perfil:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = {
    getProfesores,
    updateProfile
};
