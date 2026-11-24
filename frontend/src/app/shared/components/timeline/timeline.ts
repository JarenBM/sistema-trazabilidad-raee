import { Component, computed, input } from '@angular/core';

import { Historial } from '../../../core/models/publico.models';
import { estadoRaee } from '../../../core/utils/estados.util';
import { FechaHoraPipe } from '../../pipes/fecha-hora.pipe';
import { EstadoBadge } from '../estado-badge/estado-badge';

@Component({
  selector: 'app-timeline',
  imports: [EstadoBadge, FechaHoraPipe],
  templateUrl: './timeline.html',
  styleUrl: './timeline.css',
})
export class Timeline {
  readonly eventos = input<Historial[]>([]);

  readonly eventosOrdenados = computed(() =>
    [...this.eventos()].sort(
      (a, b) =>
        new Date(a.fecha_cambio).getTime() -
        new Date(b.fecha_cambio).getTime(),
    ),
  );

  icono(estado: string): string {
    return estadoRaee(estado).icono;
  }

  clasePunto(estado: string): string {
    switch (estado) {
      case 'SOLICITADO':
        return 'timeline-dot pendiente';
      case 'RECIBIDO':
        return 'timeline-dot info';
      case 'EVALUADO':
        return 'timeline-dot success';
      default:
        return 'timeline-dot';
    }
  }
}
