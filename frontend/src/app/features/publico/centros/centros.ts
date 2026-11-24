import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { Centro, Distrito } from '../../../core/models/catalogos.models';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { Loading } from '../../../shared/components/loading/loading';

@Component({
  selector: 'app-centros',
  imports: [FormsModule, RouterLink, EmptyState, Loading],
  templateUrl: './centros.html',
})
export class Centros {
  private readonly catalogos = inject(CatalogosService);

  readonly distritoSeleccionado = signal('');
  readonly busqueda = signal('');

  readonly distritos = rxResource({
    stream: () => this.catalogos.distritos(),
    defaultValue: [] as Distrito[],
  });

  readonly centros = rxResource({
    stream: () => this.catalogos.centros(true),
    defaultValue: [] as Centro[],
  });

  readonly centrosFiltrados = computed(() => {
    const distrito = this.distritoSeleccionado();
    const texto = this.busqueda().trim().toLowerCase();

    return this.centros.value().filter((centro) => {
      const coincideDistrito = !distrito || centro.ubigeo === distrito;
      const coincideTexto =
        !texto ||
        centro.nombre_centro.toLowerCase().includes(texto) ||
        centro.direccion.toLowerCase().includes(texto);
      return coincideDistrito && coincideTexto;
    });
  });

  limpiar(): void {
    this.distritoSeleccionado.set('');
    this.busqueda.set('');
  }

  enlaceMapa(centro: Centro): string {
    const consulta =
      centro.latitud !== null && centro.longitud !== null
        ? `${centro.latitud},${centro.longitud}`
        : `${centro.nombre_centro}, ${centro.direccion}, ${centro.distrito}, Huancayo, Perú`;
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(consulta)}`;
  }
}
