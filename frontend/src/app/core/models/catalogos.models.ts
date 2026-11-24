export interface Distrito {
  ubigeo: string;
  distrito: string;
  provincia: string;
}

export interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string | null;
}

export interface TipoDestino {
  id_tipo_destino: number;
  nombre: string;
  descripcion: string | null;
  es_valorizacion: boolean;
}

export interface Centro {
  id_centro: number;
  nombre_centro: string;
  direccion: string;
  telefono: string | null;
  ubigeo: string;
  distrito: string;
  latitud: number | null;
  longitud: number | null;
  activo: boolean;
}
