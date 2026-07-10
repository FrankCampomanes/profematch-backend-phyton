-- Base de Datos: profematch_db
-- Creado para la nueva integración Frontend-Backend

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Eliminar tablas si existen para poder regenerar la base de datos limpia
DROP TABLE IF EXISTS `profesores_cursos`;
DROP TABLE IF EXISTS `resenas`;
DROP TABLE IF EXISTS `inscripciones`;
DROP TABLE IF EXISTS `sesiones`;
DROP TABLE IF EXISTS `cursos`;
DROP TABLE IF EXISTS `profesores_perfiles`;
DROP TABLE IF EXISTS `usuarios`;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `usuarios`
-- --------------------------------------------------------
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL UNIQUE,
  `password_hash` varchar(255) NULL DEFAULT NULL,
  `rol` enum('admin','profesor','estudiante') NOT NULL,
  `estado` enum('pendiente','aprobado','inactivo') NOT NULL DEFAULT 'pendiente',
  `score_confiabilidad` int(11) NOT NULL DEFAULT 100,
  `plan` varchar(50) NOT NULL DEFAULT 'Gratuito',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `profesores_perfiles`
-- --------------------------------------------------------
CREATE TABLE `profesores_perfiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL UNIQUE,
  `descripcion` text DEFAULT NULL,
  `metodologia` text DEFAULT NULL,
  `reconocimientos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`reconocimientos`)),
  `horarios` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`horarios`)),
  `foto` varchar(500) DEFAULT NULL,
  `universidad` varchar(255) DEFAULT NULL,
  `perfil_completado` boolean NOT NULL DEFAULT false,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `cursos`
-- --------------------------------------------------------
CREATE TABLE `cursos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `categoria` varchar(255) DEFAULT 'General',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `profesores_cursos` (Nueva Tabla Pivote)
-- --------------------------------------------------------
CREATE TABLE `profesores_cursos` (
  `profesor_id` int(11) NOT NULL,
  `curso_id` int(11) NOT NULL,
  PRIMARY KEY (`profesor_id`, `curso_id`),
  FOREIGN KEY (`profesor_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `sesiones`
-- --------------------------------------------------------
CREATE TABLE `sesiones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profesor_id` int(11) NOT NULL,
  `curso_id` int(11) NOT NULL,
  `fecha_hora_inicio` datetime NOT NULL,
  `fecha_hora_fin` datetime NOT NULL,
  `cupos_maximos` int(11) NOT NULL DEFAULT 1,
  `enlace_reunion` varchar(500) DEFAULT NULL,
  `estado` enum('Programada','En Curso','Finalizada','Cancelada') NOT NULL DEFAULT 'Programada',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`profesor_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `inscripciones`
-- --------------------------------------------------------
CREATE TABLE `inscripciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) NOT NULL,
  `sesion_id` int(11) NOT NULL,
  `fecha_inscripcion` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('Confirmado','Cancelado') NOT NULL DEFAULT 'Confirmado',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sesion_id`) REFERENCES `sesiones`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `estudiante_sesion_unica` (`estudiante_id`, `sesion_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `resenas`
-- --------------------------------------------------------
CREATE TABLE `resenas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) NOT NULL,
  `profesor_id` int(11) NOT NULL,
  `sesion_id` int(11) NOT NULL,
  `comentario` text NOT NULL,
  `puntuaciones_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`puntuaciones_json`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`profesor_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sesion_id`) REFERENCES `sesiones`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `resena_unica_por_sesion` (`estudiante_id`, `sesion_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

COMMIT;
