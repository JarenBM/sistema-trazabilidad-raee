import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-footer',
  imports: [RouterLink],
  template: `
    <footer class="footer-raee mt-5">
      <div class="container py-4">
        <div class="row g-4 align-items-start">
          <div class="col-lg-5">
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="brand-mark"><i class="bi bi-recycle"></i></span>
              <span class="fw-bold text-white">RAEE Huancayo</span>
            </div>
            <p class="small mb-2 text-white-50">
              Sistema municipal para la gestión y trazabilidad de residuos de
              aparatos eléctricos y electrónicos en Huancayo, Junín.
            </p>
            <p class="small mb-0 text-white-50">
              <i class="bi bi-geo-alt me-1"></i>Huancayo, Junín — Perú
            </p>
          </div>

          <div class="col-6 col-lg-3">
            <h2 class="h6 text-white">Servicios</h2>
            <ul class="list-unstyled small mb-0">
              <li class="mb-1"><a class="footer-link" routerLink="/rastreo">Consultar trazabilidad</a></li>
              <li class="mb-1"><a class="footer-link" routerLink="/centros">Centros de acopio</a></li>
              <li class="mb-1"><a class="footer-link" routerLink="/registro">Registrar mi equipo</a></li>
              <li><a class="footer-link" routerLink="/login">Acceso de usuarios</a></li>
            </ul>
          </div>

          <div class="col-6 col-lg-4">
            <h2 class="h6 text-white">Compromiso ambiental</h2>
            <p class="small text-white-50 mb-2">
              La consulta pública no muestra datos personales. Solo se comparte
              el estado y el historial del equipo registrado.
            </p>
            <p class="small text-white-50 mb-0">
              Manejo responsable de RAEE conforme a la normativa peruana.
            </p>
          </div>
        </div>

        <hr class="border-light opacity-25 my-3" />

        <div class="d-flex flex-column flex-md-row justify-content-between gap-2 small text-white-50">
          <span>© {{ anio }} Municipalidad Provincial de Huancayo.</span>
          <span>Sistema de gestión y trazabilidad de RAEE.</span>
        </div>
      </div>
    </footer>
  `,
  styles: [
    `
      .footer-raee {
        background: #103c2b;
        color: #fff;
      }

      .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 0.7rem;
        background: rgba(255, 255, 255, 0.14);
        font-size: 1.15rem;
      }

      .footer-link {
        color: rgba(255, 255, 255, 0.72);
        text-decoration: none;
      }

      .footer-link:hover {
        color: #fff;
        text-decoration: underline;
      }
    `,
  ],
})
export class Footer {
  readonly anio = new Date().getFullYear();
}
