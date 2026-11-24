import { Component, computed, inject, input, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import {
  FormField,
  FormRoot,
  form,
  required,
  validate,
} from '@angular/forms/signals';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { Centro } from '../../../core/models/catalogos.models';
import { RaeeListado } from '../../../core/models/raee.models';
import {
  SolicitudCiudadano,
  TipoSolicitud,
} from '../../../core/models/solicitudes.models';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { ConfirmacionService } from '../../../core/services/confirmacion.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { RaeeService } from '../../../core/services/raee.service';
import { SolicitudesService } from '../../../core/services/solicitudes.service';
import { ETIQUETA_TIPO_SOLICITUD } from '../../../core/models/solicitudes.models';
import { aISO } from '../../../core/utils/fecha.util';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';

interface SolicitudCreada {
  idSolicitud: number;
  codigo: string;
  centro: string;
  tipo: string;
  fecha: string;
}

@Component({
  selector: 'app-nueva-solicitud',
  imports: [
    FormField,
    FormRoot,
    RouterLink,
    PageHeader,
    EstadoBadge,
    EmptyState,
    Loading,
    FechaHoraPipe,
  ],
  templateUrl: './nueva-solicitud.html',
})
export class NuevaSolicitud {
  readonly idRaee = input.required<string>();

  private readonly raee = inject(RaeeService);
  private readonly catalogos = inject(CatalogosService);
  private readonly solicitudesService = inject(SolicitudesService);
  private readonly confirmacion = inject(ConfirmacionService);
  private readonly notificacion = inject(NotificacionService);
  private readonly router = inject(Router);

  readonly dispositivos = rxResource({
    stream: () => this.raee.mios(),
    defaultValue: [] as RaeeListado[],
  });

  readonly centros = rxResource({
    stream: () => this.catalogos.centros(true),
    defaultValue: [] as Centro[],
  });

  readonly solicitudes = rxResource({
    stream: () => this.solicitudesService.mias(),
    defaultValue: [] as SolicitudCiudadano[],
  });

  readonly dispositivo = computed(() =>
    this.dispositivos
      .value()
      .find((item) => item.id_raee === Number(this.idRaee())),
  );

  readonly solicitudPendiente = computed(() =>
    this.solicitudes
      .value()
      .find(
        (solicitud) =>
          solicitud.id_raee === Number(this.idRaee()) &&
          solicitud.estado_solicitud === 'PENDIENTE',
      ),
  );

  readonly modelo = signal({
    idCentro: '',
    tipoSolicitud: 'PRESENCIAL' as TipoSolicitud,
    fecha: '',
  });

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.idCentro, {
        message: 'Selecciona el centro de acopio donde entregarás el equipo.',
      });
      required(camino.fecha, {
        message: 'Indica la fecha y hora de la entrega.',
      });
      validate(camino.fecha, ({ value }) => {
        const fecha = value();
        if (!fecha) {
          return undefined;
        }
        if (!aISO(fecha) || !(new Date(fecha).getTime() > Date.now())) {
          return {
            kind: 'fecha-futura',
            message: 'La fecha programada debe ser posterior a la fecha actual.',
          };
        }
        return undefined;
      });
    },
    {
      submission: {
        action: () => this.crearSolicitud(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly centroSeleccionado = computed(() =>
    this.centros
      .value()
      .find((centro) => centro.id_centro === Number(this.modelo().idCentro)),
  );

  readonly error = signal<string | null>(null);
  readonly creada = signal<SolicitudCreada | null>(null);
  readonly cancelando = signal(false);

  readonly etiquetaTipo = ETIQUETA_TIPO_SOLICITUD;

  private async crearSolicitud(): Promise<void> {
    this.error.set(null);
    const dispositivo = this.dispositivo();

    if (!dispositivo) {
      this.error.set('No se encontró el equipo seleccionado.');
      return;
    }
    if (dispositivo.estado_actual !== 'REGISTRADO') {
      this.error.set('El equipo ya no está disponible para programar una entrega.');
      return;
    }

    const fechaIso = aISO(this.modelo().fecha);
    if (!fechaIso) {
      this.error.set('La fecha y hora indicadas no son válidas.');
      return;
    }

    const centro = this.centroSeleccionado();

    try {
      const respuesta = await firstValueFrom(
        this.solicitudesService.crear({
          id_raee: dispositivo.id_raee,
          id_centro: Number(this.modelo().idCentro),
          tipo_solicitud: this.modelo().tipoSolicitud,
          fecha_programada: fechaIso,
        }),
      );

      this.creada.set({
        idSolicitud: respuesta.id_solicitud,
        codigo: dispositivo.codigo_seguimiento,
        centro: centro?.nombre_centro ?? 'Centro seleccionado',
        tipo: this.etiquetaTipo[this.modelo().tipoSolicitud],
        fecha: fechaIso,
      });
      this.notificacion.exito('Solicitud de entrega programada correctamente.');
      this.dispositivos.reload();
      this.solicitudes.reload();
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }

  async cancelar(solicitud: SolicitudCiudadano): Promise<void> {
    const confirmado = await this.confirmacion.confirmar({
      titulo: 'Cancelar solicitud',
      mensaje: 'El equipo volverá al estado registrado y podrás programar otra entrega.',
      textoConfirmar: 'Sí, cancelar',
      textoCancelar: 'Mantener solicitud',
      peligro: true,
    });

    if (!confirmado) {
      return;
    }

    this.cancelando.set(true);
    try {
      await firstValueFrom(this.solicitudesService.cancelar(solicitud.id_solicitud));
      this.notificacion.exito('La solicitud fue cancelada correctamente.');
      this.creada.set(null);
      this.dispositivos.reload();
      this.solicitudes.reload();
      await this.router.navigate(['/ciudadano']);
    } catch (error) {
      this.notificacion.error(mensajeError(error));
    } finally {
      this.cancelando.set(false);
    }
  }
}
