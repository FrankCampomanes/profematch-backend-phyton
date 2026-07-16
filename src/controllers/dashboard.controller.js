const pool = require('../config/db');

// Calcula un rango de fechas: primer y último día del mes actual
const getRangoMesActual = () => {
    const ahora = new Date();
    const inicio = new Date(ahora.getFullYear(), ahora.getMonth(), 1);
    const fin = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0, 23, 59, 59);
    return { inicio, fin };
};

const getAdminDashboard = async (req, res) => {
    try {
        const { inicio, fin } = getRangoMesActual();
        const PRECIO_SUSCRIPCION = 9.99;
        const TASA_COMISION = 0.15;

        // 1) Comisiones del mes: 15% de las sesiones finalizadas del mes actual
        const [comisionesRows] = await pool.query(
            `SELECT COALESCE(SUM(precio), 0) AS totalBruto
             FROM sesiones
             WHERE estado = 'Finalizada' AND fecha_hora_inicio BETWEEN ? AND ?`,
            [inicio, fin]
        );
        const comisiones = Number(comisionesRows[0].totalBruto) * TASA_COMISION;

        // 2) Suscripciones premium activas
        const [suscripcionesRows] = await pool.query(
            "SELECT COUNT(*) AS total FROM usuarios WHERE plan = 'Premium' AND estado = 'aprobado'"
        );
        const suscripciones = suscripcionesRows[0].total * PRECIO_SUSCRIPCION;

        // 3) Usuarios en riesgo (score crítico)
        const [riesgoRows] = await pool.query(
            "SELECT COUNT(*) AS total FROM usuarios WHERE score_confiabilidad <= 49 AND estado = 'aprobado'"
        );

        // 4) Quejas pendientes
        const [quejasRows] = await pool.query(
            "SELECT COUNT(*) AS total FROM quejas WHERE estado = 'Pendiente'"
        );

        // 5) Ingresos semanales (últimas 4 semanas, comisión 15% por semana)
        const [semanalRows] = await pool.query(
            `SELECT YEARWEEK(fecha_hora_inicio, 1) AS semana, SUM(precio) * ? AS ingreso
             FROM sesiones
             WHERE estado = 'Finalizada' AND fecha_hora_inicio >= DATE_SUB(NOW(), INTERVAL 4 WEEK)
             GROUP BY semana
             ORDER BY semana ASC`,
            [TASA_COMISION]
        );
        const ingresosSemanales = semanalRows.map(r => Number(r.ingreso));
        while (ingresosSemanales.length < 4) ingresosSemanales.unshift(0);

        // 6) Salud de comunidad: distribución de score_confiabilidad
        const [distribucionRows] = await pool.query(
            `SELECT
                SUM(CASE WHEN score_confiabilidad BETWEEN 90 AND 100 THEN 1 ELSE 0 END) AS excelente,
                SUM(CASE WHEN score_confiabilidad BETWEEN 70 AND 89 THEN 1 ELSE 0 END) AS bueno,
                SUM(CASE WHEN score_confiabilidad BETWEEN 50 AND 69 THEN 1 ELSE 0 END) AS regular,
                SUM(CASE WHEN score_confiabilidad BETWEEN 0 AND 49 THEN 1 ELSE 0 END) AS critico,
                COUNT(*) AS total
             FROM usuarios WHERE estado = 'aprobado'`
        );
        const d = distribucionRows[0];
        const total = d.total || 1;
        const distribucion = {
            excelente: Math.round((d.excelente / total) * 100),
            bueno: Math.round((d.bueno / total) * 100),
            regular: Math.round((d.regular / total) * 100),
            critico: Math.round((d.critico / total) * 100)
        };

        // 7) Historial de auditoría (quejas no resueltas, con nombres)
        const [historialRows] = await pool.query(
            `SELECT q.id, DATE_FORMAT(q.created_at, '%Y-%m-%d') AS fecha,
                    COALESCE(rep.nombre, 'Sistema') AS reportado,
                    acu.nombre AS acusado,
                    q.tipo, q.gravedad, q.estado
             FROM quejas q
             LEFT JOIN usuarios rep ON rep.id = q.reportante_id
             JOIN usuarios acu ON acu.id = q.acusado_id
             WHERE q.estado != 'Resuelto'
             ORDER BY q.created_at DESC`
        );

        res.json({
            finanzas: {
                comisiones: Number(comisiones.toFixed(2)),
                suscripciones: Number(suscripciones.toFixed(2)),
                ingresoNetoTotal: Number((comisiones + suscripciones).toFixed(2))
            },
            moderacion: {
                quejasPendientes: quejasRows[0].total,
                usuariosRiesgo: riesgoRows[0].total
            },
            ingresosSemanales,
            saludComunidad: distribucion,
            historialAuditoria: historialRows
        });
    } catch (error) {
        console.error('Error al obtener el dashboard admin:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

// Aplica sanción: resta 30 puntos de score al acusado y cierra la queja
const sancionarQueja = async (req, res) => {
    const connection = await pool.getConnection();
    try {
        const { id } = req.params;

        const [quejaRows] = await connection.query(
            "SELECT acusado_id, estado FROM quejas WHERE id = ?",
            [id]
        );
        if (quejaRows.length === 0) {
            connection.release();
            return res.status(404).json({ error: 'Queja no encontrada' });
        }
        if (quejaRows[0].estado === 'Resuelto') {
            connection.release();
            return res.status(400).json({ error: 'Esta queja ya fue resuelta' });
        }

        await connection.beginTransaction();

        // Resta 30 puntos sin bajar de 0
        await connection.query(
            "UPDATE usuarios SET score_confiabilidad = GREATEST(score_confiabilidad - 30, 0) WHERE id = ?",
            [quejaRows[0].acusado_id]
        );

        await connection.query(
            "UPDATE quejas SET estado = 'Resuelto' WHERE id = ?",
            [id]
        );

        await connection.commit();
        res.json({ message: 'Sanción aplicada: se restaron 30 puntos de score al usuario' });
    } catch (error) {
        await connection.rollback();
        console.error('Error al aplicar sanción:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    } finally {
        connection.release();
    }
};

// Desestima la queja: solo la cierra, no toca el score
const desestimarQueja = async (req, res) => {
    try {
        const { id } = req.params;

        const [result] = await pool.query(
            "UPDATE quejas SET estado = 'Resuelto' WHERE id = ? AND estado != 'Resuelto'",
            [id]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({ error: 'Queja no encontrada o ya resuelta' });
        }

        res.json({ message: 'Queja desestimada correctamente' });
    } catch (error) {
        console.error('Error al desestimar queja:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
};

module.exports = { getAdminDashboard, sancionarQueja, desestimarQueja };