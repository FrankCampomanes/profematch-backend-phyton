-- Ejecutar SOLO DESPUÉS de "npm run migrate" y "npm run seed"
-- Pega esto en tu interfaz de MySQL (Workbench / phpMyAdmin) con la BD profematch_db seleccionada.

USE profematch_db;

-- Queja reportada por un estudiante contra el profesor demo
INSERT INTO quejas (reportante_id, acusado_id, tipo, gravedad, estado)
VALUES (
  (SELECT id FROM usuarios WHERE email = 'estu@profematch.com'),
  (SELECT id FROM usuarios WHERE email = 'prof@profematch.com'),
  'No-show (Falta)', 'Alta', 'Pendiente'
);

-- Queja automática generada por el sistema (sin reportante) contra un profesor ficticio
INSERT INTO quejas (reportante_id, acusado_id, tipo, gravedad, estado)
VALUES (
  NULL,
  (SELECT id FROM usuarios WHERE email = 'profe_fake_0@profematch.com'),
  'Score Crítico (30pts)', 'Media', 'Pendiente'
);

-- Marcar 2 estudiantes como Premium (para que "Suscripciones" muestre algo)
UPDATE usuarios SET plan = 'Premium' WHERE rol = 'estudiante' LIMIT 2;

-- Bajar el score de un profesor ficticio para que aparezca en "Usuarios en Riesgo"
UPDATE usuarios SET score_confiabilidad = 35 WHERE email = 'profe_fake_0@profematch.com';
