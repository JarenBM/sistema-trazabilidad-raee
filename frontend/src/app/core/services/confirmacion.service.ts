import { Injectable, signal } from '@angular/core';

export interface OpcionesConfirmacion {
  titulo: string;
  mensaje: string;
  textoConfirmar?: string;
  textoCancelar?: string;
  peligro?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ConfirmacionService {
  private readonly _estado = signal<OpcionesConfirmacion | null>(null);
  private resolver: ((valor: boolean) => void) | null = null;

  readonly estado = this._estado.asReadonly();

  confirmar(opciones: OpcionesConfirmacion): Promise<boolean> {
    this.resolver?.(false);
    this._estado.set(opciones);

    return new Promise<boolean>((resolver) => {
      this.resolver = resolver;
    });
  }

  responder(valor: boolean): void {
    const resolver = this.resolver;
    this.resolver = null;
    this._estado.set(null);
    resolver?.(valor);
  }
}
