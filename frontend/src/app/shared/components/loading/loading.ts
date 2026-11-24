import { Component, input } from '@angular/core';

@Component({
  selector: 'app-loading',
  template: `
    <div class="d-flex align-items-center gap-2 text-muted-soft py-3">
      <span class="spinner-border spinner-border-sm text-raee" role="status" aria-hidden="true"></span>
      <span>{{ texto() }}</span>
    </div>
  `,
})
export class Loading {
  readonly texto = input<string>('Cargando información...');
}
