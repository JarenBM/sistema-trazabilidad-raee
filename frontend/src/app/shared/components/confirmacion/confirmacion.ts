import {
  Component,
  effect,
  ElementRef,
  inject,
  viewChild,
} from '@angular/core';

import { ConfirmacionService } from '../../../core/services/confirmacion.service';

@Component({
  selector: 'app-confirmacion',
  templateUrl: './confirmacion.html',
  styleUrl: './confirmacion.css',
})
export class Confirmacion {
  readonly confirmacion = inject(ConfirmacionService);
  private readonly dialogo =
    viewChild.required<ElementRef<HTMLDialogElement>>('dialogo');

  constructor() {
    effect(() => {
      const opciones = this.confirmacion.estado();
      const elemento = this.dialogo().nativeElement;

      if (opciones && !elemento.open) {
        elemento.showModal();
      } else if (!opciones && elemento.open) {
        elemento.close();
      }
    });
  }

  cerrar(): void {
    this.confirmacion.responder(false);
  }

  confirmar(): void {
    this.confirmacion.responder(true);
  }
}
