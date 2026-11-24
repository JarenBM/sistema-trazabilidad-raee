import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { SolicitudCentro } from '../../../core/models/solicitudes.models';
import { ConfirmacionService } from '../../../core/services/confirmacion.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { SolicitudesService } from '../../../core/services/solicitudes.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';

type Pestana = 'TODAS' | 'PENDIENTE' | 'COMPLETADA' | 'CANCELADA' | 'POR_EVALUAR';

interface DefinicionPestana {
  id: Pestana;
  etiqueta: string;
  icono: string;
}

@Component({
  selector: 'app-bandeja',
  imports: [
    EmptyState,
    EstadoBadge,
    Loading,
    PageHeader,
    FechaHoraPipe,
  ],
  templateUrl: './bandeja.html',
})
export class Bandeja {
  private readonly solicitudesService = inject(SolicitudesService);
  private readonly confirmacion = inject(ConfirmacionService);
  private readonly notificacion = inject(NotificacionService);
  private readonly router = inject(Router);

  readonly pestana = signal<Pestana>('PENDIENTE');
  readonly busqueda = signal('');
  readonly procesando = signal<number | null>(null);

  readonly pestanas: DefinicionPestana[] = [
    { id: 'PENDIENTE', etiqueta: 'Pendientes', icono: 'bi-hourglass-split' },
    { id: 'POR_EVALUAR', etiqueta: 'Por evaluar', icono: 'bi-clipboard-check' },
    { id: 'COMPLETADA', etiqueta: 'Completadas', icono: 'bi-check2-circle' },
    { id: 'CANCELADA', etiqueta: 'Canceladas', icono: 'bi-x-circle' },
    { id: 'TODAS', etiqueta: 'Todas', icono: 'bi-list-ul' },
  ];

  readonly solicitudes = rxResource({
    stream: () => this.solicitudesService.porCentro(),
    defaultValue: [] as SolicitudCentro[],
  });

  readonly filtradas = computed(() => {
    const pestana = this.pestana();
    const texto = this.busqueda().trim().toLowerCase();

    return this.solicitudes.value().filter((solicitud) => {
      const coincidePestana = this.coincidePestana(solicitud, pestana);
      const coincideTexto =
        !texto ||
        solicitud.codigo_seguimiento.toLowerCase().includes(texto) ||
        solicitud.ciudadano.toLowerCase().includes(texto) ||
        (solicitud.marca ?? '').toLowerCase().includes(texto) ||
        (solicitud.modelo ?? '').toLowerCase().includes(texto);
      return coincidePestana && coincideTexto;
    });
  });

  readonly conteos = computed(() => {
    const lista = this.solicitudes.value();
    return {
      PENDIENTE: lista.filter((s) => s.estado_solicitud === 'PENDIENTE').length,
      POR_EVALUAR: lista.filter(
        (s) =>
          s.estado_raee_actual === 'RECIBIDO' &&
          s.estado_solicitud !== 'CANCELADA',
      ).length,
      COMPLETADA: lista.filter((s) => s.estado_solicitud === 'COMPLETADA').length,
      CANCELADA: lista.filter((s) => s.estado_solicitud === 'CANCELADA').length,
      TODAS: lista.length,
    };
  });

  readonly sinCentro = computed(() => {
    const error = this.solicitudes.error();
    return !!error;
  });

  contar(pestana: Pestana): number {
    return this.conteos()[pestana];
  }

  cambiarPestana(pestana: Pestana): void {
    this.pestana.set(pestana);
  }

  async recepcionar(solicitud: SolicitudCentro): Promise<void> {
    const confirmado = await this.confirmacion.confirmar({
      titulo: 'Confirmar recepción',
      mensaje: `¿Confirmas que recibiste el equipo ${solicitud.codigo_seguimiento} de ${solicitud.ciudadano}? Esta acción actualizará la trazabilidad.`,
      textoConfirmar: 'Sí, recibido',
      textoCancelar: 'Cancelar',
    });

    if (!confirmado) {
      return;
    }

    this.procesando.set(solicitud.id_solicitud);
    try {
      await firstValueFrom(
        this.solicitudesService.recepcionar(solicitud.id_solicitud),
      );
      this.notificacion.exito(
        `Recepción registrada para ${solicitud.codigo_seguimiento}.`,
      );
      this.solicitudes.reload();
    } catch (error) {
      this.notificacion.error(mensajeError(error));
    } finally {
      this.procesando.set(null);
    }
  }

  async evaluar(solicitud: SolicitudCentro): Promise<void> {
    await this.router.navigate(['/encargado/evaluar', solicitud.id_raee], {
      state: { solicitud },
    });
  }

  private coincidePestana(
    solicitud: SolicitudCentro,
    pestana: Pestana,
  ): boolean {
    switch (pestana) {
      case 'TODAS':
        return true;
      case 'POR_EVALUAR':
        return (
          solicitud.estado_raee_actual === 'RECIBIDO' &&
          solicitud.estado_solicitud !== 'CANCELADA'
        );
      default:
        return solicitud.estado_solicitud === pestana;
    }
  }
}
