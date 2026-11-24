import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  Credenciales,
  RegistroRequest,
  Rol,
  TokenRespuesta,
  UsuarioSesion,
} from '../models/auth.models';

const CLAVE_TOKEN = 'raee.token';
const CLAVE_USUARIO = 'raee.usuario';
const CLAVE_EXPIRA = 'raee.expira';

function leerUsuario(): UsuarioSesion | null {
  try {
    const crudo = localStorage.getItem(CLAVE_USUARIO);
    return crudo ? (JSON.parse(crudo) as UsuarioSesion) : null;
  } catch {
    return null;
  }
}

function leerToken(): string | null {
  try {
    return localStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

function leerExpiracion(): number | null {
  try {
    const crudo = localStorage.getItem(CLAVE_EXPIRA);
    const valor = crudo ? Number(crudo) : NaN;
    return Number.isFinite(valor) ? valor : null;
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly api = environment.apiUrl;

  private readonly _token = signal<string | null>(leerToken());
  private readonly _usuario = signal<UsuarioSesion | null>(leerUsuario());
  private readonly _expiraEn = signal<number | null>(leerExpiracion());

  readonly token = this._token.asReadonly();
  readonly usuario = this._usuario.asReadonly();
  readonly expiraEn = this._expiraEn.asReadonly();

  readonly autenticado = computed(
    () => this._token() !== null && this._usuario() !== null,
  );
  readonly rol = computed<Rol | null>(() => this._usuario()?.rol ?? null);
  readonly nombreCompleto = computed(() => {
    const usuario = this._usuario();
    return usuario ? `${usuario.nombres} ${usuario.apellidos}`.trim() : '';
  });

  login(correo: string, password: string): Observable<TokenRespuesta> {
    const cuerpo = new HttpParams()
      .set('username', correo)
      .set('password', password)
      .toString();

    return this.http
      .post<TokenRespuesta>(`${this.api}/auth/login`, cuerpo, {
        headers: new HttpHeaders({
          'Content-Type': 'application/x-www-form-urlencoded',
        }),
      })
      .pipe(tap((respuesta) => this.guardarSesion(respuesta)));
  }

  registrar(datos: RegistroRequest): Observable<UsuarioSesion> {
    return this.http.post<UsuarioSesion>(`${this.api}/auth/registro`, datos);
  }

  perfil(): Observable<UsuarioSesion> {
    return this.http
      .get<UsuarioSesion>(`${this.api}/auth/me`)
      .pipe(tap((usuario) => this.actualizarUsuario(usuario)));
  }

  guardarSesion(respuesta: TokenRespuesta): void {
    const expiraEn = Date.now() + respuesta.expira_en_minutos * 60_000;
    this._token.set(respuesta.access_token);
    this._usuario.set(respuesta.usuario);
    this._expiraEn.set(expiraEn);

    try {
      localStorage.setItem(CLAVE_TOKEN, respuesta.access_token);
      localStorage.setItem(CLAVE_USUARIO, JSON.stringify(respuesta.usuario));
      localStorage.setItem(CLAVE_EXPIRA, String(expiraEn));
    } catch {
      // Almacenamiento no disponible: la sesión queda solo en memoria.
    }
  }

  private actualizarUsuario(usuario: UsuarioSesion): void {
    this._usuario.set(usuario);
    try {
      localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
    } catch {
      // Ignorar almacenamiento no disponible.
    }
  }

  sesionExpirada(): boolean {
    const expira = this._expiraEn();
    return expira !== null && Date.now() >= expira;
  }

  limpiarSesion(): void {
    this._token.set(null);
    this._usuario.set(null);
    this._expiraEn.set(null);
    try {
      localStorage.removeItem(CLAVE_TOKEN);
      localStorage.removeItem(CLAVE_USUARIO);
      localStorage.removeItem(CLAVE_EXPIRA);
    } catch {
      // Ignorar almacenamiento no disponible.
    }
  }

  cerrarSesion(): void {
    this.limpiarSesion();
    void this.router.navigate(['/login']);
  }

  rutaInicio(rol: Rol | null = this.rol()): string {
    switch (rol) {
      case 'CIUDADANO':
        return '/ciudadano';
      case 'ENCARGADO':
        return '/encargado';
      case 'ADMIN':
        return '/admin';
      default:
        return '/';
    }
  }

  refrescarPerfil(): void {
    if (!this.autenticado() || this.sesionExpirada()) {
      if (this.sesionExpirada()) {
        this.limpiarSesion();
      }
      return;
    }

    this.perfil().subscribe({
      error: () => {
        // El interceptor se encarga de un 401; otros errores no bloquean la app.
      },
    });
  }
}
