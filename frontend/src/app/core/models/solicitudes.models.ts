export type TipoSolicitud = 'PRESENCIAL' | 'RECOLECCION';

export type EstadoSolicitud = 'PENDIENTE' | 'COMPLETADA' | 'CANCELADA';

export interface SolicitudCrearRequest {
  id_raee: number;
  id_centro: number;
  tipo_solicitud: TipoSolicitud;
  fecha_programada: string;
}

export interface SolicitudCreada {
  id_solicitud: number;
}

export interface SolicitudCiudadano {
  id_solicitud: number;
  id_raee: number;
  codigo_seguimiento: string;
  tipo_solicitud: string;
  fecha_programada: string;
  estado_solicitud: string;
}

export interface SolicitudCentro {
  id_solicitud: number;
  id_raee: number;
  codigo_seguimiento: string;
  categoria: string;
  marca: string | null;
  modelo: string | null;
  ciudadano: string;
  telefono_ciudadano: string | null;
  direccion_ciudadano: string | null;
  tipo_solicitud: string;
  fecha_programada: string;
  estado_solicitud: string;
  estado_raee_actual: string | null;
}

export interface OperacionRespuesta {
  mensaje: string;
}

export const ETIQUETA_TIPO_SOLICITUD: Record<TipoSolicitud, string> = {
  PRESENCIAL: 'Entrega presencial',
  RECOLECCION: 'Recolección',
};

export const ETIQUETA_ESTADO_SOLICITUD: Record<EstadoSolicitud, string> = {
  PENDIENTE: 'Pendiente',
  COMPLETADA: 'Completada',
  CANCELADA: 'Cancelada',
};
