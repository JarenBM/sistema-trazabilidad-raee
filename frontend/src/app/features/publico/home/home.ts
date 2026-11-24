import { Component, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { Categoria, Centro, Distrito } from '../../../core/models/catalogos.models';
import { CatalogosService } from '../../../core/services/catalogos.service';

@Component({
  selector: 'app-home',
  imports: [RouterLink, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  private readonly catalogos = inject(CatalogosService);
  private readonly router = inject(Router);

  readonly codigo = signal('');

  readonly categorias = rxResource({
    stream: () => this.catalogos.categorias(),
    defaultValue: [] as Categoria[],
  });

  readonly centros = rxResource({
    stream: () => this.catalogos.centros(true),
    defaultValue: [] as Centro[],
  });

  readonly distritos = rxResource({
    stream: () => this.catalogos.distritos(),
    defaultValue: [] as Distrito[],
  });

  readonly pasos = [
    {
      icono: 'bi-person-plus',
      titulo: 'Crea tu cuenta',
      texto: 'Regístrate con tus datos básicos para identificar tus equipos.',
    },
    {
      icono: 'bi-pc-display',
      titulo: 'Registra tu equipo',
      texto: 'Indica categoría, marca y modelo. Recibirás un código único.',
    },
    {
      icono: 'bi-calendar-check',
      titulo: 'Programa la entrega',
      texto: 'Elige un centro de acopio y la fecha para entregar tu RAEE.',
    },
    {
      icono: 'bi-search',
      titulo: 'Sigue la trazabilidad',
      texto: 'Consulta el estado y el destino final con tu código de seguimiento.',
    },
  ];

  buscar(): void {
    const codigo = this.codigo().trim();
    void this.router.navigate(['/rastreo'], {
      queryParams: codigo ? { codigo } : {},
    });
  }
}
