-- ============================================================================
-- SISTEMA WEB PARA LA GESTIÓN Y TRAZABILIDAD DE RAEE - JUNÍN, PERÚ
-- Motor: PostgreSQL 15+ (Compatible con Supabase)
-- Modelo Lógico: Tercera Forma Normal (3FN) - 9 Tablas
-- ============================================================================

-- Limpieza opcional en caso de re-ejecutar el script desde cero
DROP VIEW IF EXISTS vw_estado_actual_raee CASCADE;
DROP TABLE IF EXISTS historial_trazabilidad CASCADE;
DROP TABLE IF EXISTS evaluacion CASCADE;
DROP TABLE IF EXISTS solicitud_entrega CASCADE;
DROP TABLE IF EXISTS dispositivo_raee CASCADE;
DROP TABLE IF EXISTS tipo_destino CASCADE;
DROP TABLE IF EXISTS categoria_raee CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS centro_acopio CASCADE;
DROP TABLE IF EXISTS distrito CASCADE;

-- ============================================================================
-- 1. CREACIÓN DE TABLAS Y RESTRICCIONES (DDL)
-- ============================================================================

-- 1.1. DISTRITO (Catálogo geográfico INEI - Departamento de Junín = 12)
CREATE TABLE distrito (
    ubigeo CHAR(6) PRIMARY KEY,
    distrito VARCHAR(60) NOT NULL,
    provincia VARCHAR(60) NOT NULL,
    CONSTRAINT uq_distrito_provincia UNIQUE (distrito, provincia),
    CONSTRAINT chk_ubigeo_junin CHECK (ubigeo ~ '^12[0-9]{4}$')
);

-- 1.2. CENTRO_ACOPIO (Puntos físicos de recepción en Junín/Huancayo)
CREATE TABLE centro_acopio (
    id_centro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_centro VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    ubigeo CHAR(6) NOT NULL,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_centro_distrito FOREIGN KEY (ubigeo)
        REFERENCES distrito(ubigeo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 1.3. USUARIO (Actores del sistema: Ciudadano, Encargado, Admin)
CREATE TABLE usuario (
    id_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    rol VARCHAR(20) NOT NULL,
    ubigeo CHAR(6) NOT NULL,
    direccion VARCHAR(200),
    id_centro INT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_usuario_correo UNIQUE (correo),
    CONSTRAINT chk_usuario_rol CHECK (rol IN ('CIUDADANO', 'ENCARGADO', 'ADMIN')),
    CONSTRAINT chk_usuario_encargado_centro CHECK (
        (rol = 'ENCARGADO' AND id_centro IS NOT NULL) OR
        (rol IN ('CIUDADANO', 'ADMIN') AND id_centro IS NULL)
    ),
    CONSTRAINT fk_usuario_distrito FOREIGN KEY (ubigeo)
        REFERENCES distrito(ubigeo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_centro FOREIGN KEY (id_centro)
        REFERENCES centro_acopio(id_centro) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 1.4. CATEGORIA_RAEE (Clasificación normativa de residuos electrónicos)
CREATE TABLE categoria_raee (
    id_categoria INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
);

-- 1.5. TIPO_DESTINO (Catálogo de valorización y disposición final)
CREATE TABLE tipo_destino (
    id_tipo_destino INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    es_valorizacion BOOLEAN NOT NULL,
    CONSTRAINT uq_tipo_destino_nombre UNIQUE (nombre)
);

-- 1.6. DISPOSITIVO_RAEE (Entidad núcleo del aparato electrónico registrado)
CREATE TABLE dispositivo_raee (
    id_raee INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_seguimiento VARCHAR(25) NOT NULL,
    id_usuario_generador INT NOT NULL,
    id_categoria INT NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    descripcion TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_raee_codigo UNIQUE (codigo_seguimiento),
    CONSTRAINT fk_raee_usuario FOREIGN KEY (id_usuario_generador)
        REFERENCES usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_raee_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria_raee(id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 1.7. SOLICITUD_ENTREGA (Coordinación de entrega presencial o recolección)
CREATE TABLE solicitud_entrega (
    id_solicitud INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_raee INT NOT NULL,
    id_centro INT NOT NULL,
    tipo_solicitud VARCHAR(20) NOT NULL,
    fecha_solicitud TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_programada TIMESTAMPTZ NOT NULL,
    estado_solicitud VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT chk_solicitud_tipo CHECK (tipo_solicitud IN ('PRESENCIAL', 'RECOLECCION')),
    CONSTRAINT chk_solicitud_estado CHECK (estado_solicitud IN ('PENDIENTE', 'COMPLETADA', 'CANCELADA')),
    CONSTRAINT fk_solicitud_raee FOREIGN KEY (id_raee)
        REFERENCES dispositivo_raee(id_raee) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_solicitud_centro FOREIGN KEY (id_centro)
        REFERENCES centro_acopio(id_centro) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 1.8. EVALUACION (Inspección técnica única y asignación de destino final)
CREATE TABLE evaluacion (
    id_evaluacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_raee INT NOT NULL,
    id_evaluador INT NOT NULL,
    id_tipo_destino INT NOT NULL,
    condicion_fisica VARCHAR(20) NOT NULL,
    es_operativo BOOLEAN NOT NULL,
    peso_kg DECIMAL(8,2) NOT NULL,
    observaciones TEXT,
    fecha_evaluacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_evaluacion_raee UNIQUE (id_raee),
    CONSTRAINT chk_evaluacion_condicion CHECK (condicion_fisica IN ('EXCELENTE', 'REGULAR', 'INSERVIBLE')),
    CONSTRAINT chk_evaluacion_peso CHECK (peso_kg > 0),
    CONSTRAINT fk_evaluacion_raee FOREIGN KEY (id_raee)
        REFERENCES dispositivo_raee(id_raee) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_evaluacion_usuario FOREIGN KEY (id_evaluador)
        REFERENCES usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_evaluacion_destino FOREIGN KEY (id_tipo_destino)
        REFERENCES tipo_destino(id_tipo_destino) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 1.9. HISTORIAL_TRAZABILIDAD (Bitácora inmutable de cambios de estado)
CREATE TABLE historial_trazabilidad (
    id_historial INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_raee INT NOT NULL,
    id_usuario INT NOT NULL,
    estado_anterior VARCHAR(20) NULL,
    estado_nuevo VARCHAR(20) NOT NULL,
    comentario VARCHAR(255),
    fecha_cambio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_historial_estado_ant CHECK (
        estado_anterior IS NULL OR
        estado_anterior IN ('REGISTRADO', 'SOLICITADO', 'RECIBIDO', 'EVALUADO', 'FINALIZADO')
    ),
    CONSTRAINT chk_historial_estado_nvo CHECK (
        estado_nuevo IN ('REGISTRADO', 'SOLICITADO', 'RECIBIDO', 'EVALUADO', 'FINALIZADO')
    ),
    CONSTRAINT fk_historial_raee FOREIGN KEY (id_raee)
        REFERENCES dispositivo_raee(id_raee) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ============================================================================
-- 2. ÍNDICES DE RENDIMIENTO Y REGLAS DE NEGOCIO
-- ============================================================================

CREATE INDEX idx_solicitud_raee_estado ON solicitud_entrega (id_raee, estado_solicitud);

CREATE UNIQUE INDEX uq_solicitud_pendiente_por_raee
    ON solicitud_entrega (id_raee)
    WHERE estado_solicitud = 'PENDIENTE';

CREATE INDEX idx_historial_raee_fecha ON historial_trazabilidad (id_raee, fecha_cambio);

-- ============================================================================
-- 3. TRIGGER DE INMUTABILIDAD PARA TRAZABILIDAD (RN-09)
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_proteger_historial_trazabilidad()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Operación denegada: la tabla historial_trazabilidad es inmutable (solo permite INSERT).';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inmutabilidad_historial
BEFORE UPDATE OR DELETE ON historial_trazabilidad
FOR EACH ROW
EXECUTE FUNCTION fn_proteger_historial_trazabilidad();

-- ============================================================================
-- 4. VISTA SQL PARA CONSULTAR EL ESTADO ACTUAL SIN REDUNDANCIA (3FN)
-- ============================================================================

CREATE OR REPLACE VIEW vw_estado_actual_raee AS
SELECT
    d.id_raee,
    d.codigo_seguimiento,
    d.marca,
    d.modelo,
    d.descripcion,
    d.fecha_registro,
    c.id_categoria,
    c.nombre AS categoria,
    u.id_usuario AS id_generador,
    (u.nombres || ' ' || u.apellidos) AS generador,
    ult.estado_nuevo AS estado_actual,
    ult.comentario AS ultimo_comentario,
    ult.fecha_cambio AS fecha_ultimo_estado,
    td.nombre AS destino_final,
    td.es_valorizacion,
    ev.peso_kg
FROM dispositivo_raee d
INNER JOIN categoria_raee c ON d.id_categoria = c.id_categoria
INNER JOIN usuario u ON d.id_usuario_generador = u.id_usuario
LEFT JOIN LATERAL (
    SELECT h.estado_nuevo, h.comentario, h.fecha_cambio
    FROM historial_trazabilidad h
    WHERE h.id_raee = d.id_raee
    ORDER BY h.fecha_cambio DESC, h.id_historial DESC
    LIMIT 1
) ult ON TRUE
LEFT JOIN evaluacion ev ON ev.id_raee = d.id_raee
LEFT JOIN tipo_destino td ON ev.id_tipo_destino = td.id_tipo_destino;

-- ============================================================================
-- 5. DATOS SEMILLA DE PRUEBA (CONTEXTO HUANCAYO / JUNÍN)
-- ============================================================================

INSERT INTO distrito (ubigeo, distrito, provincia) VALUES
('120101', 'Huancayo', 'Huancayo'),
('120107', 'Chilca', 'Huancayo'),
('120114', 'El Tambo', 'Huancayo'),
('120127', 'Pilcomayo', 'Huancayo'),
('120128', 'Pucará', 'Huancayo'),
('120133', 'Sapallanga', 'Huancayo');

INSERT INTO centro_acopio (nombre_centro, direccion, telefono, ubigeo, latitud, longitud, activo) VALUES
('Punto Limpio Municipal - Cercado', 'Calle Real 850, Cercado de Huancayo', '064-214580', '120101', -12.068120, -75.210450, TRUE),
('Centro de Acopio RAEE - El Tambo', 'Av. Mariscal Castilla 2450, El Tambo', '064-248910', '120114', -12.049340, -75.218920, TRUE),
('Módulo Ambiental - Chilca', 'Av. 9 de Diciembre 410, Chilca', '064-231190', '120107', -12.084210, -75.206780, TRUE);

INSERT INTO usuario (nombres, apellidos, correo, password_hash, telefono, rol, ubigeo, direccion, id_centro, activo) VALUES
('Carlos Alberto', 'Mendoza Ríos', 'admin@raeehuancayo.pe', '$2b$10$EjemploHashSeguroAdmin000000000000000000000000000', '964111222', 'ADMIN', '120101', NULL, NULL, TRUE),
('Lucía Fernanda', 'Quispe Huamán', 'encargado.centro@raeehuancayo.pe', '$2b$10$EjemploHashSeguroEncargado1000000000000000000000', '964333444', 'ENCARGADO', '120101', NULL, 1, TRUE),
('Jorge Luis', 'Paredes Soto', 'encargado.tambo@raeehuancayo.pe', '$2b$10$EjemploHashSeguroEncargado2000000000000000000000', '964555666', 'ENCARGADO', '120114', NULL, 2, TRUE),
('Andrea Sofía', 'Vargas Salazar', 'andrea.vargas@gmail.com', '$2b$10$EjemploHashSeguroCiudadano1000000000000000000000', '954777888', 'CIUDADANO', '120114', 'Jr. Los Andes 345, El Tambo', NULL, TRUE),
('Marco Antonio', 'Castro Rojas', 'marco.castro@gmail.com', '$2b$10$EjemploHashSeguroCiudadano2000000000000000000000', '954999000', 'CIUDADANO', '120101', 'Av. Giráldez 620, Huancayo', NULL, TRUE);

INSERT INTO categoria_raee (nombre, descripcion) VALUES
('Informática y Telecomunicaciones', 'Laptops, computadoras de escritorio, monitores, teclados, impresoras, celulares y routers.'),
('Pequeños Electrodomésticos', 'Licuadoras, planchas, tostadoras, aspiradoras, secadoras de cabello y cafeteras.'),
('Grandes Electrodomésticos', 'Refrigeradoras, lavadoras, cocinas eléctricas, hornos microondas y termas.'),
('Aparatos Electrónicos de Consumo', 'Televisores, equipos de sonido, consolas de videojuegos y cámaras.'),
('Herramientas Eléctricas y Electrónicas', 'Taladros, amoladoras, sierras eléctricas y equipos de medición.');

INSERT INTO tipo_destino (nombre, descripcion, es_valorizacion) VALUES
('Reutilización', 'El equipo funciona correctamente y se destina a uso directo o donación.', TRUE),
('Reparación', 'El equipo presenta fallas menores y pasa a reacondicionamiento técnico.', TRUE),
('Recuperación de componentes', 'El equipo no es reparable en su totalidad, pero se extraen piezas útiles (RAM, discos, placas).', TRUE),
('Reciclaje', 'Desensamblaje y procesamiento para recuperar metales ferrosos, cobre, oro y plásticos.', TRUE),
('Disposición final', 'Confinamiento controlado en relleno de seguridad para componentes peligrosos no aprovechables.', FALSE);

INSERT INTO dispositivo_raee (codigo_seguimiento, id_usuario_generador, id_categoria, marca, modelo, descripcion) VALUES
('RAEE-2026-0001', 4, 1, 'Lenovo', 'IdeaPad 330', 'Laptop de 15 pulgadas, pantalla dañada pero enciende con monitor externo.'),
('RAEE-2026-0002', 5, 4, 'Sony', 'Bravia KDL-32', 'Televisor LED de 32 pulgadas, fuente de poder quemada, sin control remoto.');

INSERT INTO solicitud_entrega (id_raee, id_centro, tipo_solicitud, fecha_programada, estado_solicitud) VALUES
(1, 2, 'PRESENCIAL', NOW() - INTERVAL '2 days', 'COMPLETADA'),
(2, 1, 'RECOLECCION', NOW() + INTERVAL '2 days', 'PENDIENTE');

INSERT INTO evaluacion (id_raee, id_evaluador, id_tipo_destino, condicion_fisica, es_operativo, peso_kg, observaciones) VALUES
(1, 3, 3, 'REGULAR', TRUE, 2.20, 'Pantalla rota; placa madre, procesador y memoria RAM de 8GB totalmente recuperables.');

INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario) VALUES
(1, 4, NULL, 'REGISTRADO', 'Dispositivo registrado por el ciudadano en la plataforma.'),
(1, 4, 'REGISTRADO', 'SOLICITADO', 'Solicitud presencial programada para el Centro de Acopio El Tambo.'),
(1, 3, 'SOLICITADO', 'RECIBIDO', 'Equipo recepcionado físicamente en ventanilla.'),
(1, 3, 'RECIBIDO', 'EVALUADO', 'Evaluación completada: asignado a Recuperación de componentes.'),
(2, 5, NULL, 'REGISTRADO', 'Dispositivo registrado por el ciudadano en la plataforma.'),
(2, 5, 'REGISTRADO', 'SOLICITADO', 'Solicitud de recolección programada para Punto Limpio Cercado.');




-- ============================================================================
-- CAPA DE FUNCIONES ALMACENADAS (EQUIVALENTE A STORED PROCEDURES EN POSTGRESQL)
-- Proyecto: Sistema de Gestión y Trazabilidad de RAEE - Huancayo
-- ============================================================================

-- ============================================================================
-- 1. MÓDULO DE SEGURIDAD Y USUARIOS
-- ============================================================================

-- 1.1. Obtener datos de sesión por correo (para Login y validación de JWT)
CREATE OR REPLACE FUNCTION fn_usuario_obtener_sesion(p_correo VARCHAR)
RETURNS TABLE (
    id_usuario INT,
    nombres VARCHAR,
    apellidos VARCHAR,
    correo VARCHAR,
    password_hash VARCHAR,
    rol VARCHAR,
    id_centro INT,
    activo BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id_usuario, u.nombres, u.apellidos, u.correo,
           u.password_hash, u.rol, u.id_centro, u.activo
    FROM usuario u
    WHERE LOWER(u.correo) = LOWER(TRIM(p_correo));
END;
$$;

-- 1.2. Registrar nuevo usuario (Ciudadano o Encargado creado por Admin)
CREATE OR REPLACE FUNCTION fn_usuario_registrar(
    p_nombres VARCHAR,
    p_apellidos VARCHAR,
    p_correo VARCHAR,
    p_password_hash VARCHAR,
    p_telefono VARCHAR,
    p_rol VARCHAR,
    p_ubigeo CHAR(6),
    p_direccion VARCHAR,
    p_id_centro INT DEFAULT NULL
)
RETURNS TABLE (id_usuario INT, correo VARCHAR, rol VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_usuario INT;
BEGIN
    IF EXISTS (SELECT 1 FROM usuario u WHERE LOWER(u.correo) = LOWER(TRIM(p_correo))) THEN
        RAISE EXCEPTION 'CONFLICTO: El correo electrónico ya se encuentra registrado.' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO usuario (
        nombres, apellidos, correo, password_hash, telefono, rol, ubigeo, direccion, id_centro
    )
    VALUES (
        TRIM(p_nombres), TRIM(p_apellidos), LOWER(TRIM(p_correo)), p_password_hash,
        p_telefono, p_rol, p_ubigeo, p_direccion, p_id_centro
    )
    RETURNING usuario.id_usuario INTO v_id_usuario;

    RETURN QUERY
    SELECT u.id_usuario, u.correo, u.rol
    FROM usuario u
    WHERE u.id_usuario = v_id_usuario;
END;
$$;

-- 1.3. Listar usuarios (para administración)
CREATE OR REPLACE FUNCTION fn_usuarios_listar()
RETURNS TABLE (
    id_usuario INT,
    nombres VARCHAR,
    apellidos VARCHAR,
    correo VARCHAR,
    telefono VARCHAR,
    rol VARCHAR,
    distrito VARCHAR,
    nombre_centro VARCHAR,
    activo BOOLEAN,
    fecha_registro TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id_usuario, u.nombres, u.apellidos, u.correo, u.telefono,
           u.rol, d.distrito, c.nombre_centro, u.activo, u.fecha_registro
    FROM usuario u
    INNER JOIN distrito d ON u.ubigeo = d.ubigeo
    LEFT JOIN centro_acopio c ON u.id_centro = c.id_centro
    ORDER BY u.id_usuario DESC;
END;
$$;

-- 1.4. Activar / Desactivar cuenta de usuario
CREATE OR REPLACE FUNCTION fn_usuario_cambiar_estado(p_id_usuario INT, p_activo BOOLEAN)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE usuario
    SET activo = p_activo
    WHERE id_usuario = p_id_usuario;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: El usuario especificado no existe.' USING ERRCODE = 'P0001';
    END IF;

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 2. MÓDULO DE CATÁLOGOS Y CENTROS DE ACOPIO
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_catalogos_distritos()
RETURNS TABLE (ubigeo CHAR(6), distrito VARCHAR, provincia VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT d.ubigeo, d.distrito, d.provincia
    FROM distrito d
    ORDER BY d.provincia, d.distrito;
END;
$$;

CREATE OR REPLACE FUNCTION fn_catalogos_categorias()
RETURNS TABLE (id_categoria INT, nombre VARCHAR, descripcion TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id_categoria, c.nombre, c.descripcion
    FROM categoria_raee c
    ORDER BY c.id_categoria;
END;
$$;

CREATE OR REPLACE FUNCTION fn_catalogos_tipos_destino()
RETURNS TABLE (id_tipo_destino INT, nombre VARCHAR, descripcion TEXT, es_valorizacion BOOLEAN)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT t.id_tipo_destino, t.nombre, t.descripcion, t.es_valorizacion
    FROM tipo_destino t
    ORDER BY t.id_tipo_destino;
END;
$$;

CREATE OR REPLACE FUNCTION fn_centros_listar(p_solo_activos BOOLEAN DEFAULT TRUE)
RETURNS TABLE (
    id_centro INT,
    nombre_centro VARCHAR,
    direccion VARCHAR,
    telefono VARCHAR,
    ubigeo CHAR(6),
    distrito VARCHAR,
    latitud DECIMAL,
    longitud DECIMAL,
    activo BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id_centro, c.nombre_centro, c.direccion, c.telefono,
           c.ubigeo, d.distrito, c.latitud, c.longitud, c.activo
    FROM centro_acopio c
    INNER JOIN distrito d ON c.ubigeo = d.ubigeo
    WHERE (NOT p_solo_activos OR c.activo = TRUE)
    ORDER BY c.nombre_centro;
END;
$$;

CREATE OR REPLACE FUNCTION fn_centro_crear(
    p_nombre_centro VARCHAR,
    p_direccion VARCHAR,
    p_telefono VARCHAR,
    p_ubigeo CHAR(6),
    p_latitud DECIMAL DEFAULT NULL,
    p_longitud DECIMAL DEFAULT NULL
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_centro INT;
BEGIN
    INSERT INTO centro_acopio (nombre_centro, direccion, telefono, ubigeo, latitud, longitud)
    VALUES (TRIM(p_nombre_centro), TRIM(p_direccion), p_telefono, p_ubigeo, p_latitud, p_longitud)
    RETURNING id_centro INTO v_id_centro;

    RETURN v_id_centro;
END;
$$;

CREATE OR REPLACE FUNCTION fn_centro_cambiar_estado(p_id_centro INT, p_activo BOOLEAN)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE centro_acopio
    SET activo = p_activo
    WHERE id_centro = p_id_centro;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: El centro de acopio no existe.' USING ERRCODE = 'P0001';
    END IF;

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 3. MÓDULO DE DISPOSITIVOS RAEE Y SOLICITUDES (CIUDADANO)
-- ============================================================================

-- 3.1. Registrar dispositivo RAEE + generar código único + primer evento historial
CREATE OR REPLACE FUNCTION fn_raee_registrar(
    p_id_usuario INT,
    p_id_categoria INT,
    p_marca VARCHAR,
    p_modelo VARCHAR,
    p_descripcion TEXT
)
RETURNS TABLE (id_raee INT, codigo_seguimiento VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_raee INT;
    v_codigo VARCHAR(25);
BEGIN
    INSERT INTO dispositivo_raee (
        codigo_seguimiento, id_usuario_generador, id_categoria, marca, modelo, descripcion
    )
    VALUES (
        'TMP-' || LEFT(gen_random_uuid()::TEXT, 18),
        p_id_usuario, p_id_categoria, p_marca, p_modelo, p_descripcion
    )
    RETURNING dispositivo_raee.id_raee INTO v_id_raee;

    v_codigo := 'RAEE-' || EXTRACT(YEAR FROM NOW())::TEXT || '-' || LPAD(v_id_raee::TEXT, 4, '0');

    UPDATE dispositivo_raee
    SET codigo_seguimiento = v_codigo
    WHERE dispositivo_raee.id_raee = v_id_raee;

    INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario)
    VALUES (v_id_raee, p_id_usuario, NULL, 'REGISTRADO', 'Dispositivo registrado por el ciudadano en la plataforma.');

    RETURN QUERY SELECT v_id_raee, v_codigo;
END;
$$;

-- 3.2. Listar dispositivos propios de un ciudadano (usando la Vista 3FN)
CREATE OR REPLACE FUNCTION fn_raee_listar_por_usuario(p_id_usuario INT)
RETURNS TABLE (
    id_raee INT,
    codigo_seguimiento VARCHAR,
    categoria VARCHAR,
    marca VARCHAR,
    modelo VARCHAR,
    descripcion TEXT,
    fecha_registro TIMESTAMPTZ,
    estado_actual VARCHAR,
    destino_final VARCHAR,
    peso_kg DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT v.id_raee, v.codigo_seguimiento, v.categoria, v.marca, v.modelo,
           v.descripcion, v.fecha_registro, v.estado_actual, v.destino_final, v.peso_kg
    FROM vw_estado_actual_raee v
    WHERE v.id_generador = p_id_usuario
    ORDER BY v.id_raee DESC;
END;
$$;

-- 3.3. Crear solicitud de entrega o recolección (Transaccional)
CREATE OR REPLACE FUNCTION fn_solicitud_crear(
    p_id_raee INT,
    p_id_usuario INT,
    p_id_centro INT,
    p_tipo_solicitud VARCHAR,
    p_fecha_programada TIMESTAMPTZ
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado_actual VARCHAR;
    v_centro_activo BOOLEAN;
    v_id_solicitud INT;
BEGIN
    SELECT estado_actual INTO v_estado_actual
    FROM vw_estado_actual_raee
    WHERE id_raee = p_id_raee AND id_generador = p_id_usuario;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: El dispositivo no existe o no pertenece al ciudadano.' USING ERRCODE = 'P0001';
    END IF;

    IF v_estado_actual <> 'REGISTRADO' THEN
        RAISE EXCEPTION 'CONFLICTO: Solo se pueden solicitar equipos en estado REGISTRADO (estado actual: %).', v_estado_actual USING ERRCODE = 'P0001';
    END IF;

    SELECT activo INTO v_centro_activo
    FROM centro_acopio
    WHERE id_centro = p_id_centro;

    IF NOT FOUND OR NOT v_centro_activo THEN
        RAISE EXCEPTION 'CONFLICTO: El centro de acopio seleccionado no existe o está inactivo.' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO solicitud_entrega (id_raee, id_centro, tipo_solicitud, fecha_programada, estado_solicitud)
    VALUES (p_id_raee, p_id_centro, p_tipo_solicitud, p_fecha_programada, 'PENDIENTE')
    RETURNING id_solicitud INTO v_id_solicitud;

    INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario)
    VALUES (p_id_raee, p_id_usuario, 'REGISTRADO', 'SOLICITADO', 'Solicitud de entrega (' || p_tipo_solicitud || ') programada.');

    RETURN v_id_solicitud;
END;
$$;

-- 3.4. Cancelar solicitud pendiente (Transaccional)
CREATE OR REPLACE FUNCTION fn_solicitud_cancelar(p_id_solicitud INT, p_id_usuario INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_raee INT;
    v_estado_sol VARCHAR;
BEGIN
    SELECT s.id_raee, s.estado_solicitud INTO v_id_raee, v_estado_sol
    FROM solicitud_entrega s
    INNER JOIN dispositivo_raee d ON s.id_raee = d.id_raee
    WHERE s.id_solicitud = p_id_solicitud AND d.id_usuario_generador = p_id_usuario;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: La solicitud no existe o no pertenece al ciudadano.' USING ERRCODE = 'P0001';
    END IF;

    IF v_estado_sol <> 'PENDIENTE' THEN
        RAISE EXCEPTION 'CONFLICTO: Solo se pueden cancelar solicitudes en estado PENDIENTE.' USING ERRCODE = 'P0001';
    END IF;

    UPDATE solicitud_entrega
    SET estado_solicitud = 'CANCELADA'
    WHERE id_solicitud = p_id_solicitud;

    INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario)
    VALUES (v_id_raee, p_id_usuario, 'SOLICITADO', 'REGISTRADO', 'Solicitud cancelada por el ciudadano.');

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 4. MÓDULO DE RECEPCIÓN Y EVALUACIÓN TÉCNICA (ENCARGADO DE CENTRO)
-- ============================================================================

-- 4.1. Bandeja de solicitudes filtrada por el centro asignado al encargado
CREATE OR REPLACE FUNCTION fn_solicitudes_listar_por_centro(
    p_id_centro INT,
    p_estado VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id_solicitud INT,
    id_raee INT,
    codigo_seguimiento VARCHAR,
    categoria VARCHAR,
    marca VARCHAR,
    modelo VARCHAR,
    ciudadano VARCHAR,
    telefono_ciudadano VARCHAR,
    direccion_ciudadano VARCHAR,
    tipo_solicitud VARCHAR,
    fecha_programada TIMESTAMPTZ,
    estado_solicitud VARCHAR,
    estado_raee_actual VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT s.id_solicitud, d.id_raee, d.codigo_seguimiento, c.nombre AS categoria,
           d.marca, d.modelo, (u.nombres || ' ' || u.apellidos)::VARCHAR AS ciudadano,
           u.telefono, u.direccion, s.tipo_solicitud, s.fecha_programada,
           s.estado_solicitud, v.estado_actual
    FROM solicitud_entrega s
    INNER JOIN dispositivo_raee d ON s.id_raee = d.id_raee
    INNER JOIN categoria_raee c ON d.id_categoria = c.id_categoria
    INNER JOIN usuario u ON d.id_usuario_generador = u.id_usuario
    INNER JOIN vw_estado_actual_raee v ON d.id_raee = v.id_raee
    WHERE s.id_centro = p_id_centro
      AND (p_estado IS NULL OR s.estado_solicitud = p_estado)
    ORDER BY s.fecha_programada ASC;
END;
$$;

-- 4.2. Confirmar recepción física en el centro (Transaccional)
CREATE OR REPLACE FUNCTION fn_solicitud_recepcionar(p_id_solicitud INT, p_id_encargado INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_centro_encargado INT;
    v_id_centro_sol INT;
    v_id_raee INT;
    v_estado_sol VARCHAR;
BEGIN
    SELECT id_centro INTO v_id_centro_encargado
    FROM usuario
    WHERE id_usuario = p_id_encargado AND rol = 'ENCARGADO' AND activo = TRUE;

    IF v_id_centro_encargado IS NULL THEN
        RAISE EXCEPTION 'PROHIBIDO: El usuario no es un encargado de centro activo.' USING ERRCODE = 'P0001';
    END IF;

    SELECT id_centro, id_raee, estado_solicitud INTO v_id_centro_sol, v_id_raee, v_estado_sol
    FROM solicitud_entrega
    WHERE id_solicitud = p_id_solicitud;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: La solicitud especificada no existe.' USING ERRCODE = 'P0001';
    END IF;

    IF v_id_centro_sol <> v_id_centro_encargado THEN
        RAISE EXCEPTION 'PROHIBIDO: No puede recepcionar solicitudes dirigidas a otro centro de acopio.' USING ERRCODE = 'P0001';
    END IF;

    IF v_estado_sol <> 'PENDIENTE' THEN
        RAISE EXCEPTION 'CONFLICTO: La solicitud ya fue procesada o cancelada.' USING ERRCODE = 'P0001';
    END IF;

    UPDATE solicitud_entrega
    SET estado_solicitud = 'COMPLETADA'
    WHERE id_solicitud = p_id_solicitud;

    INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario)
    VALUES (v_id_raee, p_id_encargado, 'SOLICITADO', 'RECIBIDO', 'Dispositivo recepcionado físicamente en el centro de acopio.');

    RETURN TRUE;
END;
$$;

-- 4.3. Registrar evaluación técnica y destino ambiental (Transaccional)
CREATE OR REPLACE FUNCTION fn_evaluacion_registrar(
    p_id_raee INT,
    p_id_evaluador INT,
    p_id_tipo_destino INT,
    p_condicion_fisica VARCHAR,
    p_es_operativo BOOLEAN,
    p_peso_kg DECIMAL,
    p_observaciones TEXT
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_centro_encargado INT;
    v_estado_actual VARCHAR;
    v_destino_nombre VARCHAR;
    v_id_evaluacion INT;
BEGIN
    SELECT id_centro INTO v_id_centro_encargado
    FROM usuario
    WHERE id_usuario = p_id_evaluador AND rol = 'ENCARGADO' AND activo = TRUE;

    IF v_id_centro_encargado IS NULL THEN
        RAISE EXCEPTION 'PROHIBIDO: Solo un encargado activo puede registrar evaluaciones.' USING ERRCODE = 'P0001';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM solicitud_entrega s
        WHERE s.id_raee = p_id_raee
          AND s.id_centro = v_id_centro_encargado
          AND s.estado_solicitud = 'COMPLETADA'
    ) THEN
        RAISE EXCEPTION 'PROHIBIDO: El dispositivo no fue recepcionado en el centro asignado al evaluador.' USING ERRCODE = 'P0001';
    END IF;

    SELECT estado_actual INTO v_estado_actual
    FROM vw_estado_actual_raee
    WHERE id_raee = p_id_raee;

    IF v_estado_actual <> 'RECIBIDO' THEN
        RAISE EXCEPTION 'CONFLICTO: El dispositivo debe estar en estado RECIBIDO para ser evaluado (estado actual: %).', v_estado_actual USING ERRCODE = 'P0001';
    END IF;

    SELECT nombre INTO v_destino_nombre
    FROM tipo_destino
    WHERE id_tipo_destino = p_id_tipo_destino;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NO_ENCONTRADO: El tipo de destino seleccionado no existe.' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO evaluacion (
        id_raee, id_evaluador, id_tipo_destino, condicion_fisica, es_operativo, peso_kg, observaciones
    )
    VALUES (
        p_id_raee, p_id_evaluador, p_id_tipo_destino, p_condicion_fisica, p_es_operativo, p_peso_kg, p_observaciones
    )
    RETURNING id_evaluacion INTO v_id_evaluacion;

    INSERT INTO historial_trazabilidad (id_raee, id_usuario, estado_anterior, estado_nuevo, comentario)
    VALUES (
        p_id_raee, p_id_evaluador, 'RECIBIDO', 'EVALUADO',
        'Evaluación técnica completada (' || p_peso_kg || ' kg). Destino asignado: ' || v_destino_nombre || '.'
    );

    RETURN v_id_evaluacion;
END;
$$;

-- ============================================================================
-- 5. MÓDULO DE CONSULTA PÚBLICA Y REPORTES ESTADÍSTICOS
-- ============================================================================

-- 5.1. Ficha pública de un RAEE por código de seguimiento (sin datos personales)
CREATE OR REPLACE FUNCTION fn_publico_obtener_raee(p_codigo_seguimiento VARCHAR)
RETURNS TABLE (
    id_raee INT,
    codigo_seguimiento VARCHAR,
    categoria VARCHAR,
    marca VARCHAR,
    modelo VARCHAR,
    descripcion TEXT,
    fecha_registro TIMESTAMPTZ,
    estado_actual VARCHAR,
    destino_final VARCHAR,
    es_valorizacion BOOLEAN,
    peso_kg DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT v.id_raee, v.codigo_seguimiento, v.categoria, v.marca, v.modelo,
           v.descripcion, v.fecha_registro, v.estado_actual, v.destino_final,
           v.es_valorizacion, v.peso_kg
    FROM vw_estado_actual_raee v
    WHERE UPPER(v.codigo_seguimiento) = UPPER(TRIM(p_codigo_seguimiento));
END;
$$;

-- 5.2. Línea de tiempo cronológica de trazabilidad (pública)
CREATE OR REPLACE FUNCTION fn_publico_historial_raee(p_codigo_seguimiento VARCHAR)
RETURNS TABLE (
    id_historial INT,
    estado_anterior VARCHAR,
    estado_nuevo VARCHAR,
    comentario VARCHAR,
    fecha_cambio TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT h.id_historial, h.estado_anterior, h.estado_nuevo, h.comentario, h.fecha_cambio
    FROM historial_trazabilidad h
    INNER JOIN dispositivo_raee d ON h.id_raee = d.id_raee
    WHERE UPPER(d.codigo_seguimiento) = UPPER(TRIM(p_codigo_seguimiento))
    ORDER BY h.fecha_cambio ASC, h.id_historial ASC;
END;
$$;

-- 5.3. Indicadores globales para el Dashboard del Administrador
CREATE OR REPLACE FUNCTION fn_reportes_resumen()
RETURNS TABLE (
    total_dispositivos BIGINT,
    total_registrados BIGINT,
    total_solicitados BIGINT,
    total_recibidos BIGINT,
    total_evaluados BIGINT,
    peso_total_kg NUMERIC,
    peso_valorizado_kg NUMERIC,
    peso_disposicion_final_kg NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(v.id_raee) AS total_dispositivos,
        COUNT(*) FILTER (WHERE v.estado_actual = 'REGISTRADO') AS total_registrados,
        COUNT(*) FILTER (WHERE v.estado_actual = 'SOLICITADO') AS total_solicitados,
        COUNT(*) FILTER (WHERE v.estado_actual = 'RECIBIDO') AS total_recibidos,
        COUNT(*) FILTER (WHERE v.estado_actual IN ('EVALUADO', 'FINALIZADO')) AS total_evaluados,
        COALESCE(SUM(v.peso_kg), 0) AS peso_total_kg,
        COALESCE(SUM(v.peso_kg) FILTER (WHERE v.es_valorizacion = TRUE), 0) AS peso_valorizado_kg,
        COALESCE(SUM(v.peso_kg) FILTER (WHERE v.es_valorizacion = FALSE), 0) AS peso_disposicion_final_kg
    FROM vw_estado_actual_raee v;
END;
$$;