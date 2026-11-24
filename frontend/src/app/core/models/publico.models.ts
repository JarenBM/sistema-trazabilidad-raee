import { EstadoRaee } from './raee.models';

export interface Historial {
  id_historial: number;
  estado_anterior: string | null;
  estado_nuevo: string;
  comentario: string | null;
  fecha_cambio: string;
}

export interface FichaRaee {
  id_raee: number;
  codigo_seguimiento: string;
  categoria: string;
  marca: string | null;
  modelo: string | null;
  descripcion: string | null;
  fecha_registro: string;
  estado_actual: EstadoRaee | null;
  destino_final: string | null;
  es_valorizacion: boolean | null;
  peso_kg: number | null;
}

export interface RastreoRespuesta {
  ficha: FichaRaee;
  historial: Historial[];
}
