import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  EncargadoCrearRequest,
  EstadoActualizado,
  UsuarioCreado,
  UsuarioListado,
} from '../models/usuarios.models';

@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  listar(): Observable<UsuarioListado[]> {
    return this.http.get<UsuarioListado[]>(`${this.api}/usuarios`);
  }

  crearEncargado(datos: EncargadoCrearRequest): Observable<UsuarioCreado> {
    return this.http.post<UsuarioCreado>(
      `${this.api}/usuarios/encargado`,
      datos,
    );
  }

  cambiarEstado(
    idUsuario: number,
    activo: boolean,
  ): Observable<EstadoActualizado> {
    return this.http.patch<EstadoActualizado>(
      `${this.api}/usuarios/${idUsuario}/estado`,
      { activo },
    );
  }
}
