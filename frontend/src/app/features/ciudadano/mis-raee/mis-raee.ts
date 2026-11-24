import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { RaeeListado } from '../../../core/models/raee.models';
import { SolicitudCiudadano } from '../../../core/models/solicitudes.models';
import { ConfirmacionService } from '../../../core/services/confirmacion.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { RaeeService } from '../../../core/services/raee.service';
import { SolicitudesService } from '../../../core/services/solicitudes.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';
import { PesoKgPipe } from '../../../shared/pipes/peso-kg.pipe';

@Component({
  selector: 'app-mis-raee',
  imports: [
    RouterLink,
    EstadoBadge,
    EmptyState,
    Loading,
    PageHeader,
    FechaHoraPipe,
    PesoKgPipe,
  ],
  templateUrl: './mis-raee.html',
})
export class MisRaee {
  private readonly raee = inject(RaeeService);
  private readonly solicitudesService = inject(SolicitudesService);
  private readonly confirmacion = inject(ConfirmacionService);
  private readonly notificacion = inject(NotificacionService);

  readonly filtroEstado = signal('');
  readonly busqueda = signal('');
  readonly cancelando = signal<number | null>(null);

  readonly dispositivos = rxResource({
    stream: () => this.raee.mios(),
    defaultValue: [] as RaeeListado[],
  });

  readonly solicitudes = rxResource({
    stream: () => this.solicitudesService.mias(),
    defaultValue: [] as SolicitudCiudadano[],
  });

  readonly dispositivosFiltrados = computed(() => {
    const estado = this.filtroEstado();
    const texto = this.busqueda().trim().toLowerCase();

    return this.dispositivos.value().filter((dispositivo) => {
      const coincideEstado = !estado || dispositivo.estado_actual === estado;
      const coincideTexto =
        !texto ||
        dispositivo.codigo_seguimiento.toLowerCase().includes(texto) ||
        (dispositivo.marca ?? '').toLowerCase().includes(texto) ||
        (dispositivo.modelo ?? '').toLowerCase().includes(texto) ||
        dispositivo.categoria.toLowerCase().includes(texto);
      return coincideEstado && coincideTexto;
    });
  });

  readonly resumen = computed(() => {
    const lista = this.dispositivos.value();
    return {
      total: lista.length,
      registrados: lista.filter((d) => d.estado_actual === 'REGISTRADO').length,
      enProceso: lista.filter(
        (d) => d.estado_actual === 'SOLICITADO' || d.estado_actual === 'RECIBIDO',
      ).length,
      evaluados: lista.filter((d) => d.estado_actual === 'EVALUADO').length,
    };
  });

  solicitudPendiente(idRaee: number): SolicitudCiudadano | undefined {
    return this.solicitudes
      .value()
      .find(
        (solicitud) =>
          solicitud.id_raee === idRaee &&
          solicitud.estado_solicitud === 'PENDIENTE',
      );
  }

  limpiar(): void {
    this.filtroEstado.set('');
    this.busqueda.set('');
  }

  async cancelar(solicitud: SolicitudCiudadano): Promise<void> {
    const confirmado = await this.confirmacion.confirmar({
      titulo: 'Cancelar solicitud',
      mensaje: `¿Deseas cancelar la solicitud del equipo ${solicitud.codigo_seguimiento}? El equipo volverá al estado registrado.`,
      textoConfirmar: 'Sí, cancelar',
      textoCancelar: 'Mantener solicitud',
      peligro: true,
    });

    if (!confirmado) {
      return;
    }

    this.cancelando.set(solicitud.id_solicitud);
    try {
      await firstValueFrom(this.solicitudesService.cancelar(solicitud.id_solicitud));
      this.notificacion.exito('La solicitud fue cancelada correctamente.');
      this.dispositivos.reload();
      this.solicitudes.reload();
    } catch (error) {
      this.notificacion.error(mensajeError(error));
    } finally {
      this.cancelando.set(null);
    }
  }
}
