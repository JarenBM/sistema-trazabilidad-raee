export interface CentroCrearRequest {
  nombre_centro: string;
  direccion: string;
  telefono: string | null;
  ubigeo: string;
  latitud: number | null;
  longitud: number | null;
}

export interface CentroCreado {
  id_centro: number;
}

export interface CentroEstadoRequest {
  activo: boolean;
}
