import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  RaeeCrearRequest,
  RaeeListado,
  RaeeRegistrado,
} from '../models/raee.models';

@Injectable({ providedIn: 'root' })
export class RaeeService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  registrar(datos: RaeeCrearRequest): Observable<RaeeRegistrado> {
    return this.http.post<RaeeRegistrado>(`${this.api}/raee`, datos);
  }

  mios(): Observable<RaeeListado[]> {
    return this.http.get<RaeeListado[]>(`${this.api}/raee/mios`);
  }
}
