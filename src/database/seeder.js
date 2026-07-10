const bcrypt = require('bcrypt');
const pool = require('../config/db');

// Listas de datos para aleatoriedad
const comentariosPositivos = [
    "Excelente clase, muy clara la explicación.",
    "El profesor tiene muchísimo dominio del tema, lo recomiendo totalmente.",
    "Me ayudó bastante con mis dudas puntuales. Muy paciente.",
    "Dinámico y directo al grano, excelente sesión.",
    "Su metodología es muy buena, 100% recomendado.",
    "Gran paciencia para explicar conceptos complejos.",
    "Se nota que sabe mucho. La clase se me pasó volando.",
    "Puntual y muy profesional. Sus ejemplos son muy claros.",
    "Resolvió todos mis ejercicios y me dejó material de apoyo.",
    "Es exigente pero justo, aprendí muchísimo en una hora."
];

const comentariosNeutros = [
    "Buena clase, aunque un poco rápida.",
    "Explicó bien, pero tuvimos problemas de conexión.",
    "Estuvo bien, me ayudó a entender lo básico.",
    "Cumplió con el objetivo de la sesión.",
    "El profesor es bueno, pero la metodología podría mejorar."
];

const getRandomReview = () => {
    // 80% positivos, 20% neutros
    const arrayToUse = Math.random() > 0.2 ? comentariosPositivos : comentariosNeutros;
    return arrayToUse[Math.floor(Math.random() * arrayToUse.length)];
};

const getRandomScore = (min, max) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

const seedDatabase = async () => {
    try {
        console.log('Iniciando seeding de la base de datos...');

        // 1. Cursos por defecto
        const cursosList = [
            { nombre: 'Programación Web', categoria: 'Tecnología' },
            { nombre: 'Psicología Social', categoria: 'Ciencias Sociales' },
            { nombre: 'Cálculo I', categoria: 'Matemáticas' },
            { nombre: 'Física II', categoria: 'Ciencias' },
            { nombre: 'Microeconomía', categoria: 'Economía' },
            { nombre: 'Base de Datos', categoria: 'Tecnología' },
            { nombre: 'Anatomía Humana', categoria: 'Ciencias de la Salud' },
            { nombre: 'Redacción Académica', categoria: 'Humanidades' },
            { nombre: 'Gestión de Procesos', categoria: 'Ingeniería' },
            { nombre: 'Derecho Constitucional', categoria: 'Derecho' },
            { nombre: 'Estructura de Datos', categoria: 'Tecnología' },
            { nombre: 'Álgebra Lineal', categoria: 'Matemáticas' },
            { nombre: 'Neuropsicología', categoria: 'Psicología' }
        ];

        // Limpieza de tablas
        await pool.query('DELETE FROM resenas');
        await pool.query('DELETE FROM inscripciones');
        await pool.query('DELETE FROM sesiones');
        await pool.query('DELETE FROM profesores_cursos');
        await pool.query('DELETE FROM profesores_perfiles');
        await pool.query('DELETE FROM usuarios');
        await pool.query('DELETE FROM cursos');
        await pool.query('ALTER TABLE usuarios AUTO_INCREMENT = 1');
        await pool.query('ALTER TABLE cursos AUTO_INCREMENT = 1');
        await pool.query('ALTER TABLE sesiones AUTO_INCREMENT = 1');
        await pool.query('ALTER TABLE inscripciones AUTO_INCREMENT = 1');
        await pool.query('ALTER TABLE resenas AUTO_INCREMENT = 1');
        await pool.query('ALTER TABLE profesores_perfiles AUTO_INCREMENT = 1');

        for (const curso of cursosList) {
            await pool.query('INSERT INTO cursos (nombre, categoria) VALUES (?, ?)', [curso.nombre, curso.categoria]);
        }
        console.log('Cursos insertados.');

        const [cursosDB] = await pool.query('SELECT id FROM cursos');
        const cursoIds = cursosDB.map(c => c.id);

        const getRandomCursos = (count) => {
            const shuffled = [...cursoIds].sort(() => 0.5 - Math.random());
            return shuffled.slice(0, count);
        };

        // 2. Usuarios Base
        const password_hash_admin = await bcrypt.hash('admin123', 10);
        await pool.query(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES ('Admin Demo', 'admin@profematch.com', ?, 'admin', 'aprobado')", 
            [password_hash_admin]
        );

        const password_hash_estu = await bcrypt.hash('estu123', 10);
        const [resEstu] = await pool.query(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES ('Estudiante Demo', 'estu@profematch.com', ?, 'estudiante', 'aprobado')", 
            [password_hash_estu]
        );
        const estudianteId = resEstu.insertId;

        // Vamos a crear 3 estudiantes falsos extra para que dejen las reseñas
        const estudiantesFalsosIds = [];
        for (let i = 1; i <= 3; i++) {
            const pass = await bcrypt.hash('123456', 10);
            const [res] = await pool.query(
                "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES (?, ?, ?, 'estudiante', 'aprobado')",
                [`Alumno ${i}`, `alumno${i}@mail.com`, pass]
            );
            estudiantesFalsosIds.push(res.insertId);
        }

        const password_hash_prof = await bcrypt.hash('prof123', 10);
        const [resProfDemo] = await pool.query(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES ('Profesor Ejemplo', 'prof@profematch.com', ?, 'profesor', 'aprobado')", 
            [password_hash_prof]
        );
        const profDemoId = resProfDemo.insertId;

        const universidades = ['UCV', 'UPN', 'UNMSM', 'UTP', 'PUCP', 'ULima'];

        await pool.query(
            "INSERT INTO profesores_perfiles (usuario_id, descripcion, metodologia, reconocimientos, horarios, foto, universidad, perfil_completado) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                profDemoId, 
                "Profesor con más de 10 años de experiencia en desarrollo de software e investigación académica. Apasionado por la enseñanza.", 
                "Práctica 100%, aprendizaje basado en proyectos y feedback continuo.", 
                '["Top Developer 2024", "Certificado AWS"]', 
                '{"Lunes a Viernes":["16:00 - 20:00"]}', 
                "https://ui-avatars.com/api/?name=Profesor+Ejemplo&background=0D8ABC&color=fff",
                "UNMSM",
                true
            ]
        );
        const demoCursos = getRandomCursos(2);
        for (const cId of demoCursos) {
            await pool.query("INSERT INTO profesores_cursos (profesor_id, curso_id) VALUES (?, ?)", [profDemoId, cId]);
        }

        // Función para inyectar historial de clases a un profesor
        const injectHistory = async (profId, cursosProfesor) => {
            // Creamos 3 sesiones finalizadas
            for (let i = 0; i < 3; i++) {
                const cursoId = cursosProfesor[Math.floor(Math.random() * cursosProfesor.length)];
                
                // Hace un par de días
                const fechaInicio = new Date();
                fechaInicio.setDate(fechaInicio.getDate() - (i + 1));
                fechaInicio.setHours(10 + i, 0, 0); // 10:00, 11:00, etc.
                
                const fechaFin = new Date(fechaInicio);
                fechaFin.setHours(fechaFin.getHours() + 2); // 2 horas de duración

                const [sesionRes] = await pool.query(
                    "INSERT INTO sesiones (profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, cupos_maximos, estado) VALUES (?, ?, ?, ?, ?, 'Finalizada')",
                    [profId, cursoId, fechaInicio, fechaFin, 10]
                );
                const sesionId = sesionRes.insertId;

                // Inscribimos a un estudiante falso
                const estudianteRandomId = estudiantesFalsosIds[i % estudiantesFalsosIds.length];
                await pool.query(
                    "INSERT INTO inscripciones (estudiante_id, sesion_id, estado) VALUES (?, ?, 'Confirmado')",
                    [estudianteRandomId, sesionId]
                );

                // El estudiante deja una reseña única y aleatoria
                const puntuacionesJson = {
                    Claridad: getRandomScore(4, 5),
                    Dominio: getRandomScore(4, 5),
                    Puntualidad: getRandomScore(3, 5),
                    Profesionalismo: getRandomScore(4, 5),
                    Exigencia: getRandomScore(3, 5),
                    Disponibilidad: getRandomScore(4, 5)
                };

                await pool.query(
                    "INSERT INTO resenas (estudiante_id, profesor_id, sesion_id, comentario, puntuaciones_json) VALUES (?, ?, ?, ?, ?)",
                    [estudianteRandomId, profId, sesionId, getRandomReview(), JSON.stringify(puntuacionesJson)]
                );
            }
        };

        // Inyectar historial al Profe Demo
        await injectHistory(profDemoId, demoCursos);

        // 3. Inyección de Profesores Aleatorios (Reducido a 5)
        console.log('Generando 5 profesores ficticios y su historial...');
        const fakeNames = ["Dra. Laura Gómez", "Ing. Carlos Mendoza", "Lic. Ana Silva", "Dr. Roberto Casas", "Mg. Sofía Ríos"];
        
        for (let i = 0; i < 5; i++) {
            const email = `profe_fake_${i}@profematch.com`;
            const password_hash = await bcrypt.hash('123456', 10);
            
            const [resProf] = await pool.query(
                "INSERT INTO usuarios (nombre, email, password_hash, rol, estado) VALUES (?, ?, ?, 'profesor', 'aprobado')",
                [fakeNames[i], email, password_hash]
            );
            const profId = resProf.insertId;

            const univRandom = universidades[Math.floor(Math.random() * universidades.length)];

            // Perfil Completo
            await pool.query(
                "INSERT INTO profesores_perfiles (usuario_id, descripcion, metodologia, reconocimientos, horarios, foto, universidad, perfil_completado) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    profId, 
                    "Especialista con amplia trayectoria profesional y vocación de enseñanza práctica.", 
                    "Teórico-práctica, enfocada en resolución de problemas reales.",
                    '["Reconocimiento Académico 2023"]', 
                    '{"Fines de Semana":["09:00 - 13:00"]}', 
                    `https://ui-avatars.com/api/?name=${fakeNames[i].replace(/ /g, '+')}&background=random&color=fff`, 
                    univRandom,
                    true
                ]
            );

            const numCursos = Math.floor(Math.random() * 3) + 1;
            const asignados = getRandomCursos(numCursos);
            for (const cId of asignados) {
                await pool.query("INSERT INTO profesores_cursos (profesor_id, curso_id) VALUES (?, ?)", [profId, cId]);
            }

            // Inyectar historial al profe falso
            await injectHistory(profId, asignados);
        }
        
        console.log('10 Profesores ficticios creados con su historial y reseñas únicas exitosamente.');
        console.log('Seeding completado exitosamente.');
        process.exit(0);
    } catch (error) {
        console.error('Error durante el seeding:', error);
        process.exit(1);
    }
};

seedDatabase();
