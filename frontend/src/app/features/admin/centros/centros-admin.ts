import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import {
  FormField,
  FormRoot,
  form,
  max,
  maxLength,
  min,
  minLength,
  required,
  validate,
} from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';

import { Centro, Distrito } from '../../../core/models/catalogos.models';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { CentrosService } from '../../../core/services/centros.service';
import { ConfirmacionService } from '../../../core/services/confirmacion.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';

interface CentroModelo {
  nombreCentro: string;
  direccion: string;
  telefono: string;
  ubigeo: string;
  latitud: number | null;
  longitud: number | null;
}

@Component({
  selector: 'app-centros-admin',
  imports: [
    FormField,
    FormRoot,
    PageHeader,
    EmptyState,
    Loading,
  ],
  templateUrl: './centros-admin.html',
})
export class CentrosAdmin {
  private readonly catalogos = inject(CatalogosService);
  private readonly centrosService = inject(CentrosService);
  private readonly confirmacion = inject(ConfirmacionService);
  private readonly notificacion = inject(NotificacionService);

  readonly filtroDistrito = signal('');
  readonly filtroEstado = signal('');
  readonly busqueda = signal('');
  readonly mostrarFormulario = signal(false);
  readonly procesando = signal<number | null>(null);

  readonly centros = rxResource({
    stream: () => this.catalogos.centros(false),
    defaultValue: [] as Centro[],
  });

  readonly distritos = rxResource({
    stream: () => this.catalogos.distritos(),
    defaultValue: [] as Distrito[],
  });

  readonly filtrados = computed(() => {
    const distrito = this.filtroDistrito();
    const estado = this.filtroEstado();
    const texto = this.busqueda().trim().toLowerCase();

    return this.centros.value().filter((centro) => {
      const coincideDistrito = !distrito || centro.ubigeo === distrito;

      let coincideEstado = true;
      if (estado === 'activos') {
        coincideEstado = centro.activo;
      } else if (estado === 'inactivos') {
        coincideEstado = !centro.activo;
      }

      const coincideTexto =
        !texto ||
        centro.nombre_centro.toLowerCase().includes(texto) ||
        centro.direccion.toLowerCase().includes(texto) ||
        centro.distrito.toLowerCase().includes(texto);

      return coincideDistrito && coincideEstado && coincideTexto;
    });
  });

  readonly modelo = signal<CentroModelo>(this.modeloVacio());

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.nombreCentro, { message: 'Ingresa el nombre del centro.' });
      minLength(camino.nombreCentro, 3, {
        message: 'El nombre debe tener al menos 3 caracteres.',
      });
      maxLength(camino.nombreCentro, 100, {
        message: 'El nombre no debe superar los 100 caracteres.',
      });

      required(camino.direccion, { message: 'Ingresa la dirección del centro.' });
      minLength(camino.direccion, 5, {
        message: 'La dirección debe tener al menos 5 caracteres.',
      });
      maxLength(camino.direccion, 200, {
        message: 'La dirección no debe superar los 200 caracteres.',
      });

      required(camino.ubigeo, { message: 'Selecciona el distrito del centro.' });

      validate(camino.telefono, ({ value }) => {
        const telefono = value();
        if (!telefono) {
          return undefined;
        }
        if (!/^[0-9+\-\s]+$/.test(telefono)) {
          return {
            kind: 'telefono',
            message: 'El teléfono solo admite números, espacios, + y guiones.',
          };
        }
        if (telefono.length < 6 || telefono.length > 20) {
          return {
            kind: 'telefono',
            message: 'El teléfono debe tener entre 6 y 20 caracteres.',
          };
        }
        return undefined;
      });

      min(camino.latitud, -90, {
        message: 'La latitud debe estar entre -90 y 90.',
      });
      max(camino.latitud, 90, {
        message: 'La latitud debe estar entre -90 y 90.',
      });
      min(camino.longitud, -180, {
        message: 'La longitud debe estar entre -180 y 180.',
      });
      max(camino.longitud, 180, {
        message: 'La longitud debe estar entre -180 y 180.',
      });
    },
    {
      submission: {
        action: () => this.crearCentro(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly error = signal<string | null>(null);

  abrirFormulario(): void {
    this.modelo.set(this.modeloVacio());
    this.formulario().reset();
    this.error.set(null);
    this.mostrarFormulario.set(true);
  }

  cerrarFormulario(): void {
    this.mostrarFormulario.set(false);
  }

  limpiar(): void {
    this.filtroDistrito.set('');
    this.filtroEstado.set('');
    this.busqueda.set('');
  }

  async cambiarEstado(centro: Centro): Promise<void> {
    const accion = centro.activo ? 'desactivar' : 'activar';
    const confirmado = await this.confirmacion.confirmar({
      titulo: `${accion === 'desactivar' ? 'Desactivar' : 'Activar'} centro`,
      mensaje: `¿Deseas ${accion} el centro ${centro.nombre_centro}?`,
      textoConfirmar: `Sí, ${accion}`,
      textoCancelar: 'Cancelar',
      peligro: centro.activo,
    });

    if (!confirmado) {
      return;
    }

    this.procesando.set(centro.id_centro);
    try {
      await firstValueFrom(
        this.centrosService.cambiarEstado(centro.id_centro, !centro.activo),
      );
      this.notificacion.exito(
        `Centro ${accion === 'desactivar' ? 'desactivado' : 'activado'} correctamente.`,
      );
      this.centros.reload();
    } catch (error) {
      this.notificacion.error(mensajeError(error));
    } finally {
      this.procesando.set(null);
    }
  }

  private modeloVacio(): CentroModelo {
    return {
      nombreCentro: '',
      direccion: '',
      telefono: '',
      ubigeo: '',
      latitud: null,
      longitud: null,
    };
  }

  private async crearCentro(): Promise<void> {
    this.error.set(null);
    const datos = this.modelo();

    try {
      await firstValueFrom(
        this.centrosService.crear({
          nombre_centro: datos.nombreCentro.trim(),
          direccion: datos.direccion.trim(),
          telefono: datos.telefono.trim() || null,
          ubigeo: datos.ubigeo,
          latitud: datos.latitud,
          longitud: datos.longitud,
        }),
      );
      this.notificacion.exito('Centro de acopio creado correctamente.');
      this.mostrarFormulario.set(false);
      this.modelo.set(this.modeloVacio());
      this.formulario().reset();
      this.centros.reload();
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }
}
