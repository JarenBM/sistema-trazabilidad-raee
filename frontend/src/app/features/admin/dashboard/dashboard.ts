import { DecimalPipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { ReporteResumen } from '../../../core/models/reportes.models';
import { ReportesService } from '../../../core/services/reportes.service';
import { porcentaje } from '../../../core/utils/numero.util';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PesoKgPipe } from '../../../shared/pipes/peso-kg.pipe';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, DecimalPipe, Loading, PageHeader, PesoKgPipe],
  templateUrl: './dashboard.html',
})
export class Dashboard {
  private readonly reportes = inject(ReportesService);

  readonly resumen = rxResource({
    stream: () => this.reportes.resumen(),
  });

  readonly distribucion = computed(() => {
    const datos = this.resumen.value();
    if (!datos) {
      return [];
    }
    const total = datos.total_dispositivos || 0;
    return [
      {
        etiqueta: 'Registrados',
        valor: datos.total_registrados,
        clase: 'bg-secondary',
        porcentaje: porcentaje(datos.total_registrados, total),
      },
      {
        etiqueta: 'Solicitados',
        valor: datos.total_solicitados,
        clase: 'bg-warning',
        porcentaje: porcentaje(datos.total_solicitados, total),
      },
      {
        etiqueta: 'Recibidos',
        valor: datos.total_recibidos,
        clase: 'bg-info',
        porcentaje: porcentaje(datos.total_recibidos, total),
      },
      {
        etiqueta: 'Evaluados',
        valor: datos.total_evaluados,
        clase: 'bg-success',
        porcentaje: porcentaje(datos.total_evaluados, total),
      },
    ];
  });

  readonly proporcionValorizacion = computed(() => {
    const datos = this.resumen.value();
    if (!datos) {
      return 0;
    }
    return porcentaje(
      datos.peso_valorizado_kg,
      datos.peso_total_kg,
    );
  });

  readonly proporcionDisposicion = computed(() => {
    const datos = this.resumen.value();
    if (!datos) {
      return 0;
    }
    return porcentaje(
      datos.peso_disposicion_final_kg,
      datos.peso_total_kg,
    );
  });

  kpis(datos: ReporteResumen) {
    return [
      {
        etiqueta: 'Total de equipos',
        valor: datos.total_dispositivos,
        icono: 'bi-pc-display',
        clase: 'text-raee',
      },
      {
        etiqueta: 'Registrados',
        valor: datos.total_registrados,
        icono: 'bi-file-earmark-plus',
        clase: 'text-secondary',
      },
      {
        etiqueta: 'Solicitados',
        valor: datos.total_solicitados,
        icono: 'bi-truck',
        clase: 'text-warning',
      },
      {
        etiqueta: 'Recibidos',
        valor: datos.total_recibidos,
        icono: 'bi-box-seam',
        clase: 'text-info',
      },
      {
        etiqueta: 'Evaluados',
        valor: datos.total_evaluados,
        icono: 'bi-check2-circle',
        clase: 'text-success',
      },
    ];
  }
}
