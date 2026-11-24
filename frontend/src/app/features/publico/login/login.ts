import { Component, inject, signal } from '@angular/core';
import {
  FormField,
  FormRoot,
  email,
  form,
  minLength,
  required,
} from '@angular/forms/signals';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AuthService } from '../../../core/services/auth.service';
import { mensajeError } from '../../../core/utils/http-error.util';
import { marcarTocados } from '../../../core/utils/form.util';

@Component({
  selector: 'app-login',
  imports: [FormField, FormRoot, RouterLink],
  templateUrl: './login.html',
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  readonly modelo = signal({ correo: '', password: '' });
  readonly formulario = form(
    this.modelo,
    (camino) => {
      required(camino.correo, { message: 'Ingresa tu correo electrónico.' });
      email(camino.correo, {
        message: 'Ingresa un correo electrónico válido.',
      });
      required(camino.password, { message: 'Ingresa tu contraseña.' });
      minLength(camino.password, 8, {
        message: 'La contraseña debe tener al menos 8 caracteres.',
      });
    },
    {
      submission: {
        action: () => this.ingresar(),
        onInvalid: () => marcarTocados(this.formulario),
      },
    },
  );

  readonly mostrarPassword = signal(false);
  readonly error = signal<string | null>(null);

  readonly registrado = this.route.snapshot.queryParamMap.get('registrado') === '1';
  readonly sesionExpirada =
    this.route.snapshot.queryParamMap.get('sesionExpirada') === '1';

  alternarPassword(): void {
    this.mostrarPassword.update((visible) => !visible);
  }

  private async ingresar(): Promise<void> {
    this.error.set(null);
    this.modelo.update((valor) => ({
      ...valor,
      correo: valor.correo.trim().toLowerCase(),
    }));

    try {
      await firstValueFrom(
        this.auth.login(this.modelo().correo, this.modelo().password),
      );

      const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
      const destino =
        returnUrl && returnUrl.startsWith('/')
          ? returnUrl
          : this.auth.rutaInicio();

      await this.router.navigateByUrl(destino);
    } catch (error) {
      this.error.set(
        error instanceof HttpErrorResponse && error.status === 401
          ? 'Correo o contraseña incorrectos. Verifica tus datos e inténtalo nuevamente.'
          : mensajeError(error),
      );
    }
  }
}
