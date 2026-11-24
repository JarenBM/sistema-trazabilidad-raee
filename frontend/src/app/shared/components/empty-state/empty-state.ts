import { Component, input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  template: `
    <div class="text-center py-5">
      <div class="icon-circle mx-auto mb-3">
        <i [class]="'bi ' + icono()"></i>
      </div>
      <h3 class="h5">{{ titulo() }}</h3>
      <p class="text-muted-soft mb-3">{{ mensaje() }}</p>
      <ng-content />
    </div>
  `,
})
export class EmptyState {
  readonly titulo = input.required<string>();
  readonly mensaje = input<string>('');
  readonly icono = input<string>('bi-inbox');
}
