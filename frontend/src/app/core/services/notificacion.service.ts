import { Injectable, signal } from '@angular/core';

export type TipoNotificacion = 'success' | 'danger' | 'warning' | 'info';

export interface Notificacion {
  id: number;
  tipo: TipoNotificacion;
  mensaje: string;
}

@Injectable({ providedIn: 'root' })
export class NotificacionService {
  private readonly _notificaciones = signal<Notificacion[]>([]);
  private contador = 0;

  readonly notificaciones = this._notificaciones.asReadonly();

  exito(mensaje: string): void {
    this.agregar('success', mensaje);
  }

  error(mensaje: string): void {
    this.agregar('danger', mensaje);
  }

  advertencia(mensaje: string): void {
    this.agregar('warning', mensaje);
  }

  info(mensaje: string): void {
    this.agregar('info', mensaje);
  }

  cerrar(id: number): void {
    this._notificaciones.update((items) =>
      items.filter((item) => item.id !== id),
    );
  }

  private agregar(tipo: TipoNotificacion, mensaje: string): void {
    const id = ++this.contador;
    this._notificaciones.update((items) => [...items, { id, tipo, mensaje }]);
    setTimeout(() => this.cerrar(id), 5500);
  }
}
