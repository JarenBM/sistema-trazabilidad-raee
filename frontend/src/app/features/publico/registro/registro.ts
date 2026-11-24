import { Component, inject, signal } from '@angular/core';
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
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { Distrito } from '../../../core/models/catalogos.models';
import { AuthService } from '../../../core/services/auth.service';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';

interface RegistroModelo {
  nombres: string;
  apellidos: string;
  correo: string;
  telefono: string;
  ubigeo: string;
  direccion: string;
  password: string;
  confirmarPassword: string;
}

@Component({
  selector: 'app-registro',
  imports: [FormField, FormRoot, RouterLink],
  templateUrl: './registro.html',
})
export class Registro {
  private readonly auth = inject(AuthService);
  private readonly catalogos = inject(CatalogosService);
  private readonly router = inject(Router);

  readonly distritos = rxResource({
    stream: () => this.catalogos.distritos(),
    defaultValue: [] as Distrito[],
  });

  readonly modelo = signal<RegistroModelo>({
    nombres: '',
    apellidos: '',
    correo: '',
    telefono: '',
    ubigeo: '',
    direccion: '',
    password: '',
    confirmarPassword: '',
  });

  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.nombres, { message: 'Ingresa tus nombres.' });
      minLength(camino.nombres, 2, {
        message: 'Los nombres deben tener al menos 2 caracteres.',
      });
      maxLength(camino.nombres, 100, {
        message: 'Los nombres no deben superar los 100 caracteres.',
      });

      required(camino.apellidos, { message: 'Ingresa tus apellidos.' });
      minLength(camino.apellidos, 2, {
        message: 'Los apellidos deben tener al menos 2 caracteres.',
      });
      maxLength(camino.apellidos, 100, {
        message: 'Los apellidos no deben superar los 100 caracteres.',
      });

      required(camino.correo, { message: 'Ingresa tu correo electrónico.' });
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

      required(camino.ubigeo, { message: 'Selecciona tu distrito.' });

      validate(camino.direccion, ({ value }) => {
        const direccion = value();
        if (!direccion) {
          return undefined;
        }
        if (direccion.length < 5 || direccion.length > 200) {
          return {
            kind: 'direccion',
            message: 'La dirección debe tener entre 5 y 200 caracteres.',
          };
        }
        return undefined;
      });

      required(camino.password, { message: 'Crea una contraseña.' });
      minLength(camino.password, 8, {
        message: 'La contraseña debe tener al menos 8 caracteres.',
      });
      maxLength(camino.password, 128, {
        message: 'La contraseña no debe superar los 128 caracteres.',
      });

      required(camino.confirmarPassword, {
        message: 'Confirma tu contraseña.',
      });
      validate(camino.confirmarPassword, ({ value, valueOf }) =>
        value() === valueOf(camino.password)
          ? undefined
          : {
              kind: 'confirmacion',
              message: 'Las contraseñas no coinciden.',
            },
      );
    },
    {
      submission: {
        action: () => this.registrar(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly mostrarPassword = signal(false);
  readonly error = signal<string | null>(null);

  alternarPassword(): void {
    this.mostrarPassword.update((visible) => !visible);
  }

  private async registrar(): Promise<void> {
    this.error.set(null);
    const datos = this.modelo();

    try {
      await firstValueFrom(
        this.auth.registrar({
          nombres: datos.nombres.trim(),
          apellidos: datos.apellidos.trim(),
          correo: datos.correo.trim().toLowerCase(),
          password: datos.password,
          telefono: datos.telefono.trim() || null,
          ubigeo: datos.ubigeo,
          direccion: datos.direccion.trim() || null,
        }),
      );

      try {
        await firstValueFrom(
          this.auth.login(datos.correo.trim().toLowerCase(), datos.password),
        );
        await this.router.navigateByUrl(this.auth.rutaInicio());
      } catch {
        await this.router.navigate(['/login'], {
          queryParams: { registrado: 1 },
        });
      }
    } catch (error) {
      this.error.set(mensajeError(error));
    }
  }
}
