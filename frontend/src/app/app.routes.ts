import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { publicOnlyGuard } from './core/guards/public-only.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    title: 'RAEE Huancayo | Gestión y trazabilidad',
    loadComponent: () =>
      import('./features/publico/home/home').then((m) => m.Home),
  },
  {
    path: 'rastreo',
    title: 'Consulta de trazabilidad | RAEE Huancayo',
    loadComponent: () =>
      import('./features/publico/rastreo/rastreo').then((m) => m.Rastreo),
  },
  {
    path: 'centros',
    title: 'Centros de acopio | RAEE Huancayo',
    loadComponent: () =>
      import('./features/publico/centros/centros').then((m) => m.Centros),
  },
  {
    path: 'login',
    title: 'Iniciar sesión | RAEE Huancayo',
    canActivate: [publicOnlyGuard],
    loadComponent: () =>
      import('./features/publico/login/login').then((m) => m.Login),
  },
  {
    path: 'registro',
    title: 'Crear cuenta | RAEE Huancayo',
    canActivate: [publicOnlyGuard],
    loadComponent: () =>
      import('./features/publico/registro/registro').then((m) => m.Registro),
  },
  {
    path: 'ciudadano',
    title: 'Mis equipos | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('CIUDADANO')],
    loadComponent: () =>
      import('./features/ciudadano/mis-raee/mis-raee').then((m) => m.MisRaee),
  },
  {
    path: 'ciudadano/registrar',
    title: 'Registrar equipo | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('CIUDADANO')],
    loadComponent: () =>
      import('./features/ciudadano/registrar-raee/registrar-raee').then(
        (m) => m.RegistrarRaee,
      ),
  },
  {
    path: 'ciudadano/solicitud/:idRaee',
    title: 'Programar entrega | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('CIUDADANO')],
    loadComponent: () =>
      import('./features/ciudadano/nueva-solicitud/nueva-solicitud').then(
        (m) => m.NuevaSolicitud,
      ),
  },
  {
    path: 'encargado',
    title: 'Bandeja del centro | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('ENCARGADO')],
    loadComponent: () =>
      import('./features/encargado/bandeja/bandeja').then((m) => m.Bandeja),
  },
  {
    path: 'encargado/evaluar/:idRaee',
    title: 'Evaluación técnica | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('ENCARGADO')],
    loadComponent: () =>
      import('./features/encargado/evaluacion/evaluacion').then(
        (m) => m.Evaluacion,
      ),
  },
  {
    path: 'admin',
    title: 'Panel de control | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('ADMIN')],
    loadComponent: () =>
      import('./features/admin/dashboard/dashboard').then((m) => m.Dashboard),
  },
  {
    path: 'admin/centros',
    title: 'Gestión de centros | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('ADMIN')],
    loadComponent: () =>
      import('./features/admin/centros/centros-admin').then(
        (m) => m.CentrosAdmin,
      ),
  },
  {
    path: 'admin/usuarios',
    title: 'Gestión de usuarios | RAEE Huancayo',
    canActivate: [authGuard, roleGuard('ADMIN')],
    loadComponent: () =>
      import('./features/admin/usuarios/usuarios').then((m) => m.Usuarios),
  },
  {
    path: '**',
    title: 'Página no encontrada | RAEE Huancayo',
    loadComponent: () =>
      import('./features/no-encontrado/no-encontrado').then(
        (m) => m.NoEncontrado,
      ),
  },
];
