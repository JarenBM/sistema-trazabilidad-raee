import { Pipe, PipeTransform } from '@angular/core';

import { formatearPeso } from '../../core/utils/numero.util';

@Pipe({ name: 'pesoKg' })
export class PesoKgPipe implements PipeTransform {
  transform(valor: number | string | null | undefined): string {
    return formatearPeso(valor);
  }
}
