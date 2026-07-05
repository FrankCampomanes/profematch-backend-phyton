-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 05-07-2026 a las 03:31:54
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `profematch_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evaluaciones`
--

CREATE TABLE `evaluaciones` (
  `id` int(11) NOT NULL,
  `tutoria_id` int(11) NOT NULL,
  `evaluador_id` int(11) NOT NULL,
  `evaluado_id` int(11) NOT NULL,
  `calificacion_general` int(11) DEFAULT NULL CHECK (`calificacion_general` between 1 and 5),
  `comentario` text DEFAULT NULL,
  `recomendaria` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evaluaciones_detalle`
--

CREATE TABLE `evaluaciones_detalle` (
  `id` int(11) NOT NULL,
  `evaluacion_id` int(11) NOT NULL,
  `categoria` varchar(255) NOT NULL,
  `puntuacion` int(11) DEFAULT NULL CHECK (`puntuacion` between 1 and 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `logros_estudiantes`
--

CREATE TABLE `logros_estudiantes` (
  `id` int(11) NOT NULL,
  `estudiante_id` int(11) NOT NULL,
  `insignia` varchar(255) NOT NULL,
  `fecha_obtencion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `materias`
--

CREATE TABLE `materias` (
  `id` int(11) NOT NULL,
  `nombre_materia` varchar(255) NOT NULL,
  `categoria` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `tipo` enum('recordatorio','cancelacion','valoracion') NOT NULL,
  `leida` tinyint(1) DEFAULT 0,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `penalizaciones`
--

CREATE TABLE `penalizaciones` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `tutoria_id` int(11) DEFAULT NULL,
  `puntos_descontados` int(11) NOT NULL,
  `motivo` text NOT NULL,
  `tipo` enum('cancelacion_tardia','no_show','queja_formal') NOT NULL,
  `fecha_penalizacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `perfiles_profesores`
--

CREATE TABLE `perfiles_profesores` (
  `usuario_id` int(11) NOT NULL,
  `tarifa_hora` decimal(10,2) NOT NULL,
  `plan_suscripcion` enum('gratuito','premium') NOT NULL,
  `comision_porcentaje` decimal(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tutorias`
--

CREATE TABLE `tutorias` (
  `id` int(11) NOT NULL,
  `profesor_id` int(11) NOT NULL,
  `estudiante_id` int(11) NOT NULL,
  `materia_id` int(11) NOT NULL,
  `fecha_hora_inicio` datetime NOT NULL,
  `fecha_hora_fin` datetime NOT NULL,
  `estado` enum('pendiente','confirmada','completada','cancelada') NOT NULL,
  `tarifa_bruta` decimal(10,2) DEFAULT NULL,
  `monto_comision` decimal(10,2) DEFAULT NULL,
  `monto_neto` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol` enum('admin','estudiante','profesor') NOT NULL,
  `score_confiabilidad` int(11) DEFAULT 100,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado_cuenta` varchar(20) DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `email`, `password_hash`, `rol`, `score_confiabilidad`, `fecha_registro`, `estado_cuenta`) VALUES
(1, 'Daniel Quispe', 'administrador@profematch.edu.pe', 'password_hash_123', 'admin', 100, '2026-07-05 00:37:03', 'activo'),
(2, 'Ana Silva', 'ana.estudiante@profematch.edu.pe', 'password_hash_123', 'estudiante', 95, '2026-07-05 00:37:03', 'activo'),
(3, 'Carlos Gómez', 'carlos.profe@profematch.edu.pe', 'password_hash_123', 'profesor', 85, '2026-07-05 00:37:03', 'activo'),
(4, 'Luis Ramírez', 'luis.profe@profematch.edu.pe', 'password_hash_123', 'profesor', 45, '2026-07-05 00:37:03', 'activo');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tutoria_id` (`tutoria_id`),
  ADD KEY `evaluador_id` (`evaluador_id`),
  ADD KEY `evaluado_id` (`evaluado_id`);

--
-- Indices de la tabla `evaluaciones_detalle`
--
ALTER TABLE `evaluaciones_detalle`
  ADD PRIMARY KEY (`id`),
  ADD KEY `evaluacion_id` (`evaluacion_id`);

--
-- Indices de la tabla `logros_estudiantes`
--
ALTER TABLE `logros_estudiantes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `estudiante_id` (`estudiante_id`);

--
-- Indices de la tabla `materias`
--
ALTER TABLE `materias`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `penalizaciones`
--
ALTER TABLE `penalizaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `tutoria_id` (`tutoria_id`);

--
-- Indices de la tabla `perfiles_profesores`
--
ALTER TABLE `perfiles_profesores`
  ADD PRIMARY KEY (`usuario_id`);

--
-- Indices de la tabla `tutorias`
--
ALTER TABLE `tutorias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `profesor_id` (`profesor_id`),
  ADD KEY `estudiante_id` (`estudiante_id`),
  ADD KEY `materia_id` (`materia_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `evaluaciones_detalle`
--
ALTER TABLE `evaluaciones_detalle`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `logros_estudiantes`
--
ALTER TABLE `logros_estudiantes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `materias`
--
ALTER TABLE `materias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `penalizaciones`
--
ALTER TABLE `penalizaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tutorias`
--
ALTER TABLE `tutorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  ADD CONSTRAINT `evaluaciones_ibfk_1` FOREIGN KEY (`tutoria_id`) REFERENCES `tutorias` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `evaluaciones_ibfk_2` FOREIGN KEY (`evaluador_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `evaluaciones_ibfk_3` FOREIGN KEY (`evaluado_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `evaluaciones_detalle`
--
ALTER TABLE `evaluaciones_detalle`
  ADD CONSTRAINT `evaluaciones_detalle_ibfk_1` FOREIGN KEY (`evaluacion_id`) REFERENCES `evaluaciones` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `logros_estudiantes`
--
ALTER TABLE `logros_estudiantes`
  ADD CONSTRAINT `logros_estudiantes_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `penalizaciones`
--
ALTER TABLE `penalizaciones`
  ADD CONSTRAINT `penalizaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `penalizaciones_ibfk_2` FOREIGN KEY (`tutoria_id`) REFERENCES `tutorias` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `perfiles_profesores`
--
ALTER TABLE `perfiles_profesores`
  ADD CONSTRAINT `perfiles_profesores_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `tutorias`
--
ALTER TABLE `tutorias`
  ADD CONSTRAINT `tutorias_ibfk_1` FOREIGN KEY (`profesor_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tutorias_ibfk_2` FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tutorias_ibfk_3` FOREIGN KEY (`materia_id`) REFERENCES `materias` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
