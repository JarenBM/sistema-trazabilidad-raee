import {
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (peticion, siguiente) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const esRutaPublica =
    peticion.url.includes('/auth/login') ||
    peticion.url.includes('/auth/registro');
  const token = auth.token();

  const peticionConToken =
    token && !esRutaPublica
      ? peticion.clone({
          setHeaders: { Authorization: `Bearer ${token}` },
        })
      : peticion;

  return siguiente(peticionConToken).pipe(
    catchError((error: unknown) => {
      if (
        error instanceof HttpErrorResponse &&
        error.status === 401 &&
        auth.autenticado() &&
        !esRutaPublica
      ) {
        auth.limpiarSesion();
        const urlActual = router.url;
        if (!urlActual.startsWith('/login')) {
          void router.navigate(['/login'], {
            queryParams: {
              sesionExpirada: 1,
              returnUrl: urlActual,
            },
          });
        }
      }

      return throwError(() => error);
    }),
  );
};
