import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { ETIQUETA_ROL } from '../../../core/models/auth.models';
import { AuthService } from '../../../core/services/auth.service';

interface Enlace {
  ruta: string;
  etiqueta: string;
  icono: string;
}

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class Navbar {
  readonly auth = inject(AuthService);
  readonly menuAbierto = signal(false);
  readonly cuentaAbierta = signal(false);

  readonly etiquetaRol = computed(() => {
    const rol = this.auth.rol();
    return rol ? ETIQUETA_ROL[rol] : '';
  });

  readonly enlacesPublicos: Enlace[] = [
    { ruta: '/', etiqueta: 'Inicio', icono: 'bi-house-door' },
    { ruta: '/rastreo', etiqueta: 'Trazabilidad', icono: 'bi-search' },
    { ruta: '/centros', etiqueta: 'Centros de acopio', icono: 'bi-geo-alt' },
  ];

  readonly enlacesRol = computed<Enlace[]>(() => {
    switch (this.auth.rol()) {
      case 'CIUDADANO':
        return [
          { ruta: '/ciudadano', etiqueta: 'Mis equipos', icono: 'bi-pc-display' },
          {
            ruta: '/ciudadano/registrar',
            etiqueta: 'Registrar equipo',
            icono: 'bi-plus-square',
          },
        ];
      case 'ENCARGADO':
        return [
          {
            ruta: '/encargado',
            etiqueta: 'Bandeja del centro',
            icono: 'bi-inbox',
          },
        ];
      case 'ADMIN':
        return [
          { ruta: '/admin', etiqueta: 'Panel', icono: 'bi-speedometer2' },
          {
            ruta: '/admin/centros',
            etiqueta: 'Centros',
            icono: 'bi-buildings',
          },
          {
            ruta: '/admin/usuarios',
            etiqueta: 'Usuarios',
            icono: 'bi-people',
          },
        ];
      default:
        return [];
    }
  });

  alternarMenu(): void {
    this.menuAbierto.update((abierto) => !abierto);
    this.cuentaAbierta.set(false);
  }

  alternarCuenta(): void {
    this.cuentaAbierta.update((abierta) => !abierta);
  }

  cerrarMenus(): void {
    this.menuAbierto.set(false);
    this.cuentaAbierta.set(false);
  }

  salir(): void {
    this.cerrarMenus();
    this.auth.cerrarSesion();
  }
}
