import { Component, computed, inject, input, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import {
  FormField,
  FormRoot,
  form,
  max,
  maxLength,
  min,
  required,
} from '@angular/forms/signals';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { TipoDestino } from '../../../core/models/catalogos.models';
import {
  CondicionFisica,
  ETIQUETA_CONDICION,
  EvaluacionRegistrada,
} from '../../../core/models/evaluaciones.models';
import { SolicitudCentro } from '../../../core/models/solicitudes.models';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { EvaluacionesService } from '../../../core/services/evaluaciones.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { SolicitudesService } from '../../../core/services/solicitudes.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';

interface EvaluacionModelo {
  idDestino: string;
  condicion: CondicionFisica | '';
  esOperativo: boolean;
  peso: number | null;
  observaciones: string;
}

@Component({
  selector: 'app-evaluacion',
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
  templateUrl: './evaluacion.html',
})
export class Evaluacion {
  readonly idRaee = input.required<string>();

  private readonly solicitudesService = inject(SolicitudesService);
  private readonly catalogos = inject(CatalogosService);
  private readonly evaluaciones = inject(EvaluacionesService);
  private readonly notificacion = inject(NotificacionService);

  private readonly solicitudDesdeNavegacion = this.leerSolicitudNavegacion();

  readonly solicitudes = rxResource({
    stream: () => this.solicitudesService.porCentro(),
    defaultValue: [] as SolicitudCentro[],
  });

  readonly destinos = rxResource({
    stream: () => this.catalogos.tiposDestino(),
    defaultValue: [] as TipoDestino[],
  });

  readonly solicitud = computed<SolicitudCentro | undefined>(() => {
    const idRaee = Number(this.idRaee());
    const desdeBandeja = this.solicitudDesdeNavegacion;
    const lista = this.solicitudes.value();

    return (
      lista.find(
        (item) =>
          item.id_raee === idRaee && item.estado_raee_actual === 'RECIBIDO',
      ) ??
      lista.find((item) => item.id_raee === idRaee) ??
      (desdeBandeja?.id_raee === idRaee ? desdeBandeja : undefined)
    );
  });

  readonly condiciones: Array<{ valor: CondicionFisica; etiqueta: string }> = [
    { valor: 'EXCELENTE', etiqueta: ETIQUETA_CONDICION.EXCELENTE },
    { valor: 'REGULAR', etiqueta: ETIQUETA_CONDICION.REGULAR },
    { valor: 'INSERVIBLE', etiqueta: ETIQUETA_CONDICION.INSERVIBLE },
  ];

  readonly modelo = signal<EvaluacionModelo>({
    idDestino: '',
    condicion: '',
    esOperativo: false,
    peso: null,
    observaciones: '',
  });

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.idDestino, {
        message: 'Selecciona el tipo de destino del equipo.',
      });
      required(camino.condicion, {
        message: 'Selecciona la condición física del equipo.',
      });
      required(camino.peso, {
        message: 'Ingresa el peso del equipo en kilogramos.',
      });
      min(camino.peso, 0.01, {
        message: 'El peso debe ser mayor a 0 kg.',
      });
      max(camino.peso, 9999.99, {
        message: 'El peso no debe superar los 9999.99 kg.',
      });
      maxLength(camino.observaciones, 1000, {
        message: 'Las observaciones no deben superar los 1000 caracteres.',
      });
    },
    {
      submission: {
        action: () => this.registrarEvaluacion(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly destinoSeleccionado = computed(() =>
    this.destinos
      .value()
      .find((destino) => destino.id_tipo_destino === Number(this.modelo().idDestino)),
  );

  readonly error = signal<string | null>(null);
  readonly resultado = signal<EvaluacionRegistrada | null>(null);

  private leerSolicitudNavegacion(): SolicitudCentro | null {
    const estado = window.history.state as { solicitud?: SolicitudCentro };
    return estado?.solicitud ?? null;
  }

  private async registrarEvaluacion(): Promise<void> {
    this.error.set(null);
    const solicitud = this.solicitud();

    if (!solicitud) {
      this.error.set('No se encontró la solicitud del equipo.');
      return;
    }
    if (solicitud.estado_raee_actual !== 'RECIBIDO') {
      this.error.set('El equipo debe estar recibido para poder evaluarlo.');
      return;
    }

    const datos = this.modelo();
    const peso = datos.peso;

    if (!peso || !datos.condicion) {
      this.error.set('Completa los datos obligatorios de la evaluación.');
      return;
    }

    try {
      const respuesta = await firstValueFrom(
        this.evaluaciones.registrar({
          id_raee: Number(this.idRaee()),
          id_tipo_destino: Number(datos.idDestino),
          condicion_fisica: datos.condicion,
          es_operativo: datos.esOperativo,
          peso_kg: peso,
          observaciones: datos.observaciones.trim() || null,
        }),
      );
      this.resultado.set(respuesta);
      this.notificacion.exito('Evaluación técnica registrada correctamente.');
      this.solicitudes.reload();
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }
}
