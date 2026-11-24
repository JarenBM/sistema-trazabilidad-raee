import { Component, inject } from '@angular/core';

import {
  NotificacionService,
  TipoNotificacion,
} from '../../../core/services/notificacion.service';

@Component({
  selector: 'app-toast-container',
  templateUrl: './toast-container.html',
})
export class ToastContainer {
  readonly notificacion = inject(NotificacionService);

  icono(tipo: TipoNotificacion): string {
    switch (tipo) {
      case 'success':
        return 'bi-check-circle-fill text-success';
      case 'danger':
        return 'bi-exclamation-octagon-fill text-danger';
      case 'warning':
        return 'bi-exclamation-triangle-fill text-warning';
      default:
        return 'bi-info-circle-fill text-primary';
    }
  }

  borde(tipo: TipoNotificacion): string {
    return `border-${tipo === 'danger' ? 'danger' : tipo}`;
  }
}
