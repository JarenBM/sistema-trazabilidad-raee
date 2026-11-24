import { Component, inject, signal } from '@angular/core';
import { FormField, FormRoot, form, pattern, required } from '@angular/forms/signals';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { RastreoRespuesta } from '../../../core/models/publico.models';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { PublicoService } from '../../../core/services/publico.service';
import { normalizarCodigo } from '../../../core/utils/codigo.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { esNoEncontrado, mensajeError } from '../../../core/utils/http-error.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { Timeline } from '../../../shared/components/timeline/timeline';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';
import { PesoKgPipe } from '../../../shared/pipes/peso-kg.pipe';

@Component({
  selector: 'app-rastreo',
  imports: [
    FormField,
    FormRoot,
    RouterLink,
    Timeline,
    EstadoBadge,
    FechaHoraPipe,
    PesoKgPipe,
    Loading,
    EmptyState,
  ],
  templateUrl: './rastreo.html',
  styleUrl: './rastreo.css',
})
export class Rastreo {
  private readonly publico = inject(PublicoService);
  private readonly notificacion = inject(NotificacionService);
  private readonly route = inject(ActivatedRoute);

  readonly modelo = signal({ codigo: '' });
  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.codigo, {
        message: 'Ingresa el código de seguimiento de tu equipo.',
      });
      pattern(camino.codigo, /^RAEE-\d{4}-\d{4}$/i, {
        message: 'El formato debe ser RAEE-AAAA-0000, por ejemplo RAEE-2026-0001.',
      });
    },
    {
      submission: {
        action: () => this.buscar(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly resultado = signal<RastreoRespuesta | null>(null);
  readonly error = signal<string | null>(null);
  readonly noEncontrado = signal(false);
  readonly buscado = signal(false);
  readonly cargando = signal(false);

  constructor() {
    const codigo = this.route.snapshot.queryParamMap.get('codigo');
    if (codigo) {
      this.modelo.set({ codigo });
      void this.buscar();
    }
  }

  usarEjemplo(codigo: string): void {
    this.modelo.set({ codigo });
    void this.buscar();
  }

  async buscar(): Promise<void> {
    const codigo = normalizarCodigo(this.modelo().codigo);
    this.buscado.set(true);
    this.cargando.set(true);
    this.error.set(null);
    this.noEncontrado.set(false);
    this.resultado.set(null);

    try {
      const respuesta = await firstValueFrom(this.publico.rastrear(codigo));
      this.resultado.set(respuesta);
    } catch (error) {
      if (esNoEncontrado(error)) {
        this.noEncontrado.set(true);
      } else {
        this.error.set(mensajeError(error));
      }
    } finally {
      this.cargando.set(false);
    }
  }

  async copiar(codigo: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(codigo);
      this.notificacion.exito('Código copiado al portapapeles.');
    } catch {
      this.notificacion.advertencia(
        'No se pudo copiar automáticamente. Selecciona el código manualmente.',
      );
    }
  }
}
