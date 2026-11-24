import { Component, computed, input } from '@angular/core';

import {
  estadoRaee,
  estadoRol,
  estadoSolicitud,
} from '../../../core/utils/estados.util';

type TipoEstado = 'raee' | 'solicitud' | 'rol';

@Component({
  selector: 'app-estado-badge',
  template: `
    <span [class]="'badge rounded-pill ' + visual().clase">
      <i [class]="'bi me-1 ' + visual().icono"></i>{{ visual().etiqueta }}
    </span>
  `,
})
export class EstadoBadge {
  readonly estado = input.required<string | null>();
  readonly tipo = input<TipoEstado>('raee');

  readonly visual = computed(() => {
    switch (this.tipo()) {
      case 'solicitud':
        return estadoSolicitud(this.estado());
      case 'rol':
        return estadoRol(this.estado());
      default:
        return estadoRaee(this.estado());
    }
  });
}
