export interface EstadoVisual {
  etiqueta: string;
  clase: string;
  icono: string;
}

const ESTADOS_RAEE: Record<string, EstadoVisual> = {
  REGISTRADO: {
    etiqueta: 'Registrado',
    clase: 'text-bg-secondary',
    icono: 'bi-file-earmark-plus',
  },
  SOLICITADO: {
    etiqueta: 'Solicitado',
    clase: 'text-bg-warning',
    icono: 'bi-truck',
  },
  RECIBIDO: {
    etiqueta: 'Recibido',
    clase: 'text-bg-info',
    icono: 'bi-box-seam',
  },
  EVALUADO: {
    etiqueta: 'Evaluado',
    clase: 'text-bg-success',
    icono: 'bi-check2-circle',
  },
};

const ESTADOS_SOLICITUD: Record<string, EstadoVisual> = {
  PENDIENTE: {
    etiqueta: 'Pendiente',
    clase: 'text-bg-warning',
    icono: 'bi-hourglass-split',
  },
  COMPLETADA: {
    etiqueta: 'Completada',
    clase: 'text-bg-success',
    icono: 'bi-check2-circle',
  },
  CANCELADA: {
    etiqueta: 'Cancelada',
    clase: 'text-bg-danger',
    icono: 'bi-x-circle',
  },
};

const ROLES: Record<string, EstadoVisual> = {
  CIUDADANO: {
    etiqueta: 'Ciudadano',
    clase: 'text-bg-primary',
    icono: 'bi-person',
  },
  ENCARGADO: {
    etiqueta: 'Encargado',
    clase: 'text-bg-info',
    icono: 'bi-person-badge',
  },
  ADMIN: {
    etiqueta: 'Administrador',
    clase: 'text-bg-dark',
    icono: 'bi-shield-check',
  },
};

const DESCONOCIDO: EstadoVisual = {
  etiqueta: 'Sin estado',
  clase: 'text-bg-light border',
  icono: 'bi-question-circle',
};

function buscar(mapa: Record<string, EstadoVisual>, estado: string | null) {
  return estado ? (mapa[estado] ?? { ...DESCONOCIDO, etiqueta: estado }) : DESCONOCIDO;
}

export function estadoRaee(estado: string | null): EstadoVisual {
  return buscar(ESTADOS_RAEE, estado);
}

export function estadoSolicitud(estado: string | null): EstadoVisual {
  return buscar(ESTADOS_SOLICITUD, estado);
}

export function estadoRol(rol: string | null): EstadoVisual {
  return buscar(ROLES, rol);
}
