export type CondicionFisica = 'EXCELENTE' | 'REGULAR' | 'INSERVIBLE';

export interface EvaluacionCrearRequest {
  id_raee: number;
  id_tipo_destino: number;
  condicion_fisica: CondicionFisica;
  es_operativo: boolean;
  peso_kg: number;
  observaciones: string | null;
}

export interface EvaluacionRegistrada {
  id_evaluacion: number;
}

export const ETIQUETA_CONDICION: Record<CondicionFisica, string> = {
  EXCELENTE: 'Excelente',
  REGULAR: 'Regular',
  INSERVIBLE: 'Inservible',
};
