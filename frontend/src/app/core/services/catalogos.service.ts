import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  Categoria,
  Centro,
  Distrito,
  TipoDestino,
} from '../models/catalogos.models';

@Injectable({ providedIn: 'root' })
export class CatalogosService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  distritos(): Observable<Distrito[]> {
    return this.http.get<Distrito[]>(`${this.api}/catalogos/distritos`);
  }

  categorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(`${this.api}/catalogos/categorias`);
  }

  tiposDestino(): Observable<TipoDestino[]> {
    return this.http.get<TipoDestino[]>(`${this.api}/catalogos/tipos-destino`);
  }

  centros(soloActivos = true): Observable<Centro[]> {
    const parametros = new HttpParams().set('solo_activos', String(soloActivos));
    return this.http.get<Centro[]>(`${this.api}/catalogos/centros`, {
      params: parametros,
    });
  }
}
