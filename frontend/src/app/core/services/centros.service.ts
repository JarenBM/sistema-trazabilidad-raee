import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CentroCreado,
  CentroCrearRequest,
} from '../models/centros.models';
import { EstadoActualizado } from '../models/usuarios.models';

@Injectable({ providedIn: 'root' })
export class CentrosService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  crear(datos: CentroCrearRequest): Observable<CentroCreado> {
    return this.http.post<CentroCreado>(`${this.api}/centros`, datos);
  }

  cambiarEstado(
    idCentro: number,
    activo: boolean,
  ): Observable<EstadoActualizado> {
    return this.http.patch<EstadoActualizado>(
      `${this.api}/centros/${idCentro}/estado`,
      { activo },
    );
  }
}
