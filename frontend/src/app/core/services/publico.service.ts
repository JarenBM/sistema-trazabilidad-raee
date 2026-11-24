import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { RastreoRespuesta } from '../models/publico.models';

@Injectable({ providedIn: 'root' })
export class PublicoService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  rastrear(codigo: string): Observable<RastreoRespuesta> {
    const codigoSeguro = encodeURIComponent(codigo.trim().toUpperCase());
    return this.http.get<RastreoRespuesta>(
      `${this.api}/publico/rastreo/${codigoSeguro}`,
    );
  }
}
