import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-no-encontrado',
  imports: [RouterLink],
  template: `
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-6 text-center">
          <div class="display-1 fw-bold text-raee">404</div>
          <h1 class="h3 mt-2">Página no encontrada</h1>
          <p class="text-muted-soft mb-4">
            La dirección que ingresaste no existe o el contenido fue movido.
          </p>
          <div class="d-flex flex-column flex-sm-row justify-content-center gap-2">
            <a class="btn btn-raee" routerLink="/">
              <i class="bi bi-house-door me-1"></i>Ir al inicio
            </a>
            <a class="btn btn-outline-raee" routerLink="/rastreo">
              <i class="bi bi-search me-1"></i>Consultar trazabilidad
            </a>
            <a class="btn btn-outline-secondary" routerLink="/login">
              <i class="bi bi-box-arrow-in-right me-1"></i>Iniciar sesión
            </a>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class NoEncontrado {}
