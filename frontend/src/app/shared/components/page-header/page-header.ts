import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-page-header',
  imports: [RouterLink],
  template: `
    <div class="d-flex flex-wrap align-items-start justify-content-between gap-3 mb-4">
      <div>
        @if (volver()) {
          <a class="small text-decoration-none d-inline-flex align-items-center gap-1 mb-2" [routerLink]="volver()">
            <i class="bi bi-arrow-left"></i>Volver
          </a>
        }
        <h1 class="h3 mb-1">
          @if (icono()) {
            <i [class]="'bi me-2 text-raee ' + icono()"></i>
          }
          {{ titulo() }}
        </h1>
        @if (subtitulo()) {
          <p class="text-muted-soft mb-0">{{ subtitulo() }}</p>
        }
      </div>
      <div class="d-flex flex-wrap gap-2">
        <ng-content />
      </div>
    </div>
  `,
})
export class PageHeader {
  readonly titulo = input.required<string>();
  readonly subtitulo = input<string>('');
  readonly volver = input<string | null>(null);
  readonly icono = input<string>('');
}
