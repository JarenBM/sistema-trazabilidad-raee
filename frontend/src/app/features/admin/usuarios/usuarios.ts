import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import {
  FormField,
  FormRoot,
  email,
  form,
  maxLength,
  minLength,
  required,
  validate,
} from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';

import { Centro, Distrito } from '../../../core/models/catalogos.models';
import { UsuarioListado } from '../../../core/models/usuarios.models';
import { AuthService } from '../../../core/services/auth.service';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { ConfirmacionService } from '../../../core/services/confirmacion.service';
import { NotificacionService } from '../../../core/services/notificacion.service';
import { UsuariosService } from '../../../core/services/usuarios.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';
import { EmptyState } from '../../../shared/components/empty-state/empty-state';
import { EstadoBadge } from '../../../shared/components/estado-badge/estado-badge';
import { Loading } from '../../../shared/components/loading/loading';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { FechaHoraPipe } from '../../../shared/pipes/fecha-hora.pipe';

interface EncargadoModelo {
  nombres: string;
  apellidos: string;
  correo: string;
  telefono: string;
  ubigeo: string;
  direccion: string;
  password: string;
  idCentro: string;
}

@Component({
  selector: 'app-usuarios',
  imports: [
    FormField,
    FormRoot,
    PageHeader,
    EstadoBadge,
    EmptyState,
    Loading,
    FechaHoraPipe,
  ],
  templateUrl: './usuarios.html',
})
export class Usuarios {
  private readonly usuariosService = inject(UsuariosService);
  private readonly catalogos = inject(CatalogosService);
  private readonly confirmacion = inject(ConfirmacionService);
  private readonly notificacion = inject(NotificacionService);
  private readonly auth = inject(AuthService);

  readonly filtroRol = signal('');
  readonly filtroEstado = signal('');
  readonly busqueda = signal('');
  readonly mostrarFormulario = signal(false);
  readonly procesando = signal<number | null>(null);

  readonly usuarios = rxResource({
    stream: () => this.usuariosService.listar(),
    defaultValue: [] as UsuarioListado[],
  });

  readonly distritos = rxResource({
    stream: () => this.catalogos.distritos(),
    defaultValue: [] as Distrito[],
  });

  readonly centros = rxResource({
    stream: () => this.catalogos.centros(true),
    defaultValue: [] as Centro[],
  });

  readonly filtrados = computed(() => {
    const rol = this.filtroRol();
    const estado = this.filtroEstado();
    const texto = this.busqueda().trim().toLowerCase();

    return this.usuarios.value().filter((usuario) => {
      const coincideRol = !rol || usuario.rol === rol;

      let coincideEstado = true;
      if (estado === 'activos') {
        coincideEstado = usuario.activo;
      } else if (estado === 'inactivos') {
        coincideEstado = !usuario.activo;
      }

      const coincideTexto =
        !texto ||
        usuario.nombres.toLowerCase().includes(texto) ||
        usuario.apellidos.toLowerCase().includes(texto) ||
        usuario.correo.toLowerCase().includes(texto) ||
        (usuario.nombre_centro ?? '').toLowerCase().includes(texto);

      return coincideRol && coincideEstado && coincideTexto;
    });
  });

  readonly modelo = signal<EncargadoModelo>(this.modeloVacio());

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.nombres, { message: 'Ingresa los nombres.' });
      minLength(camino.nombres, 2, {
        message: 'Los nombres deben tener al menos 2 caracteres.',
      });
      maxLength(camino.nombres, 100, {
        message: 'Los nombres no deben superar los 100 caracteres.',
      });

      required(camino.apellidos, { message: 'Ingresa los apellidos.' });
      minLength(camino.apellidos, 2, {
        message: 'Los apellidos deben tener al menos 2 caracteres.',
      });
      maxLength(camino.apellidos, 100, {
        message: 'Los apellidos no deben superar los 100 caracteres.',
      });

      required(camino.correo, { message: 'Ingresa el correo del encargado.' });
      email(camino.correo, {
        message: 'Ingresa un correo electrónico válido.',
      });
      maxLength(camino.correo, 100, {
        message: 'El correo no debe superar los 100 caracteres.',
      });

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

      required(camino.ubigeo, { message: 'Selecciona el distrito.' });

      validate(camino.direccion, ({ value }) => {
        if (!value) {
          return undefined;
        }
        if (value.length < 5 || value.length > 200) {
          return {
            kind: 'direccion',
            message: 'La dirección debe tener entre 5 y 200 caracteres.',
          };
        }
        return undefined;
      });

      required(camino.password, { message: 'Asigna una contraseña inicial.' });
      minLength(camino.password, 8, {
        message: 'La contraseña debe tener al menos 8 caracteres.',
      });
      maxLength(camino.password, 128, {
        message: 'La contraseña no debe superar los 128 caracteres.',
      });

      required(camino.idCentro, {
        message: 'Selecciona el centro de acopio del encargado.',
      });
    },
    {
      submission: {
        action: () => this.crearEncargado(),
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
    this.filtroRol.set('');
    this.filtroEstado.set('');
    this.busqueda.set('');
  }

  esMiCuenta(usuario: UsuarioListado): boolean {
    return this.auth.usuario()?.id_usuario === usuario.id_usuario;
  }

  async cambiarEstado(usuario: UsuarioListado): Promise<void> {
    if (this.esMiCuenta(usuario)) {
      this.notificacion.advertencia('No puedes desactivar tu propia cuenta.');
      return;
    }

    const accion = usuario.activo ? 'desactivar' : 'activar';
    const confirmado = await this.confirmacion.confirmar({
      titulo: `${accion === 'desactivar' ? 'Desactivar' : 'Activar'} usuario`,
      mensaje: `¿Deseas ${accion} la cuenta de ${usuario.nombres} ${usuario.apellidos}?`,
      textoConfirmar: `Sí, ${accion}`,
      textoCancelar: 'Cancelar',
      peligro: usuario.activo,
    });

    if (!confirmado) {
      return;
    }

    this.procesando.set(usuario.id_usuario);
    try {
      await firstValueFrom(
        this.usuariosService.cambiarEstado(usuario.id_usuario, !usuario.activo),
      );
      this.notificacion.exito(
        `Usuario ${accion === 'desactivar' ? 'desactivado' : 'activado'} correctamente.`,
      );
      this.usuarios.reload();
    } catch (error) {
      this.notificacion.error(mensajeError(error));
    } finally {
      this.procesando.set(null);
    }
  }

  private modeloVacio(): EncargadoModelo {
    return {
      nombres: '',
      apellidos: '',
      correo: '',
      telefono: '',
      ubigeo: '',
      direccion: '',
      password: '',
      idCentro: '',
    };
  }

  private async crearEncargado(): Promise<void> {
    this.error.set(null);
    const datos = this.modelo();

    try {
      await firstValueFrom(
        this.usuariosService.crearEncargado({
          nombres: datos.nombres.trim(),
          apellidos: datos.apellidos.trim(),
          correo: datos.correo.trim().toLowerCase(),
          password: datos.password,
          telefono: datos.telefono.trim() || null,
          ubigeo: datos.ubigeo,
          direccion: datos.direccion.trim() || null,
          id_centro: Number(datos.idCentro),
        }),
      );
      this.notificacion.exito('Encargado creado correctamente.');
      this.mostrarFormulario.set(false);
      this.modelo.set(this.modeloVacio());
      this.formulario().reset();
      this.usuarios.reload();
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }
}
