export interface ApiError {
  detail?: string | ErrorValidacion[];
}

export interface ErrorValidacion {
  loc?: Array<string | number>;
  msg?: string;
  type?: string;
}
