import { Rol } from './auth.models';

export interface UsuarioListado {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  correo: string;
  telefono: string | null;
  rol: Rol;
  distrito: string;
  nombre_centro: string | null;
  activo: boolean;
  fecha_registro: string;
}

export interface EncargadoCrearRequest {
  nombres: string;
  apellidos: string;
  correo: string;
  password: string;
  telefono: string | null;
  ubigeo: string;
  direccion: string | null;
  id_centro: number;
}

export interface UsuarioCreado {
  id_usuario: number;
  correo: string;
  rol: Rol;
}

export interface UsuarioEstadoRequest {
  activo: boolean;
}

export interface EstadoActualizado {
  actualizado: boolean;
}
