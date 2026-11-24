export type Rol = 'CIUDADANO' | 'ENCARGADO' | 'ADMIN';

export interface UsuarioSesion {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  correo: string;
  rol: Rol;
  id_centro: number | null;
  activo: boolean;
}

export interface TokenRespuesta {
  access_token: string;
  token_type: string;
  expira_en_minutos: number;
  usuario: UsuarioSesion;
}

export interface RegistroRequest {
  nombres: string;
  apellidos: string;
  correo: string;
  password: string;
  telefono: string | null;
  ubigeo: string;
  direccion: string | null;
}

export interface Credenciales {
  correo: string;
  password: string;
}

export const ETIQUETA_ROL: Record<Rol, string> = {
  CIUDADANO: 'Ciudadano',
  ENCARGADO: 'Encargado de centro',
  ADMIN: 'Administrador',
};
