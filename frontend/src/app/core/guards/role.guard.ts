import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { Rol } from '../models/auth.models';
import { AuthService } from '../services/auth.service';
import { NotificacionService } from '../services/notificacion.service';

export function roleGuard(...roles: Rol[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const notificacion = inject(NotificacionService);

    const rol = auth.rol();
    if (rol && roles.includes(rol)) {
      return true;
    }

    notificacion.error('No tienes permisos para acceder a esa sección.');
    return router.createUrlTree([auth.rutaInicio(rol)]);
  };
}
