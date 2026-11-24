import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  EvaluacionCrearRequest,
  EvaluacionRegistrada,
} from '../models/evaluaciones.models';

@Injectable({ providedIn: 'root' })
export class EvaluacionesService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  registrar(datos: EvaluacionCrearRequest): Observable<EvaluacionRegistrada> {
    return this.http.post<EvaluacionRegistrada>(
      `${this.api}/evaluaciones`,
      datos,
    );
  }
}
