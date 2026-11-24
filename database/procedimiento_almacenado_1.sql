DROP FUNCTION IF EXISTS fn_solicitudes_listar_por_usuario(INT);

CREATE FUNCTION fn_solicitudes_listar_por_usuario(p_id_usuario INT)
RETURNS TABLE (
    id_solicitud INT,
    id_raee INT,
    codigo_seguimiento VARCHAR,
    tipo_solicitud VARCHAR,
    fecha_programada TIMESTAMPTZ,
    estado_solicitud VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id_solicitud,
        s.id_raee,
        r.codigo_seguimiento::VARCHAR,
        s.tipo_solicitud::VARCHAR,
        s.fecha_programada,
        s.estado_solicitud::VARCHAR
    FROM solicitud_entrega s
    INNER JOIN dispositivo_raee r ON r.id_raee = s.id_raee
    WHERE r.id_usuario_generador = p_id_usuario
    ORDER BY s.id_solicitud DESC;
END;
$$;