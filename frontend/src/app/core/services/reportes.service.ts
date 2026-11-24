import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ReporteResumen } from '../models/reportes.models';

@Injectable({ providedIn: 'root' })
export class ReportesService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  resumen(): Observable<ReporteResumen> {
    return this.http.get<ReporteResumen>(`${this.api}/reportes/resumen`);
  }
}
