import { Pipe, PipeTransform } from '@angular/core';

import { formatearFechaHora } from '../../core/utils/fecha.util';

@Pipe({ name: 'fechaHora' })
export class FechaHoraPipe implements PipeTransform {
  transform(valor: string | null | undefined): string {
    return formatearFechaHora(valor);
  }
}
