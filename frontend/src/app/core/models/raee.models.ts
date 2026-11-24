export type EstadoRaee =
  | 'REGISTRADO'
  | 'SOLICITADO'
  | 'RECIBIDO'
  | 'EVALUADO';

export interface RaeeCrearRequest {
  id_categoria: number;
  marca: string;
  modelo: string;
  descripcion: string | null;
}

export interface RaeeRegistrado {
  id_raee: number;
  codigo_seguimiento: string;
}

export interface RaeeListado {
  id_raee: number;
  codigo_seguimiento: string;
  categoria: string;
  marca: string | null;
  modelo: string | null;
  descripcion: string | null;
  fecha_registro: string;
  estado_actual: EstadoRaee | null;
  destino_final: string | null;
  peso_kg: number | null;
}

export const ETIQUETA_ESTADO_RAEE: Record<EstadoRaee, string> = {
  REGISTRADO: 'Registrado',
  SOLICITADO: 'Solicitado',
  RECIBIDO: 'Recibido',
  EVALUADO: 'Evaluado',
};
