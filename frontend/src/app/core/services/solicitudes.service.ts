import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  OperacionRespuesta,
  SolicitudCentro,
  SolicitudCiudadano,
  SolicitudCreada,
  SolicitudCrearRequest,
} from '../models/solicitudes.models';

@Injectable({ providedIn: 'root' })
export class SolicitudesService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  crear(datos: SolicitudCrearRequest): Observable<SolicitudCreada> {
    return this.http.post<SolicitudCreada>(`${this.api}/solicitudes`, datos);
  }

  mias(): Observable<SolicitudCiudadano[]> {
    return this.http.get<SolicitudCiudadano[]>(
      `${this.api}/solicitudes/mias`,
    );
  }

  cancelar(idSolicitud: number): Observable<OperacionRespuesta> {
    return this.http.patch<OperacionRespuesta>(
      `${this.api}/solicitudes/${idSolicitud}/cancelar`,
      {},
    );
  }

  porCentro(estado?: string | null): Observable<SolicitudCentro[]> {
    let parametros = new HttpParams();
    if (estado) {
      parametros = parametros.set('estado', estado);
    }
    return this.http.get<SolicitudCentro[]>(`${this.api}/solicitudes/centro`, {
      params: parametros,
    });
  }

  recepcionar(idSolicitud: number): Observable<OperacionRespuesta> {
    return this.http.patch<OperacionRespuesta>(
      `${this.api}/solicitudes/${idSolicitud}/recepcionar`,
      {},
    );
  }
}
