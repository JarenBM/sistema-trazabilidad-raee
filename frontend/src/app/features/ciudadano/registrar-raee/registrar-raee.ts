import { Component, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import {
  FormField,
  FormRoot,
  form,
  maxLength,
  required,
} from '@angular/forms/signals';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { Categoria } from '../../../core/models/catalogos.models';
import { RaeeRegistrado } from '../../../core/models/raee.models';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { RaeeService } from '../../../core/services/raee.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';

@Component({
  selector: 'app-registrar-raee',
  imports: [FormField, FormRoot, RouterLink, PageHeader, Loading],
  templateUrl: './registrar-raee.html',
})
export class RegistrarRaee {
  private readonly raee = inject(RaeeService);
  private readonly catalogos = inject(CatalogosService);
  private readonly notificacion = inject(NotificacionService);

  readonly categorias = rxResource({
    stream: () => this.catalogos.categorias(),
    defaultValue: [] as Categoria[],
  });

  readonly modelo = signal({
    idCategoria: '',
    marca: '',
    modelo: '',
    descripcion: '',
  });

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.idCategoria, {
        message: 'Selecciona la categoría del equipo.',
      });
      required(camino.marca, { message: 'Ingresa la marca del equipo.' });
      maxLength(camino.marca, 50, {
        message: 'La marca no debe superar los 50 caracteres.',
      });
      required(camino.modelo, { message: 'Ingresa el modelo del equipo.' });
      maxLength(camino.modelo, 50, {
        message: 'El modelo no debe superar los 50 caracteres.',
      });
      maxLength(camino.descripcion, 500, {
        message: 'La descripción no debe superar los 500 caracteres.',
      });
    },
    {
      submission: {
        action: () => this.registrarEquipo(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly error = signal<string | null>(null);
  readonly registrado = signal<RaeeRegistrado | null>(null);

  async copiarCodigo(): Promise<void> {
    const registro = this.registrado();
    if (!registro) {
      return;
    }
    try {
      await navigator.clipboard.writeText(registro.codigo_seguimiento);
      this.notificacion.exito('Código copiado al portapapeles.');
    } catch {
      this.notificacion.advertencia(
        'No se pudo copiar automáticamente. Anota el código manualmente.',
      );
    }
  }

  registrarOtro(): void {
    this.registrado.set(null);
    this.error.set(null);
    this.modelo.set({
      idCategoria: '',
      marca: '',
      modelo: '',
      descripcion: '',
    });
    this.formulario().reset();
  }

  private async registrarEquipo(): Promise<void> {
    this.error.set(null);
    const datos = this.modelo();

    try {
      const respuesta = await firstValueFrom(
        this.raee.registrar({
          id_categoria: Number(datos.idCategoria),
          marca: datos.marca.trim(),
          modelo: datos.modelo.trim(),
          descripcion: datos.descripcion.trim() || null,
        }),
      );
      this.registrado.set(respuesta);
      this.notificacion.exito('Equipo registrado correctamente.');
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }
}
