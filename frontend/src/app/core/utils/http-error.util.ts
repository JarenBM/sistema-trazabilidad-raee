import { HttpErrorResponse } from '@angular/common/http';

import { ApiError } from '../models/api.models';

function mensajeDeValidacion(cuerpo: ApiError): string | null {
  if (!Array.isArray(cuerpo.detail) || cuerpo.detail.length === 0) {
    return null;
  }
  const mensajes = cuerpo.detail
    .map((error) => error.msg?.trim())
    .filter((mensaje): mensaje is string => !!mensaje);
  return mensajes.length > 0 ? mensajes.join(' ') : null;
}

export function mensajeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'No se pudo conectar con el servidor. Verifica que la API esté disponible.';
    }

    const cuerpo = error.error as ApiError | string | null;

    if (typeof cuerpo === 'string' && cuerpo.trim()) {
      return cuerpo;
    }

    if (cuerpo && typeof cuerpo === 'object') {
      if (typeof cuerpo.detail === 'string' && cuerpo.detail.trim()) {
        return cuerpo.detail;
      }
      const validacion = mensajeDeValidacion(cuerpo);
      if (validacion) {
        return validacion;
      }
    }

    if (error.status === 401) {
      return 'Tu sesión expiró o las credenciales no son válidas.';
    }
    if (error.status === 403) {
      return 'No tienes permisos para realizar esta operación.';
    }
    if (error.status === 404) {
      return 'No se encontró la información solicitada.';
    }
    if (error.status === 409) {
      return 'La operación entra en conflicto con el estado actual de los datos.';
    }
    if (error.status === 503) {
      return 'La base de datos no se encuentra disponible en este momento.';
    }

    return `Ocurrió un error inesperado (HTTP ${error.status}).`;
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return 'Ocurrió un error inesperado. Inténtalo nuevamente.';
}

export function esNoEncontrado(error: unknown): boolean {
  return error instanceof HttpErrorResponse && error.status === 404;
}
